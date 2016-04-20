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
Instance - Integration Tests
"""

# Imports #####################################################################

import os
import time

import requests
from django.conf import settings

from instance.models.instance import SingleVMOpenEdXInstance
from instance.models.server import Status, Progress
from instance.tests.decorators import patch_git_checkout
from instance.tests.integration.base import IntegrationTestCase
from instance.tests.integration.factories.instance import SingleVMOpenEdXInstanceFactory
from instance.tasks import provision_instance
from opencraft.tests.utils import shard


# Tests #######################################################################

class InstanceIntegrationTestCase(IntegrationTestCase):
    """
    Integration test cases for instance high-level tasks
    """
    def assert_instance_up(self, instance):
        """
        Check that the given instance is up and accepting requests
        """
        self.assertEqual(instance.status, Status.Ready)
        self.assertEqual(instance.progress, Progress.Success)
        server = instance.server_set.first()
        attempts = 3
        while True:
            attempts -= 1
            try:
                requests.get('http://{0}'.format(server.public_ip)).raise_for_status()
                break
            except Exception:  # pylint: disable=broad-except
                if not attempts:
                    raise
            time.sleep(15)

    @shard(1)
    def test_provision_instance(self):
        """
        Provision an instance
        """
        SingleVMOpenEdXInstanceFactory(name='Integration - test_provision_instance')
        instance = SingleVMOpenEdXInstance.objects.get()
        provision_instance(instance.pk)
        self.assert_instance_up(instance)

    @shard(2)
    def test_external_databases(self):
        """
        Ensure that the instance can connect to external databases
        """
        if not settings.INSTANCE_MYSQL_URL or not settings.INSTANCE_MONGO_URL:
            print('External databases not configured, skipping integration test')
            return
        SingleVMOpenEdXInstanceFactory(name='Integration - test_external_databases',
                                       use_ephemeral_databases=False)
        instance = SingleVMOpenEdXInstance.objects.get()
        provision_instance(instance.pk)
        self.assert_instance_up(instance)

    @patch_git_checkout
    def test_ansible_failure(self, git_checkout, git_working_dir):
        """
        Ensure failures in the ansible flow are reflected in the instance
        """
        git_working_dir.return_value = os.path.join(os.path.dirname(__file__), "ansible")

        SingleVMOpenEdXInstanceFactory(name='Integration - test_ansible_failure',
                                       ansible_playbook_name='failure')
        instance = SingleVMOpenEdXInstance.objects.get()
        provision_instance(instance.pk)
        self.assertEqual(instance.status, Status.Provisioning)
        self.assertEqual(instance.progress, Progress.Failed)

    @patch_git_checkout
    def test_ansible_failignore(self, git_checkout, git_working_dir):
        """
        Ensure failures that are ignored doesn't reflect in the instance
        """
        git_working_dir.return_value = os.path.join(os.path.dirname(__file__), "ansible")

        SingleVMOpenEdXInstanceFactory(name='Integration - test_ansible_failignore',
                                       ansible_playbook_name='failignore')
        instance = SingleVMOpenEdXInstance.objects.get()
        provision_instance(instance.pk)
        self.assertEqual(instance.status, Status.Ready)
        self.assertEqual(instance.progress, Progress.Success)
