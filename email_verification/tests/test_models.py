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
Email verification model tests
"""

# Imports #####################################################################

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from email_verification.models import EmailVerification


# Tests #######################################################################

class EmailVerificationTestCase(TestCase):
    """
    Tests for the EmailVerification model.
    """
    def setUp(self):
        self.verification = EmailVerification.verify(
            email='purplerain@example.com',
            base_url='http://example.com/',
        )

    def test_verify_new(self):
        """
        Test that verifying a new email address sends a verification email.
        """
        self.assertEqual(self.verification.verified, False)

        self.assertEqual(self.verification.verification_email_sent, True)
        self.assertAlmostEqual(self.verification.verification_email_date,
                               datetime.now(timezone.utc),
                               delta=timedelta(seconds=5))
        self.assertTrue(self.verification.verification_code)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertEqual(email.subject,
                         EmailVerification.verification_email_subject)
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(email.recipients(), [self.verification.email])

        verification_url = 'http://example.com'
        verification_url += reverse('email-verification:verify', kwargs={
            'code': self.verification.verification_code
        })
        self.assertIn(verification_url, email.body)

    def test_verify_existing(self):
        """
        Test that the verification email is only sent once.
        """
        verification = EmailVerification.verify(self.verification.email,
                                                base_url='http://example.com/')
        self.assertEqual(verification, self.verification)
        self.assertEqual(len(mail.outbox), 1)

    def test_verify_resend(self):
        """
        Check that we can force-send the verification email.
        """
        original_code = self.verification.verification_code
        verification = EmailVerification.verify(self.verification.email,
                                                base_url='http://example.com/',
                                                force_send_email=True)
        self.assertEqual(len(mail.outbox), 2)
        self.assertNotEqual(verification.verification_code, original_code)

        email = mail.outbox[-1]
        self.assertIn(verification.verification_code, email.body)

    def test_check_verification_code(self):
        """
        Test that we can check a verification code.
        """
        code = self.verification.verification_code
        verification = EmailVerification.check_verification_code(code)
        self.assertEqual(verification, self.verification)
        self.assertEqual(verification.verified, True)
        self.assertAlmostEqual(verification.verification_date,
                               datetime.now(timezone.utc),
                               delta=timedelta(seconds=5))

    @patch.object(EmailVerification, 'verification_code_expiry', timedelta(0))
    def test_check_verification_code_expired(self):
        """
        Check that an expired verification code will not verify an email
        address.
        """
        code = self.verification.verification_code
        verification = EmailVerification.check_verification_code(code)
        self.assertEqual(verification, self.verification)
        self.assertEqual(verification.verified, False)
