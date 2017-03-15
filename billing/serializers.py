# -*- coding: utf-8 -*-
#
# OpenCraft -- tools to aid developing and hosting free software projects
# Copyright (C) 2015-2016 OpenCraft <contact@opencraft.com>
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
Billing serializers (API representation)
"""

# Imports #####################################################################

from django.conf import settings
from rest_framework import serializers

from billing.models import BillingCustomer


# Serializers #################################################################

class BillingCustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for BillingCustomer
    """
    class Meta:
        model = BillingCustomer
        fields = (
            'id',
            'stripe_customer_id',
        )

    def to_representation(self, obj):
        """
        Add additional fields/data to the output
        """
        output = super().to_representation(obj)
        output['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return output
