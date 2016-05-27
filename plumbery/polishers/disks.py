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
import time

from plumbery.polishers.base import NodeConfiguration
from plumbery.exception import ConfigurationError
from plumbery.logging import setup_logging
logging = setup_logging()


class DisksConfiguration(NodeConfiguration):
    __name__ = 'DisksConfiguration'
    _element_name_ = 'disks'
    _configuration_ = {
    }

    def validate(self, settings):
        if self._element_name_ in settings:
            value = settings[self._element_name_].upper()
            if value not in ['ESSENTIALS', 'ADVANCED']:
                raise ConfigurationError(
                    "- monitoring should be "
                    "either 'essentials' or 'advanced'")

    def configure(self, node, settings):
        if self._element_name_ in settings:
            for item in settings['disks']:
                logging.debug("- setting disk {}".format(item))
                attributes = item.split()
                if len(attributes) < 2:
                    logging.info("- malformed disk attributes;"
                                 " provide disk id and size in GB, e.g., 1 50;"
                                 " add disk type if needed, e.g., economy")
                elif len(attributes) < 3:
                    id = int(attributes[0])
                    size = int(attributes[1])
                    speed = 'standard'
                else:
                    id = int(attributes[0])
                    size = int(attributes[1])
                    speed = attributes[2]

                self.set_node_disk(node, id, size, speed)
            return True
        return False

    def deconfigure(self, node, settings):
        return True

    def set_node_disk(self, node, id, size, speed='standard'):
        """
        Sets a virtual disk

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param id: the disk id, starting at 0 and growing
        :type id: ``int``

        :param size: the disk size, expressed in Giga bytes
        :type size: ``int``

        :param speed: storage type, either 'standard',
            'highperformance' or 'economy'
        :type speed: ``str``

        """

        if size < 1:
            logging.info("- minimum disk size is 1 GB")
            return

        if size > 1000:
            logging.info("- disk size cannot exceed 1000 GB")
            return

        if speed not in ['standard', 'highperformance', 'economy']:
            logging.info("- disk speed should be either 'standard' "
                         "or 'highperformance' or 'economy'")
            return

        if 'disks' in node.extra:
            for disk in node.extra['disks']:
                if disk['scsiId'] == id:
                    changed = False

                    if disk['size'] > size:
                        logging.info("- disk shrinking could break the node")
                        logging.info("- skipped - disk {} will not be reduced"
                                     .format(id))

                    if disk['size'] < size:
                        logging.info("- expanding disk {} to {} GB"
                                     .format(id, size))
                        self.change_node_disk_size(node, disk['id'], size)
                        changed = True

                    if disk['speed'].lower() != speed.lower():
                        logging.info("- changing disk {} to '{}'"
                                     .format(id, speed))
                        self.change_node_disk_speed(node, disk['id'], speed)
                        changed = True

                    if not changed:
                        logging.debug("- no change in disk {}".format(id))

                    return

        logging.info("- adding {} GB '{}' disk".format(
            size, speed))

        if self.engine.safeMode:
            logging.info("- skipped - safe mode")
            return

        while True:
            try:
                self.region.ex_add_storage_to_node(
                    node=node,
                    amount=size,
                    speed=speed.upper())

                logging.info("- in progress")

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

        if self.engine.safeMode:
            logging.info("- skipped - safe mode")
            return

        while True:
            try:
                self.region.ex_change_storage_size(
                    node=node,
                    disk_id=id,
                    size=size)

                logging.info("- in progress")

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

        :param speed: storage type, either 'standard',
            'highperformance' or 'economy'
        :type speed: ``str``

        """

        if self.engine.safeMode:
            logging.info("- skipped - safe mode")
            return

        while True:
            try:
                self.region.ex_change_storage_speed(
                    node=node,
                    disk_id=id,
                    speed=speed)

                logging.info("- in progress")

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