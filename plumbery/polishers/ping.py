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

from libcloud.compute.base import NodeState

from plumbery.polisher import PlumberyPolisher
from plumbery.plogging import plogging


class PingPolisher(PlumberyPolisher):
    """
    Checks state of nodes

    """

    def shine_node(self, node, settings, container):
        """
        Lists network address of a node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        :param container: the container of this node
        :type container: :class:`plumbery.PlumberyInfrastructure`

        """

        plogging.info("Pinging node '{}'".format(settings['name']))
        if node is None:
            plogging.info("- not found")
            return

        if 'description' in node.extra:
            description = node.extra['description'].replace(
                '#plumbery', '').strip()
            if len(description) > 0:
                plogging.info("- {}".format(description))

        if node.state == NodeState.RUNNING:
            plogging.info("- node is up and running")
        elif node.state in [NodeState.TERMINATED,
                            NodeState.STOPPED,
                            NodeState.SUSPENDED]:
            plogging.info("- node has been stopped")
        else:
            plogging.info("- state: {}".format(node.state))

        # hack because the driver does not report public ipv4 accurately
        if len(node.public_ips) < 1:
            domain = container.get_network_domain(
                container.blueprint['domain']['name'])
            for rule in container.region.ex_list_nat_rules(domain):
                if rule.internal_ip == node.private_ips[0]:
                    node.public_ips.append(rule.external_ip)
                    break

        if len(node.public_ips) > 0:
            plogging.info("- public: {}".format(
                node.public_ips[0]))

        for item in node.private_ips:
            plogging.info("- private: {}".format(str(item)))

        if node.extra['ipv6']:
            plogging.info("- ipv6: {}".format(str(node.extra['ipv6'])))
