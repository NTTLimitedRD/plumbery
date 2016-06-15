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

from plumbery.fitting import PlumberyFitting
from plumbery.plogging import plogging


class DummyFitting(PlumberyFitting):
    """
    Dummy fittings used for tests

    :param settings: specific settings for this fittings
    :type settings: ``dict``

    :param blueprint: the blueprint in which this fittings has been defined
    :type blueprint: :class:`PlumberyBlueprint`

    Look at another file in this directory if you are looking for something
    to derive for your own needs.
    """

    def parse(self, settings):
        """
        Parses and checks settings

        :param settings: specific settings for this fittings
        :type settings: ``dict``

        This function raises a `ValueError` if invalid settings are provided.
        """

        if not isinstance(settings, dict):
            raise TypeError('test: should be a dictionary')

        if 'dummy' not in settings:
            raise ValueError('Missing key dummy: in test:')

        if not isinstance(settings['dummy'], str):
            raise TypeError('Invalid parameter dummy: in test:')

        if len(settings['dummy']) < 1:
            raise ValueError('Invalid parameter dummy: in test:')

        print('false')
        self.completed = False

    def do_some_action(self, parameters={}):
        """
        Does something

        :param parameters: specific parameters for this action
        :type parameters: ``dict``

        :return: True if success, False otherwise
        :rtype: ``boolean``

        """

        print('true')
        self.completed = True
        return True
