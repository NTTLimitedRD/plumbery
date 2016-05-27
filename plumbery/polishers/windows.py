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
import requests

import pywinexe

from libcloud.compute.types import NodeState
from winrm.protocol import Protocol

from plumbery.polishers.base import NodeConfiguration

from plumbery.logging import setup_logging
logging = setup_logging()


class WindowsConfiguration(NodeConfiguration):
    __name__ = 'WindowsConfiguration'
    _element_name_ = 'windows'
    _configuration_ = {
    }
    # I don't like this..
    setup_winrm = "Invoke-Expression ((New-Object System.Net.Webclient).DownloadString('https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1'))"

    def __init__(self, engine):
        self.secret = engine.get_shared_secret()
        # todo: provide a fittings-wide override.
        self.username = 'administrator'
        logging.debug('Loading windows polisher')

    def _try_winrm(self, node):
        ipv6 = node.extra['ipv6']
        p = Protocol(
                endpoint='https://[%s]:5986/wsman' % ipv6,  # RFC 2732
                transport='ntlm',
                username=self.username,
                password=self.secret,
                server_cert_validation='ignore')
        shell_id = p.open_shell()
        command_id = p.run_command(shell_id, 'ipconfig', ['/all'])
        std_out, std_err, status_code = p.get_command_output(shell_id, command_id)
        p.cleanup_command(shell_id, command_id)
        p.close_shell(shell_id)
        return std_out

    def _winrm_commands(self, node, commands):
        ipv6 = node.extra['ipv6']
        p = Protocol(
                endpoint='https://[%s]:5986/wsman' % ipv6,  # RFC 2732
                transport='ntlm',
                username=self.username,
                password=self.secret,
                server_cert_validation='ignore')
        shell_id = p.open_shell()
        std_out_logs = []
        std_err_logs = []

        # run the commands in sequence.
        for command, params in commands:
            command_id = p.run_ps(shell_id, command, params)
            std_out, std_err, status_code = p.get_command_output(shell_id, command_id)
            std_out_logs.append(std_out)
            std_err_logs.append(std_err)
            p.cleanup_command(shell_id, command_id)

        p.close_shell(shell_id)
        return std_out_logs, std_err_logs

    def _setup_winrm(self, node):
        """
        Setup WinRM on a remote node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`
        """
        ipv6 = node.extra['ipv6']
        pywinexe.api.run(
                [WindowsConfiguration.setup_winrm],
                cmd='powershell.exe',
                user=self.username,
                password=self.secret,
                host=ipv6)

    def validate(self, settings):
        return True

    def reap(self, *args):
        logging.debug('Reap for windows polisher (noop)')
        return

    def configure(self, node, settings):
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
            self._try_winrm(node)
        except requests.exceptions.ConnectionError:
            logging.warn('initial connection failed, trying to setup winrm remotely')
            self._setup_winrm(node)
            self._try_winrm(node)

        # OK, we're all ready. Let's look at the node config and start commands
        cmds = []
        hostname = settings.get('hostname', None)
        if hostname is not None and isinstance(hostname, str):
            cmds.append(('Rename-Computer', ['-NewName', hostname]))

        extra_cmds = settings.get('cmds', [])
        for command in extra_cmds:
            command = command.rstrip()
            command_parts = command.split(' ')
            cmds.append((command_parts[0], command_parts[1:]))

        out, err = self._winrm_commands(node, cmds)
        logging.info(out)
        logging.warning(err)
