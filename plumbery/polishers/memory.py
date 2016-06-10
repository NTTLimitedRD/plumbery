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

from plumbery.plogging import plogging


class MemoryConfiguration(NodeConfiguration):
    __name__ = 'MemoryConfiguration'
    _element_name_ = 'memory'
    _configuration_ = {
    }

    def validate(self, settings):
        if self._element_name_ in settings:
            memory = int(settings[self._element_name_])
            if memory < 1 or memory > 256:
                raise ConfigurationError("- memory should be between 1 and 256")

    def configure(self, node, settings):
        if self._element_name_ in settings:
            memory = int(settings[self._element_name_])
            plogging.debug("- setting {} GB of memory".format(
                    memory))
            return memory
        return False
