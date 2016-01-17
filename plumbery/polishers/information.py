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

from libcloud.compute.base import NodeState

from plumbery.polisher import PlumberyPolisher
from plumbery.text import PlumberyText
from plumbery.text import PlumberyNodeContext


class InformationPolisher(PlumberyPolisher):
    """
    Shows information attached to nodes

    """

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

        information = []
        if ('information' in settings
                and isinstance(settings['information'], list)
                and len(settings['information']) > 0):

            for line in settings['information']:

                tokens = line.split(' ')
                if tokens[0] == 'echo':
                    tokens.pop(0)
                message = ' '.join(tokens)
                message = PlumberyText.expand_variables(
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

        if node is None:
            return

        logging.info("About '{}':".format(settings['name']))

        lines = []
        if node.state == NodeState.RUNNING:
            lines.append("node is up and running")

        lines += self.list_information(node, settings, container)
        if len(lines) < 1:
            logging.info("- no information to report")
            return

        for line in lines:
            logging.info("- {}".format(line))
