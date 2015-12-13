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
import yaml

from plumbery.exceptions import PlumberyException
from plumbery.polisher import PlumberyPolisher


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

        self.report = []

    def move_to(self, facility):
        """
        Moves to another API endpoint

        :param facility: access to local parameters and functions
        :type facility: :class:`plumbery.PlumberyFacility`


        """

        self.facility = facility
        self.region = facility.region

    def shine_node(self, node, settings):
        """
        Finalizes setup of one node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        """

        print node
        print settings

        spits = []

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
            self.region.ex_update_node(node, cpu_count=cpu, ram_mb=memory)
            spits.append("cpu: {}".format(cpu))
            spits.append("memory: {}".format(memory))
        elif cpu:
            self.region.ex_update_node(node, cpu_count=cpu)
            spits.append("cpu: {}".format(cpu))
        elif memory:
            self.region.ex_update_node(node, ram_mb=memory)
            spits.append("memory: {}".format(memory))

        if 'disks' in settings:
            for item in settings['disks']:
                attributes = item.split( )
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
                            self.region.ex_add_storage_to_node(node, amount=size, speed=speed)
                            logging.info("- adding disk for {}GB '{}'".format(size, speed))
                            spits.append("disk: {} {}".format(size, speed))

                        except Exception as feedback:
                            if 'RESOURCE_BUSY' in str(feedback):
                                time.sleep(10)
                                continue

                            else:
                                logging.info("- unable to add disk {}GB '{}'".format(size, speed))
                                logging.info(str(feedback))

                        break

        if 'monitoring' in settings:
            value = settings['monitoring'].upper()
            if value not in ['ESSENTIALS', 'ADVANCED']:
                logging.info("- monitoring should be 'essentials' or 'advanced'")
            else:
                while True:
                    try:
                        self.region.ex_enable_monitoring(node, service_plan=value)
                        logging.info("- monitoring set to '{}'".format(value))
                        spits.append("monitoring: {}".format(value))

                    except Exception as feedback:
                        if 'RESOURCE_BUSY' in str(feedback):
                            time.sleep(10)
                            continue

                        elif 'NO_CHANGE' in str(feedback):
                            logging.info("- monitoring has not been changed")

                        else:
                            logging.info("- unable to set '{0}' monitoring".format(value))
                            logging.info(str(feedback))


                    break

        self.report.append({node.name: spits})

    def reap(self):
        """
        Saves information gathered through the polishing sequence

        All information captured in dumped in a file, in YAML format,
        to provide a flexible and accurate inventory of all live nodes
        described in the fittings plan.

        """

        if 'reap' in self.settings:
            fileName = self.settings['reap']
        else:
            fileName = 'spit.yaml'

        logging.info("Spitting in '{}'".format(fileName))
        with open(fileName, 'w') as stream:
            stream.write(yaml.dump(self.report, default_flow_style=False))
            stream.close()
