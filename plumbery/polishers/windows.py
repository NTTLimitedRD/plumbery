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
import requests

import pywinexe

from libcloud.compute.types import NodeState
from pywinrm.protocol import Protocol

from plumbery.polishers.prepare import PreparePolisher
from plumbery.polisher import PlumberyPolisher


class WindowsPolisher(PlumberyPolisher):
    # I don't like this..
    setup_winrm = "Invoke-Expression ((New-Object System.Net.Webclient).DownloadString('https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1'))"

    def _setup_winrm(self, node):
        """
        Setup WinRM on a remote node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`
        """
        ipv6 = node.extra['ipv6']
        pywinexe.api.run(
                [WindowsPolisher.setup_winrm],
                cmd='powershell.exe',
                user=self.username,
                password=self.secret,
                host=ipv6)

    def go(self, engine):
        super(PreparePolisher, self).go(engine)
        self.secret = engine.get_shared_secret()
        # todo: provide a fittings-wide override.
        self.username = 'administrator'

    def shine_node(self, node, settings, container):
        """
        prepares a node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        :param container: the container of this node
        :type container: :class:`plumbery.PlumberyInfrastructure`

        """

        logging.info("preparing node '{}'".format(settings['name']))
        if node is None:
            logging.info("- not found")
            return

        timeout = 300
        tick = 6
        while node.extra['status'].action == 'START_SERVER':
            time.sleep(tick)
            node = self.nodes.get_node(node.name)
            timeout -= tick
            if timeout < 0:
                break

        if node.state != NodeState.RUNNING:
            logging.info("- skipped - node is not running")
            return

        ipv6 = node.extra['ipv6']
        if ipv6 is None:
            logging.error('No ipv6 address for node, cannot configure')
            return

        # Check to see if WinRM works..
        try:
            p = Protocol(
                endpoint='https://[%s]:5986/wsman' % ipv6, # RFC 2732
                transport='ntlm',
                username=self.username,
                password=self.secret,
                server_cert_validation='ignore')
            shell_id = p.open_shell()
            command_id = p.run_command(shell_id, 'ipconfig', ['/all'])
            std_out, std_err, status_code = p.get_command_output(shell_id, command_id)
            p.cleanup_command(shell_id, command_id)
            p.close_shell(shell_id)
        except requests.exceptions.ConnectionError:
            self._setup_winrm(node)
