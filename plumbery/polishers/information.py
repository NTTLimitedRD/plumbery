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
import sys

from libcloud.compute.base import NodeState

from plumbery.polisher import PlumberyPolisher
from plumbery.text import PlumberyText
from plumbery.text import PlumberyContext
from plumbery.text import PlumberyNodeContext
from plumbery.plogging import plogging


class InformationPolisher(PlumberyPolisher):
    """
    Shows information attached to fittings plan, to containers, to nodes

    """

    def go(self, engine):
        """
        Lists information registered at the highest level of fittings plan

        :param engine: the plumbery engine itself
        :type engine: :class:`plumbery.PlumberyEngine`

        """

        self.engine = engine

        self.information = []

        environment = PlumberyContext(context=self.engine)

        lines = []
        for line in engine.information:

            tokens = line.split(' ')
            if tokens[0] == 'echo':
                tokens.pop(0)
            message = ' '.join(tokens)
            message = PlumberyText.expand_string(
                message, environment)
            lines.append(message)

        for label in engine.links.keys():
            message = "{}: {}".format(label, engine.links[label])
            lines.append(message)

        if len(lines) < 1:
            return

        self.information.append("About this fittings plan:")

        for line in lines:
            self.information.append("- {}".format(line))

    def move_to(self, facility):
        """
        Lists information registered in one document of fittings plan

        :param facility: a target facility
        :type facility: :class:`plumbery.PlumberyFacility`

        This function is called once for each facility that is visited during
        the polishing process. You can override it for any specific
        initialisation that you would require.

        """

        self.facility = facility

        environment = PlumberyContext(context=self.facility)

        if ('information' in facility.settings and
                isinstance(facility.settings['information'], str)):

            facility.settings['information'] = \
                facility.settings['information'].strip('\n').split('\n')

        lines = []
        if ('information' in facility.settings and
                isinstance(facility.settings['information'], list) and
                len(facility.settings['information']) > 0):

            for line in facility.settings['information']:

                tokens = line.split(' ')
                if tokens[0] == 'echo':
                    tokens.pop(0)
                message = ' '.join(tokens)
                message = PlumberyText.expand_string(
                    message, environment)
                lines.append(message)

        if len(lines) < 1:
            return

        self.information.append("About '{}':".format(
            facility.get_location_id()))

        for line in lines:
            self.information.append("- {}".format(line))

    def shine_container(self, container):
        """
        Lists information registered at the container level

        :param container: the container to be polished
        :type container: :class:`plumbery.PlumberyInfrastructure`

        """

        environment = PlumberyNodeContext(node=None,
                                          container=container,
                                          context=self.facility)

        if ('information' in container.blueprint.keys() and
                isinstance(container.blueprint['information'], str)):

            container.blueprint['information'] = \
                container.blueprint['information'].strip('\n').split('\n')

        lines = []
        if ('information' in container.blueprint.keys() and
                isinstance(container.blueprint['information'], list) and
                len(container.blueprint['information']) > 0):

            for line in container.blueprint['information']:

                tokens = line.split(' ')
                if tokens[0] == 'echo':
                    tokens.pop(0)
                message = ' '.join(tokens)
                message = PlumberyText.expand_string(
                    message, environment)
                lines.append(message)

        if len(lines) < 1:
            return

        self.information.append("About '{}':".format(
            container.blueprint['target']))

        for line in lines:
            self.information.append("- {}".format(line))

    def list_information(self, node, settings, container):
        """
        Lists information for a node if it exists

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        :param container: the container of this node
        :type container: :class:`plumbery.PlumberyInfrastructure`

        """

        environment = PlumberyNodeContext(node=node,
                                          container=container,
                                          context=self.facility)

        if ('information' in settings and
                isinstance(settings['information'], str)):

            settings['information'] = \
                settings['information'].strip('\n').split('\n')

        information = []
        if ('information' in settings
                and isinstance(settings['information'], list)
                and len(settings['information']) > 0):

            for line in settings['information']:

                tokens = line.split(' ')
                if tokens[0] == 'echo':
                    tokens.pop(0)
                message = ' '.join(tokens)
                message = PlumberyText.expand_string(
                    message, environment)
                information.append(message)

        return information

    def shine_node(self, node, settings, container):
        """
        Shows information attached to node, if any

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        :param container: the container of this node
        :type container: :class:`plumbery.PlumberyInfrastructure`

        """

        plogging.info("- examinating node '{}'".format(settings['name']))

        lines = []

        if (node is not None and 'description' in node.extra):
            description = node.extra['description'].replace(
                '#plumbery', '').strip()
            if len(description) > 0:
                lines.append(description)

        if node is None:
            plogging.debug("- not found")
            lines.append("node is unknown")
        elif node.state == NodeState.RUNNING:
            lines.append("node is up and running")
        elif node.state in [NodeState.TERMINATED,
                            NodeState.STOPPED,
                            NodeState.SUSPENDED]:
            lines.append("node has been stopped")
        else:
            lines.append("state: {}".format(node.state))

        if node is not None:
            lines += self.list_information(
                node=node, settings=settings, container=container)

        if len(lines) < 1:
            return

        self.information.append("About '{}':".format(settings['name']))

        for line in lines:
            self.information.append("- {}".format(line))

    def reap(self):
        """
        Saves information gathered through the polishing sequence

        All information captured in dumped in a file, in YAML format,
        to provide a flexible and accurate inventory of all live nodes
        described in the fittings plan.

        """

        if len(self.information) < 1:
            return

        if 'reap' in self.settings:
            fileName = self.settings['reap']
            plogging.info("Writing information in '{}'".format(fileName))
            stream = open(fileName, 'w')
        else:
            plogging.info("Showing information")
            stream = sys.stdout

        stream.write('\n'.join(self.information)+'\n')
