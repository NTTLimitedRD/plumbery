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

from plumbery.plogging import plogging

__all__ = ['PlumberyPolisher']


class PlumberyPolisher(object):
    """
    Polishes elements of the fittings plan

    :param settings: specific settings for this polisher
    :type param: ``dict``

    Even embedded fittings deserve some good treatment, and this what
    polishing is about. You know the usual sequence:

    * at some point, decide that all appliances have to be visited
    * find every appliance and prepare it
    * after the hard work, go back home for some rest

    This is exactly what plumbery is offering to you in a straightforward
    extensible mechanism.

        You can create polishers of your own, or use polishers from other
        persons. All polishers have to be placed in the directory
        ``plumbery.polishers``. Each polisher should be put in a separate
        python file, and define a class that repeats the file name. For example
        the file::

            plumbery\\polishers\\configure.py

        should contain::

            class ConfigurePolisher(PlumberyPolisher):
            ...

        Once this is done properly, you can use the polisher by mentioning it
        if the fittings plan used by plumbery. Also, you can pass any
        parameters that the polisher would require.

        Example of configuration of ``fittings.yaml``::

            ---
            safeMode: False
            polishers:
              - configure:
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

    def __init__(self, settings):
        self.settings = settings

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

        :return: a list of filtered polishers
        :rtype: ``list`` of :class:`plumbery.PlumberyPolisher` or ``[]``

        """
        if filter is None:
            for polisher in polishers:
                plogging.info("Using polisher '{}'".format(
                    polisher.settings['name']))
            return polishers

        for polisher in polishers:
            if polisher.settings['name'] == filter:
                plogging.info("Using polisher '{}'".format(filter))
                filtered = [polisher]
                return filtered

        # generate an exception if no implementation is available
        polisher = PlumberyPolisher.from_shelf(filter)

        plogging.info("Using polisher '{}'".format(filter))
        return [polisher]

    @classmethod
    def from_shelf(cls, polishId, settings={}):
        """
        Picks up a polisher from the shelf

        :param polishId: name of the polisher to use, e.g., ``inventory``
        :type polishId: ``str``

        :param settings: specific settings for this polisher
        :type param: ``dict``

        :return: instance of a polisher ready to use
        :rtype: :class:`plumbery.PlumberyPolisher`

        """

        moduleName = 'plumbery.polishers.' + polishId
        polisherName = polishId.capitalize() + 'Polisher'
        try:

            plogging.debug("Importing '{}'".format(moduleName))
            polisherModule = __import__(
                moduleName,
                globals(),
                locals(),
                [polisherName])

            plogging.debug("Instantiating '{}'".format(polisherName))
            polisherClass = getattr(polisherModule, polisherName)
            if settings is None:
                settings = {}
            settings['name'] = polishId
            return polisherClass(settings)

        except ImportError as feedback:
            plogging.debug("Unable to find module '{}'".format(moduleName))
            raise feedback

        except Exception as feedback:
            plogging.debug("Unable to import '{}' from '{}'".format(
                polisherName, moduleName))
            raise feedback

    def go(self, engine):
        """
        Puts the shoes on, and go polishing

        :param engine: the plumbery engine itself
        :type engine: :class:`plumbery.PlumberyEngine`

        This function is called once, before starting the process of
        polishing each node. You can override it for any specific
        initialisation that you would require.

        """

        self.engine = engine

    def move_to(self, facility):
        """
        Enters a facility to polish nodes there

        :param facility: a target facility
        :type facility: :class:`plumbery.PlumberyFacility`

        This function is called once for each facility that is visited during
        the polishing process. You can override it for any specific
        initialisation that you would require.

        """

        self.facility = facility

    def shine_container(self, container):
        """
        prepares a container until it shines

        :param container: the container to be polished
        :type container: :class:`plumbery.PlumberyInfrastructure`

        This is where the hard work is done. You have to override this
        function in your own polisher. Note that you can compare the reality
        versus the theoritical settings if you want.

        """

        pass

    def shine_node(self, node, settings, container):
        """
        prepares a node until it shines

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        :param container: the container of this node
        :type container: :class:`plumbery.PlumberyInfrastructure`

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
