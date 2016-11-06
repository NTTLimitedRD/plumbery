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


class EthernetFitting(PlumberyFitting):
    """
    Represents a VLAN


    """

    def parse(self, settings):
        """
        Parses and checks settings

        :param settings: specific settings for this fittings
        :type settings: ``dict``

        This function raises a `ValueError` if invalid settings are provided.

        Following directives are handled by this class:
        - name - name of the VLAN - mandatory
        - description
        - subnet - e.g., '10.2.3.0'

        Example:

          ethernet:
            name: myNetwork
            subnet: 10.2.3.0


        """

        if not isinstance(settings, dict):
            raise TypeError('Settings should be a dictionary')

        expected = ('description', 'name', 'subnet')
        for key in settings.keys():
            if key not in expected:
                raise KeyError('Unkown key %s: in settings' % key)

        mandatory = ('name', 'subnet')
        for key in mandatory:
            if key not in settings:
                raise KeyError('Missing key %s: in settings' % key)

        # description

        if 'description' not in settings:
            settings['description'] = ''

        elif not isinstance(settings['description'], str):
            raise TypeError('Invalid directive description: in settings')

        elif len(settings['description']) < 1:
            raise ValueError('Invalid directive description: in settings')

        self.description = (settings['description']+' #plumbery').strip()

        # name

        if not isinstance(settings['name'], str):
            raise TypeError('Invalid directive name: in settings')

        if len(settings['name']) < 1:
            raise ValueError('Invalid directive name: in settings')

        self.name = settings['name']

        # subnet

        if not isinstance(settings['subnet'], str):
            raise TypeError('Invalid directive subnet: in settings')

        elif len(settings['subnet'].split('.')) != 4:
            raise ValueError('Invalid directive subnet: in settings')

        self.subnet = settings['subnet']

