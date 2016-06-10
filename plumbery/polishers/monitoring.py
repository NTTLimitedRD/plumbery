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

from libcloud.compute.types import NodeState

from plumbery.polishers.base import NodeConfiguration
from plumbery.exception import ConfigurationError
from plumbery.plogging import plogging


class MonitoringConfiguration(NodeConfiguration):
    __name__ = 'MonitoringConfiguration'
    _element_name_ = 'monitoring'
    _configuration_ = {
    }

    def __init__(self, engine, facility):
        self.engine = engine
        self.facility = facility

    def validate(self, settings):
        if self._element_name_ in settings:
            value = settings[self._element_name_].upper()
            if value not in ['ESSENTIALS', 'ADVANCED']:
                raise ConfigurationError(
                    "- monitoring should be "
                    "either 'essentials' or 'advanced'")
        return True

    def configure(self, node, settings):
        if self._element_name_ in settings:
            self._start_monitoring(node, settings[self._element_name_].upper())
            return True
        return False

    def deconfigure(self, node, settings):
        if self._element_name_ in settings:
            self._stop_monitoring(node, settings)
            return True
        return False

    def _start_monitoring(self, node, monitoring='ESSENTIALS'):
        """
        Enables monitoring of one node

        :param node: the target node
        :type node: :class:`libcloud.compute.base.Node`

        :param monitoring: either 'ESSENTIALS' or 'ADVANCED'
        :type monitoring: ``str``

        """

        value = monitoring.upper()
        plogging.info("Starting {} monitoring of node '{}'".format(
            value.lower(), node.name))

        while True:
            try:
                self.facility.region.ex_enable_monitoring(node, service_plan=value)
                plogging.info("- in progress")
                return True

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
                    plogging.info("- unable to start monitoring "
                                 "- node has been locked")

                else:
                    plogging.info("- unable to start monitoring")
                    plogging.error(str(feedback))

            break

        return False

    def _stop_monitoring(self, node, settings):
        """
        Disables monitoring of one node

        :param node: the target node
        :type node: :class:`libcloud.compute.base.Node`

        """

        if node is None:
            return

        if ('running' in settings
                and settings['running'] == 'always'
                and node.state == NodeState.RUNNING):

            return

        if self.engine.safeMode:
            return

        plogging.info("Stopping monitoring of node '{}'".format(node.name))

        while True:

            try:
                self.facility.region.ex_disable_monitoring(node)
                plogging.info("- in progress")

            except Exception as feedback:

                if 'NO_CHANGE' in str(feedback):
                    pass

                elif 'OPERATION_NOT_SUPPORTED' in str(feedback):
                    pass

                elif 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                elif 'RESOURCE_NOT_FOUND' in str(feedback):
                    plogging.info("- not found")

                elif 'RESOURCE_LOCKED' in str(feedback):
                    plogging.info("- not now - locked")

                else:
                    plogging.info("- unable to stop monitoring")
                    plogging.error(str(feedback))

            break
