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
from plumbery.polishers.base import NodeConfiguration
from plumbery.exception import ConfigurationError
from libcloud.common.dimensiondata import DimensionDataServerCpuSpecification

from plumbery.plogging import plogging


class CpuConfiguration(NodeConfiguration):
    __name__ = 'CpuConfiguration'
    _element_name_ = 'cpu'
    _configuration_ = {
    }

    def validate(self, settings):
        if self._element_name_ in settings:
            tokens = str(settings[self._element_name_]).split(' ')
            if len(tokens) < 2:
                tokens.append('1')
            if len(tokens) < 3:
                tokens.append('standard')

            if int(tokens[0]) < 1 or int(tokens[0]) > 32:
                raise ConfigurationError('CPU should be within 1 and 32')

            elif int(tokens[1]) < 1 or int(tokens[1]) > 2:
                raise ConfigurationError("Core per cpu should be either 1 or 2")

            elif tokens[2].upper() not in ('STANDARD',
                                           'HIGHPERFORMANCE'):
                raise ConfigurationError(
                    "- cpu speed should be either 'standard'"
                    " or 'highspeed'")
            return True

    def configure(self, node, settings):
        if self._element_name_ in settings:
            tokens = str(settings[self._element_name_]).split(' ')
            if len(tokens) < 2:
                tokens.append('1')
            if len(tokens) < 3:
                tokens.append('standard')
            plogging.debug("- setting compute {}".format(' '.join(tokens)))
            cpu = DimensionDataServerCpuSpecification(
                cpu_count=tokens[0],
                cores_per_socket=tokens[1],
                performance=tokens[2].upper())
            return cpu
        return False
