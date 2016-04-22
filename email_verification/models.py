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
Models for email verification
"""

# Imports #####################################################################

from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.crypto import get_random_string


# Models ######################################################################

class EmailVerification(models.Model):
    """
    Verification status for an email address. The main entry point is the
    `verify` classmethod.
    """
    VERIFICATION_CODE_LENGTH = 64

    verification_code_expiry = timedelta(days=7)
    verification_email_subject = 'Please verify this email address'

    email = models.EmailField(primary_key=True)
    verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=VERIFICATION_CODE_LENGTH,
                                         db_index=True)
    verification_email_date = models.DateTimeField(null=True)
    verification_date = models.DateTimeField(null=True)

    @classmethod
    def verify(cls, email, base_url, force_send_email=False):
        """
        Verify the given email address. Returns a corresponding
        `EmailVerification` instance.

        `base_url` should be the domain prefix to include in the verification
        link, e.g. 'http://example.com/'.

        If an email has already been sent to verify the given address, a new
        email will not be sent unless `force_send_email` is True.
        """
        try:
            instance = cls.objects.get(email=email)
        except cls.DoesNotExist:
            instance = cls(email=email)
        if force_send_email or not instance.verification_email_sent:
            instance.send_verification_email(base_url)
        return instance

    @classmethod
    def check_verification_code(cls, code):
        """
        Check that the given verification code is valid, and mark the email
        address as verified if it is. Returns the corresponding
        `EmailVerification` instance.
        """
        instance = cls.objects.get(verification_code=code)
        if not instance.verified and not instance.verification_code_expired:
            instance.verification_date = datetime.now(timezone.utc)
            instance.verified = True
            instance.save()
        return instance

    def __str__(self):
        return '{email} ({status})'.format(
            email=self.email,
            status='verified' if self.verified else 'unverified',
        )

    def reset(self):
        """
        Reset this email address to an unverified state and generate a new
        verification code.
        """
        self.verified = False
        self.verification_code = get_random_string(self.VERIFICATION_CODE_LENGTH)

    def send_verification_email(self, base_url):
        """
        Send an email to verify that the email address exists.
        """
        self.reset()
        send_mail(
            subject=self.verification_email_subject,
            message=self.get_verification_email_message(base_url),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=(self.email,),
        )
        self.verification_email_date = datetime.now(timezone.utc)
        self.save()

    @property
    def verification_email_sent(self):
        """
        Return True if a verification email has been sent, False otherwise.
        """
        return bool(self.verification_email_date)

    @property
    def verification_code_expired(self):
        """
        Return True if the verification code has expired, False otherwise.
        """
        return (self.verification_email_sent and
                datetime.now(timezone.utc) > (self.verification_email_date +
                                              self.verification_code_expiry))

    def get_verification_url(self, base_url):
        """
        An absolute url to include in the verification email.
        """
        assert self.verification_code
        return urljoin(base_url, reverse('email-verification:verify', kwargs={
            'code': self.verification_code,
        }))

    def get_verification_email_message(self, base_url):
        """
        The plain text body of the verification email.
        """
        return 'Verify your email address: {0}'.format(self.get_verification_url(base_url))
