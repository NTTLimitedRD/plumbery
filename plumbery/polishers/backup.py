# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import time
from six import string_types
from plumbery.polishers.base import NodeConfiguration
from plumbery.exception import ConfigurationError
from plumbery.plogging import plogging


class BackupConfiguration(NodeConfiguration):
    __name__ = 'BackupConfiguration'
    _element_name_ = 'backup'
    _configuration_ = {
    }

    def __init__(self, engine, facility):
        self.engine = engine
        self.facility = facility

    def validate(self, settings):
        if self._element_name_ in settings:
            backup = settings[self._element_name_]
            if isinstance(backup, dict):
                plan = backup['plan'].lower().capitalize()
            else:
                plan = backup.lower().capitalize()
            if plan not in ['Essentials', 'Advanced', 'Enterprise']:
                raise ConfigurationError("Backup plan not valid")
            return True

    def configure(self, node, settings):
        if self._element_name_ in settings:
            self._configure_backup(node, settings[self._element_name_])
            return True
        return False

    def deconfigure(self, node, settings):
        return True

    def _configure_backup(self, node, backup):
        """
        Configure backup on a node

        :param node: the target node
        :type node: :class:`libcloud.compute.base.Node`

        :param backup: The backup settings
        :type  backup: ``dict`` or ``str``

        """
        default_email = self.facility.backup.connection.get_account_details().email
        if isinstance(backup, string_types):
            backup = {
                'plan': backup,
                'email': default_email,
                'clients': [{
                    'type': 'filesystem'
                }]
            }

        plan = backup['plan'].lower().capitalize()
        plogging.info("Starting {} backup of node '{}'".format(
            plan.lower(), node.name))

        backup_details = None
        try:
            self.facility.backup.create_target_from_node(
                node,
                extra={'servicePlan': plan})
        except Exception as feedback:
            if feedback.msg == 'Cloud backup for this server is already enabled or being enabled (state: NORMAL).':
                plogging.info("- already there")
                backup_details = self.facility.backup.ex_get_backup_details_for_target(node.id)
            else:
                plogging.info("- unable to start backup")
                plogging.error(str(feedback))
                return False

        while (backup_details is not None and
               backup_details.status is not 'NORMAL'):
            try:
                backup_details = self.facility.backup.ex_get_backup_details_for_target(node.id)
                plogging.info("- in progress, found asset %s", backup_details.asset_id)

            except Exception as feedback:
                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                elif 'RETRYABLE_SYSTEM_ERROR' in str(feedback):
                    time.sleep(10)
                    continue

                elif 'NO_CHANGE' in str(feedback):
                    plogging.info("- already there")

                elif 'RESOURCE_LOCKED' in str(feedback):
                    plogging.info("- unable to start backup "
                                 "- node has been locked")

                else:
                    plogging.info("- unable to start backup")
                    plogging.error(str(feedback))

            break
        target = self.facility.backup.ex_get_target_by_id(node.id)
        storage_policies = self.facility.backup.ex_list_available_storage_policies(
            target=target
        )
        schedule_policies = self.facility.backup.ex_list_available_schedule_policies(
            target=target
        )
        client_types = self.facility.backup.ex_list_available_client_types(
            target=target
        )
        clients = backup.get('clients', [{'type': 'filesystem'}])
        for client in clients:
            plogging.info("- adding backup client")

            client_type = client.get('type', 'filesystem').lower()
            storage_policy = client.get(
                'storagePolicy', '14 Day Storage Policy').lower()
            schedule_policy = client.get(
                'schedulePolicy', '12AM - 6AM').lower()
            trigger = client.get('trigger', 'ON_FAILURE')
            email = client.get('email', default_email)

            try:
                storage_policy = [x for x in storage_policies
                                  if x.name.lower() == storage_policy][0]
            except IndexError:
                raise ConfigurationError(
                    "Could not find matching storage policy '%s'" %
                    storage_policy)
            try:
                schedule_policy = [x for x in schedule_policies
                                   if x.name.lower() == schedule_policy][0]
            except IndexError:
                raise ConfigurationError(
                    "Could not find matching schedule policy '%s'" %
                    schedule_policy)

            if client_type in ['file', 'filesystem']:
                client = [x for x in client_types if x.is_file_system][0]
            else:
                client = [x for x in client_types
                          if x.description.startswith(client_type)][0]
            self.facility.backup.ex_add_client_to_target(
                target=target,
                client_type=client,
                storage_policy=storage_policy,
                schedule_policy=schedule_policy,
                trigger=trigger,
                email=email
            )
        return True