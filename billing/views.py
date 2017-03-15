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
Billing views
"""

# Imports #####################################################################

from billing.models import BillingCustomer


# Views #######################################################################

class BillingCustomerMixin:
    """
    Mix this in to generic views to provide a BillingCustomer object for the
    logged in user.
    """
    def get_object(self, *args, **kwargs):
        """
        Get the BillingCustomer object for the logged in user, if any.
        """
        if self.request.user.is_authenticated:
            if hasattr(self.request.user, 'billing_customer'):
                return self.request.user.billing_customer
            billing_customer = BillingCustomer()
            billing_customer.user = self.request.user
            return billing_customer
        return None