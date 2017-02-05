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


class DomainFitting(PlumberyFitting):
    """
    Represents a network domain


    """

    def parse(self, settings):
        """
        Parses and checks settings

        :param settings: specific settings for this fittings
        :type settings: ``dict``

        This function raises a `ValueError` if invalid settings are provided.

        Following directives are handled by this class:
        - name - name of the network domain - mandatory
        - ipv4 - number of public addresses to assign, or 'auto'
        - description
        - service - 'essentials' or 'advanced'

        Example:

          domain:
            name: "virtual_data_centre_1"
            ipv4: auto


        """

        if not isinstance(settings, dict):
            raise TypeError('Settings should be a dictionary')

        expected = ('description', 'ipv4', 'name', 'service')
        for key in settings.keys():
            if key not in expected:
                raise KeyError('Unkown key %s: in settings' % key)

        mandatory = ('name',)
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

        # ipv4

        if 'ipv4' not in settings:
            settings['ipv4'] = None

        elif isinstance(settings['ipv4'], str):
            if settings['ipv4'] != 'auto':
                raise ValueError('Invalid directive ipv4: in settings')

        elif type(settings['ipv4']) is int:
            if settings['ipv4'] < 2 or settings['ipv4'] > 256:
                raise ValueError('Invalid directive ipv4: in settings')

        else:
            raise TypeError('Invalid directive ipv4: in settings')

        self.ipv4 = settings['ipv4']

        # name

        if not isinstance(settings['name'], str):
            raise TypeError('Invalid directive name: in settings')

        if len(settings['name']) < 1:
            raise ValueError('Invalid directive name: in settings')

        self.name = settings['name']

        # service

        if 'service' not in settings:
            settings['service'] = 'ESSENTIALS'

        elif not isinstance(settings['service'], str):
            raise TypeError('Invalid directive service: in settings')

        elif settings['service'].upper() not in ('ESSENTIALS', 'ADVANCED'):
            raise ValueError('Invalid directive service: in settings')

        self.service = settings['service'].upper()
