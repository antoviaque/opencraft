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
Billing API views
"""

# Imports #####################################################################

import json
import logging

from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
import stripe

from billing.serializers import BillingCustomerSerializer
from billing.views import BillingCustomerMixin


# Logging #####################################################################

logger = logging.getLogger(__name__)


# Views #######################################################################

class BillingCustomerViewSet(BillingCustomerMixin, ViewSet):
    """
    ViewSet for ajax validation of the beta test registration form.
    """
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        Returns a list with the BillingCustomer object for the current user
        """
        serializer = BillingCustomerSerializer(self.get_object())
        return Response([serializer.data])

    def create(self, request):
        """
        Register a Stripe token for the current user
        """
        logger.info('Received a request to register a Stripe token')
        stripe_token = request.data.get('stripe_token')
        if not stripe_token:
            logger.error('Request to register a Stripe token, but without a `stripe_token` parameter')
            return Response('Missing required parameter `stripe_token`', status=400)
        else:
            logger.info('Stripe token received: %s', stripe_token)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        billing_customer = self.get_object()

        try:
            # Create
            if not billing_customer.stripe_customer_id:
                logger.info('No existing customer registered in Stripe, creating.')
                stripe_customer = stripe.Customer.create(
                    email=request.user.email,
                    description='{} ({})'.format(request.user.profile.full_name, request.user.username),
                    source=stripe_token,
                )
                billing_customer.stripe_customer_id = stripe_customer.id
                logger.info('Stripe customer registered with id = "%s", Stripe returned: %s',
                            billing_customer.stripe_customer_id,
                            stripe_customer)
                billing_customer.save()
            # Update
            else:
                logger.info('Existing customer already registered in Stripe ("%s"), updating.',
                            billing_customer.stripe_customer_id)
                stripe_customer = stripe.Customer.retrieve(billing_customer.stripe_customer_id)
                stripe_customer.source = stripe_token
                stripe_customer.save()
                logger.info('Stripe customer with id = "%s" updated with new token, Stripe returned: %s',
                            billing_customer.stripe_customer_id,
                            stripe_customer)
        except stripe.error.StripeError as e:
            logger.error('Error from Stripe while registering token')
            logger.exception(e)
            return Response('Error recording credit card', status=400)

        serializer = BillingCustomerSerializer(billing_customer)
        return Response(serializer.data)
