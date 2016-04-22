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
Models for the Instance Manager beta test
"""

# Imports #####################################################################

from django.contrib.auth.models import User
from django.db import models


# Models ######################################################################

class BetaTestApplication(models.Model):
    """
    An application to beta test the Instance Manager.
    """
    BASE_DOMAIN = 'opencraft.hosting'

    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    )

    user = models.OneToOneField(User)
    subdomain = models.CharField(
        max_length=255,
        verbose_name='domain name',
        help_text=('The URL students will visit. In the future, you will also '
                   'have the possibility to use your own domain name.'
                   '\n\nExample: hogwarts.{0}').format(BASE_DOMAIN),
        unique=True,
    )
    instance_name = models.CharField(
        max_length=255,
        help_text=('The name of your institution, company or project.'
                   '\n\nExample: Hogwarts Online Learning'),
    )
    public_contact_email = models.EmailField(
        help_text=('The email your instance of Open edX will be using to '
                   'send emails, and where your users should send their '
                   'support requests.'
                   '\n\nThis needs to be a valid email.'),
    )
    project_description = models.TextField(
        verbose_name='your project',
        help_text=('What are you going to use the instance for? What are '
                   'your expectations?'),
    )
    subscribe_to_updates = models.BooleanField(
        default=False,
        help_text=('I want OpenCraft to keep me updated about the progress '
                   'of the beta test, and send me an email occasionally '
                   'about it.'),
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    def __str__(self):
        return self.domain

    @property
    def domain(self):
        """
        The full domain requested for this application.
        """
        return '{0}.{1}'.format(self.subdomain, self.BASE_DOMAIN)
