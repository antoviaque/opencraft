# -*- coding: utf-8 -*-
#
# OpenCraft -- tools to aid developing and hosting free software projects
# Copyright (C) 2015 OpenCraft <xavier@opencraft.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Tests for the betatest app
"""

# Imports #####################################################################

import re

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from betatest.models import BetaTestApplication
from email_verification.models import EmailVerification


# Tests #######################################################################

class BetaTestApplicationTestCase(TestCase):
    """
    Tests for beta test applications.
    """
    url = reverse('beta:register')

    def setUp(self):
        self.application = {
            'subdomain': 'hogwarts',
            'instance_name': 'Hogwarts',
            'full_name': 'Albus Dumbledore',
            'username': 'albus',
            'email': 'albus.dumbledore@hogwarts.edu',
            'public_contact_email': 'support@hogwarts.edu',
            'password': 'gryffindor',
            'password_confirmation': 'gryffindor',
            'project_description': 'Online courses in Witchcraft and Wizardry',
            'accept_terms': 'on',
        }

    def assert_registration_succeeds(self, application):
        """
        Assert that the given application form data creates new user, profile
        and registration instances, sends email verification messages, and
        displays a success message.
        """
        response = self.client.post(self.url, application, follow=True)
        self.assertContains(response, 'Thank you for registering')

        # An application, user and profile should have been created
        application = BetaTestApplication.objects.get()
        user = application.user
        profile = user.profile

        # Check the application fields
        for application_field in ('subdomain',
                                  'instance_name',
                                  'public_contact_email',
                                  'project_description'):
            self.assertEqual(getattr(application, application_field),
                             self.application[application_field])
        self.assertEqual(application.subscribe_to_updates,
                         bool(self.application.get('subscribe_to_updates')))

        # Check the user fields
        for user_field in ('username', 'email'):
            self.assertEqual(getattr(user, user_field),
                             self.application[user_field])
        self.assertTrue(user.check_password(self.application['password']))

        # Check the profile fields
        self.assertEqual(profile.full_name, self.application['full_name'])

        # Test email verification flow
        self.assertEqual(len(mail.outbox), 2)
        for verification_email in mail.outbox:
            verify_url = re.search(r'https?://testserver/[^\s]+',
                                   verification_email.body).group(0)
            self.client.get(verify_url)
        for email_address in (user.email, application.public_contact_email):
            verification = EmailVerification.objects.get(email=email_address)
            self.assertEqual(verification.verified, True)

    def assert_registration_fails(self, application):
        """
        Assert that the given application form data does not create new user,
        profile and registration instances, or send email verification
        messages, and that the form is redisplayed.
        """
        response = self.client.post(self.url, application, follow=True)
        self.assertEqual(response.resolver_match.url_name, 'register') #pylint: disable=no-member
        self.assertEqual(len(mail.outbox), 0)

    def test_valid_application(self):
        """
        Test a valid beta test application.
        """
        self.assert_registration_succeeds(self.application)

    def test_invalid_subdomain(self):
        """
        Invalid characters in the subdomain.
        """
        self.application['subdomain'] = 'hogwarts?'
        self.assert_registration_fails(self.application)

    def test_invalid_username(self):
        """
        Invalid characters in the username.
        """
        self.application['username'] = 'albus@dumbledore'
        self.assert_registration_fails(self.application)

    def test_invalid_email(self):
        """
        Invalid email address.
        """
        self.application['email'] = 'albus'
        self.assert_registration_fails(self.application)

    def test_invalid_public_contact_email(self):
        """
        Invalid public contact email address.
        """
        self.application['public_contact_email'] = 'hogwarts'
        self.assert_registration_fails(self.application)

    def test_weak_password(self):
        """
        Password not strong enough.
        """
        for password in ('password', 'qwerty', 'Hogwarts'):
            self.application['password'] = password
            self.application['password_confirmation'] = password
            self.assert_registration_fails(self.application)

    def test_password_mismatch(self):
        """
        Password confirmation does not match password.
        """
        self.application['password_confirmation'] = 'slytherin'
        self.assert_registration_fails(self.application)
