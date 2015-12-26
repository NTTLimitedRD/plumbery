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
import time

from plumbery.polisher import PlumberyPolisher
from plumbery.nodes import PlumberyNodes


class SpitPolisher(PlumberyPolisher):
    """
    Finalizes the setup of fittings

    This polisher looks at each node in sequence, and adjust settings
    according to fittings plan. This is covering various features that
    can not be set during the creation of nodes, such as:
    - number of CPU
    - quantity of RAM
    - monitoring

    """

    def go(self, engine):
        """
        Restarts the inventory process
        """

        self.engine = engine

    def move_to(self, facility):
        """
        Moves to another API endpoint

        :param facility: access to local parameters and functions
        :type facility: :class:`plumbery.PlumberyFacility`


        """

        self.facility = facility
        self.region = facility.region
        self.nodes = PlumberyNodes(facility)

    def shine_container(self, container):
        """
        Rubs a container until it shines

        :param container: the container to be polished
        :type container: :class:`plumbery.PlumberyInfrastructure`

        This is where the hard work is done. You have to override this
        function in your own polisher. Note that you can compare the reality
        versus the theoritical settings if you want.

        """

        if container.network is None:
            return

        nodes = PlumberyNodes(self.facility)

        names = nodes.list_nodes(container.blueprint)

        logging.info("Waiting for nodes to be deployed")
        for name in names:
            while True:
                node = nodes.get_node(name)
                if node is None:
                    logging.info("- aborted - missing node '{}'".format(name))
                    return

                if node.extra['status'].action is None:
                    break

                if node is not None \
                    and node.extra['status'].failure_reason is not None:

                    logging.info("- aborted - failed deployment of node '{}'".format(name))
                    return

                time.sleep(20)

        logging.info("- done")

        container._build_firewall_rules()

        container._reserve_ipv4()

        container._build_balancer()

    def shine_node(self, node, settings, container):
        """
        Finalizes setup of one node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        :param container: the container of this node
        :type container: :class:`plumbery.PlumberyInfrastructure`

        """

        cpu = None
        if 'cpu' in settings:
            cpu = int(settings['cpu'])
            if cpu < 1 or cpu > 32:
                logging.info("- cpu should be between 1 and 32")
                cpu = None

        memory = None
        if 'memory' in settings:
            memory = int(settings['memory'])
            if memory < 1 or memory > 256:
                logging.info("- memory should be between 1 and 256")
                memory = None

        if cpu and memory:
            logging.info("- assigning {} cpus".format(cpu))
            logging.info("- assigning {}GB of memory".format(memory))
            self.region.ex_update_node(node, cpu_count=cpu, ram_mb=memory)
        elif cpu:
            logging.info("- assigning {} cpus".format(cpu))
            self.region.ex_update_node(node, cpu_count=cpu)
        elif memory:
            logging.info("- assigning {}GB of memory".format(memory))
            self.region.ex_update_node(node, ram_mb=memory)

        if 'disks' in settings:
            for item in settings['disks']:
                attributes = item.split()
                if len(attributes) < 2:
                    size = int(attributes[0])
                    speed = 'STANDARD'
                else:
                    size = int(attributes[0])
                    speed = attributes[1].upper()

                if size < 1 or size > 1000:
                    logging.info("- disk size cannot exceed 1000")
                elif speed not in ['STANDARD', 'HIGHPERFORMANCE', 'ECONOMIC']:
                    logging.info("- disk speed should be 'standard' or 'highperformance' or 'economic'")
                else:
                    while True:
                        try:
                            logging.info("- adding disk for {}GB '{}'".format(size, speed))
                            self.region.ex_add_storage_to_node(node, amount=size, speed=speed)

                        except Exception as feedback:
                            if 'RESOURCE_BUSY' in str(feedback):
                                time.sleep(10)
                                continue

                            else:
                                logging.info("- unable to add disk {}GB '{}'".format(size, speed))
                                logging.error(str(feedback))

                        break

        if 'monitoring' in settings:
            self.nodes._start_monitoring(node, settings['monitoring'])

        if 'glue' in settings:
            container._attach_node(node, settings['glue'])

        container._add_to_pool(node)
