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

import logging

from exceptions import PlumberyException

__all__ = ['PlumberyPolisher']


class PlumberyPolisher:
    """
    Polishes all these nodes

    :param settings: specific settings for this polisher
    :type param: ``dict``

    Even embedded fittings deserve some good treatment, and this what
    polishing is about. You know the usual sequence:

    * at some point, decide that all appliances have to be visited
    * find every appliance and rub it
    * after the hard work, go back home for some rest

    This is exactly what plumbery is offering to you in a straightforward
    extensible mechanism.

    """

    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_shelf(cls, polishId, settings={}):
        """
        Picks up a polisher from the shelf

        :param polishId: name of the polisher to use, e.g., ``spit``
        :type polishId: ``str``

        :param settings: specific settings for this polisher
        :type param: ``dict``

        :returns: :class:`plumbery.PlumberyPolisher`
            - instance of a polisher ready to use

        :raises: :class:`plumbery.PlumberyException` if no polisher can be found

        You can create polishers of your own, or use polishers from other
        persons. All polishers have to be placed in the directory
        ``plumbery.polishers``. Each polisher should be put in a separate
        python file, and define a class that repeats the file name. For example
        the file::

            plumbery\\polishers\\spit.py

        should contain::

            class SpitPolisher(PlumberyPolisher):
            ...

        Once this is done properly, you can use the polisher by mentioning it
        if the fittings plan used by plumbery. Also, you can pass any parameters
        that the polisher would require.

        Example of configuration of ``fittings.yaml``::

            ---
            safeMode: False
            polishers:
              - spit:
                  file: nodes.yaml
              - ansible:
                  file: inventory.yaml
            ---
            # Frankfurt in Europe
            locationId: EU6
            regionId: dd-eu
            ...

        The engine provides multiple ways to polish nodes. For example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').polish_all_nodes()

        """

        try:
            settings['name'] = polishId

            moduleName = 'polishers.' + polishId
            polisherName = polishId.capitalize() + 'Polisher'

            polisherModule = __import__(moduleName,
                    globals(), locals(), [polisherName])
            polisherClass = getattr(polisherModule, polisherName)
            return polisherClass(settings)

        except Exception as feedback:
            raise PlumberyException(
                "Error: unable to load polisher '{0}' {1}!".format(
                    polishId, feedback))

    def go(self, engine):
        """
        Puts the shoes on, and go polishing

        This function is called once, before starting the process of
        polishing each node. You can override it for any specific
        initialisation that you would require.

        """

        self.engine = engine

    @classmethod
    def filter(cls, polishers, filter=None):
        """
        Selects only the polisher you want, or take them all

        :param polishers: polishers to be applied
        :type polishers: list of :class:`plumbery.PlumberyPolisher`

        :param filter: the name of a single polisher to apply. If this
            parameter is missing, all polishers declared in the fittings plan
            will be applied
        :type filter: ``str``

        :returns: list of :class:`plumbery.PlumberyPolisher`

        :raises: ``LookupError`` if no polisher can be found

        """

        if not filter:
            for polisher in polishers:
                logging.info("Using polisher '{}'".format(polisher.settings['name']))
            return polishers

        for polisher in polishers:
            if polisher.settings['name'] == filter:
                filtered = [polisher]
                logging.info("Using polisher '{}'".format(polisher.settings['name']))
                return filtered

        return [PlumberyPolisher.from_shelf(filter)]

    def move_to(self, facility):
        """
        Enters a facility to polish nodes there

        This function is called once for each facility that is visited during
        the polishing process. You can override it for any specific
        initialisation that you would require.

        """

        self.facility = facility

    def shine_domain(self, domain, settings):
        """
        Rubs a domain until it shines

        :param domain: the domain to be polished
        :type domain: `strp`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        This is where the hard work is done. You have to override this
        function in your own polisher. Note that you can compare the reality
        versus the theoritical settings if you want.

        """

        pass

    def shine_node(self, node, settings):
        """
        Rubs a node until it shines

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        This is where the hard work is done. You have to override this
        function in your own polisher. Note that you can compare the reality
        versus the theoritical settings if you want.

        """

        pass

    def reap(self):
        """
        Reaps the outcome of all this polishing

        This function is called once, after all nodes have been polished. You
        can override it for any specific closure that you would require.

        """

        pass
