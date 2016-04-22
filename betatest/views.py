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
Beta test views
"""

# Imports #####################################################################

from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.shortcuts import render
from django.views.generic.edit import CreateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from betatest.forms import BetaTestApplicationForm
from email_verification.models import EmailVerification


# Views #######################################################################

class BetaTestApplicationView(CreateView):
    """
    Display the beta test application form.
    """
    template_name = 'betatest/application.html'
    form_class = BetaTestApplicationForm
    success_url = reverse_lazy('beta:success')

    @transaction.atomic
    def form_valid(self, form):
        """
        If the form is valid, send verification emails for the user's email
        address and the given public contact email.
        """
        response = super().form_valid(form)
        base_url = self.request.build_absolute_uri('/')
        EmailVerification.verify(self.object.user.email, base_url)
        EmailVerification.verify(self.object.public_contact_email, base_url)
        return response


def success(request):
    """
    Display a message on successful registration.
    """
    return render(request, 'betatest/success.html')


@api_view(['POST'])
@permission_classes((AllowAny,))
def validate_registration(request):
    """
    Validate the given form input, and return any errors as json.
    """
    form = BetaTestApplicationForm(request.data)
    return Response(form.errors)
