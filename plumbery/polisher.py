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

# standard libraries
import os

from libcloud.compute.ssh import SSHClient


__all__ = ['PlumberyPolisher']


class PlumberyPolisher:
    """Make new appliances shine"""

    @classmethod
    def from_shelf(cls, polishId):
        """
        Pick up a polisher from the shelf

        :param polishId: name of the polisher to use, e.g., ``spit``
        :type polishId: ``str``

        :return: instance of a polisher ready to use
        :rtype: :class:`PlumberyPolisher`
        """

        # we may not find a suitable polisher
        try:
            moduleName = 'polishers.' + polishId
            polisherName = polishId.capitalize() + 'Polisher'

            polisherModule = __import__(moduleName, globals(), locals(), [polisherName])
            polisherClass = getattr(polisherModule, polisherName)
            return polisherClass()

        except Exception as feedback:
            print("Error: unable to load polisher '{}'!".format(polishId))
            print(str(feedback))
            return None

    def shine_node(self, node):
        """
        Rub it until it shines

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`
        """

        raise NotImplementedError("Error: do not know how to polish '{}'".format(node.name))

    @classmethod
    def rub_node(cls, node, rubs):
        """
        Communicate with the node over SSH
        """

        # get root password from environment SHARED_SECRET
        # with bash, edit ~/.bash_profile to export in local environment
        sharedSecret = os.getenv('SHARED_SECRET', 'whatSUpDoc')

        # use libcloud to communicate to remote nodes
        session = SSHClient(hostname=node.private_ips[0],
                            port=22,
                            username='root',
                            password=sharedSecret,
                            key_files=None,
                            timeout=15)

        # end to end private connectivity is required to succeed
        try:
            session.connect()
            node = rubs.run(node, session)

        except Exception as feedback:
            print("Error: unable to rub '{}' at '{}'!".format(node.name,
                                                             node.private_ips[0]))
            print(str(feedback))
            result = False

        else:
            result = True

        # closing could kill everything as well
        try:
            session.close()
        except:
            pass

        return result
