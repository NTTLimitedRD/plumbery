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

        logging.info("Spitting at blueprint '{}'".format(
            container.blueprint['target']))

        if container.network is None:
            logging.info("- aborted - no network here")
            return

        nodes = PlumberyNodes(self.facility)

        names = nodes.list_nodes(container.blueprint)

        logging.info("- waiting for nodes to be deployed")

        for name in names:
            while True:
                node = nodes.get_node(name)
                if node is None:
                    logging.info("- aborted - missing node '{}'".format(name))
                    return

                if node.extra['status'].action is None:
                    break

                if (node is not None
                        and node.extra['status'].failure_reason is not None):

                    logging.info("- aborted - failed deployment "
                                 "of node '{}'".format(name))
                    return

                time.sleep(20)

        logging.info("- nodes have been deployed")

        container._build_firewall_rules()

        container._build_balancer()

    def change_node_disk_size(self, node, id, size):
        """
        Changes an existing virtual disk

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param id: the disk unique identifier, as reported by the API
        :type id: ``str``

        :param size: the disk size, expressed in Giga bytes
        :type size: ``int``

        """

        while True:
            try:
                self.region.ex_change_storage_size(
                    node=node,
                    disk_id=id,
                    size=size)

            except Exception as feedback:
                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                if 'Please try again later' in str(feedback):
                    time.sleep(10)
                    continue

                logging.info("- unable to change disk size to {}GB"
                             .format(size))
                logging.error(str(feedback))

            break

    def change_node_disk_speed(self, node, id, speed):
        """
        Changes an existing virtual disk

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param id: the disk unique identifier, as reported by the API
        :type id: ``str``

        :param speed: storage type, either 'standard', 'highperformance' or 'economy'
        :type speed: ``str``

        """

        while True:
            try:
                self.region.ex_change_storage_speed(
                    node=node,
                    disk_id=id,
                    speed=speed)

            except Exception as feedback:
                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                if 'Please try again later' in str(feedback):
                    time.sleep(10)
                    continue

                logging.info("- unable to change disk to '{}'"
                             .format(speed))
                logging.error(str(feedback))

            break

    def set_node_disk(self, node, id, size, speed='standard'):
        """
        Sets a virtual disk

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param id: the disk id, starting at 0 and growing
        :type id: ``int``

        :param size: the disk size, expressed in Giga bytes
        :type size: ``int``

        :param speed: storage type, either 'standard', 'highperformance' or 'economy'
        :type speed: ``str``

        """

        if size < 1:
            logging.info("- minimum disk size is 1 GB")
            return

        if size > 1000:
            logging.info("- disk size cannot exceed 1000 GB")
            return

        speed = speed.upper()
        if speed not in ['STANDARD', 'HIGHPERFORMANCE', 'ECONOMY']:
            logging.info("- disk speed should be either 'standard' "
                         "or 'highperformance' or 'economy'")
            return

        if 'disks' in node.extra:
            for disk in node.extra['disks']:
                if disk['scsiId'] == id:
                    changed = False

                    if disk['size'] != size:
                        logging.info("- expanding disk {} to {} GB".format(
                            id, size))
                        self.change_node_disk_size(node, disk['id'], size)
                        changed = True

                    if disk['speed'] != speed:
                        logging.info("- changing disk {} to '{}'".format(
                            id, speed))
                        self.change_node_disk_speed(node, disk['id'], speed)
                        changed = True

                    if not changed:
                        logging.info("- no change in disk {}".format(id))

                    return

        while True:
            try:
                logging.info("- adding disk for {}GB '{}'".format(
                    size, speed))
                self.region.ex_add_storage_to_node(
                    node=node,
                    amount=size,
                    speed=speed)

            except Exception as feedback:
                if 'RESOURCE_BUSY' in str(feedback):
                    time.sleep(10)
                    continue

                if 'Please try again later' in str(feedback):
                    time.sleep(10)
                    continue

                logging.info("- unable to add disk {} GB '{}'"
                             .format(size, speed))
                logging.error(str(feedback))

            break

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

        logging.info("Spitting at node '{}'".format(settings['name']))
        if node is None:
            logging.info("- not found")
            return

        if 'disks' in settings:
            for item in settings['disks']:
                logging.debug("- setting disk {}".format(item))
                attributes = item.split()
                if len(attributes) < 2:
                    logging.info("- malformed disk atributes;"
                                 " provide disk id and size in GB, e.g., 1 50;"
                                 " add disk type if needed, e.g., highperformance")
                elif len(attributes) < 3:
                    id = int(attributes[0])
                    size = int(attributes[1])
                    speed = 'standard'
                else:
                    id = int(attributes[0])
                    size = int(attributes[1])
                    speed = attributes[2]

                self.set_node_disk(node, id, size, speed)

        if 'monitoring' in settings:
            self.nodes._start_monitoring(node, settings['monitoring'])

        if 'glue' in settings:
            container._attach_node(node, settings['glue'])

        container._add_to_pool(node)
