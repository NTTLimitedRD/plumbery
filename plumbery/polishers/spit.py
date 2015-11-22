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
"""
The minimum action before rubbing an appliance
"""

import os

from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.deployment import ScriptDeployment
from libcloud.compute.deployment import SSHKeyDeployment

from plumbery.polisher import PlumberyPolisher


class SpitPolisher(PlumberyPolisher):
    """
    Make new appliances shine


    """

    def shine_node(self, node):
        """
        Rub it until it shines

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`
        """

        print "Spitting on node '{}'".format(node.name)

        # actions to be performed
        rubs = []

        # path to the public key that has to be pushed to new node
        publicKeyPath = os.path.expanduser('~/.ssh/id_rsa.pub')

        # read text of the public key
        publicKeyText = None
        with open(publicKeyPath) as stream:
            publicKeyText = stream.read()

        # will be added to the keys for root user on remote node
        if publicKeyText:
            rubs.append(SSHKeyDeployment(publicKeyText))

        # shell script to run on the remote server
        scriptText = None
        with open(os.path.dirname(__file__)+'/spit.sh') as stream:
            scriptText = stream.read()

        # this will be communicated to remote node and executed
        if scriptText:
            rubs.append(ScriptDeployment(publicKeyText))

        # rub this node
        if self.rub_node(node=node, rubs=MultiStepDeployment(rubs)):
            print '- done'
