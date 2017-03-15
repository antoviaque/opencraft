# -*- coding: utf-8 -*-
#
# OpenCraft -- tools to aid developing and hosting free software projects
# Copyright (C) 2015-2017 OpenCraft <contact@opencraft.com>
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
Models for the billing application
"""

# Imports #####################################################################

from django.conf import settings
from django.db import models
from django_extensions.db.models import TimeStampedModel

from instance.models.utils import ValidateModelMixin


# Models ######################################################################

class BillingCustomer(ValidateModelMixin, TimeStampedModel):
    """
    A billing representation of a user
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='billing_customer',
    )
    stripe_customer_id = models.CharField(
        max_length=50,
        help_text=('The id of the customer recorded in Stripe for this user.'),
    )