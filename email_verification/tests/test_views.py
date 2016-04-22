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
Email verification view tests
"""

# Imports #####################################################################

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase

from email_verification.models import EmailVerification


# Tests #######################################################################

class VerifyEmailTestCase(TestCase):
    """
    Tests for the verify_email view.
    """
    def setUp(self):
        self.verification = EmailVerification.verify(
            email='raspberryberet@example.com',
            base_url='http://example.com/',
        )
        self.verification_url = self.verification.get_verification_url(
            base_url='http://example.com/',
        )

    def test_verify_email(self):
        """
        Test that we can check a verification code.
        """
        response = self.client.get(self.verification_url)
        self.assertContains(response, 'Thank you for verifying your email address')
        self.verification.refresh_from_db()
        self.assertEqual(self.verification.verified, True)

    @patch.object(EmailVerification, 'verification_code_expiry', timedelta(0))
    def test_verify_email_code_expired(self):
        """
        Test attempting to verify an expired verification code.
        """
        response = self.client.get(self.verification_url)
        self.assertContains(response, 'Your email verification link has expired')
        self.verification.refresh_from_db()
        self.assertEqual(self.verification.verified, False)

    def test_verify_unknown_code(self):
        """
        Check that attempting to verify an unknown code returns 404.
        """
        url = self.verification_url[:len(self.verification_url) - 10] + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
