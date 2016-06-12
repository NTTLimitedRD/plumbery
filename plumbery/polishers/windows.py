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

from pywinexe.api import cmd as run_cmd
from pywinexe.api import ps as run_ps

from libcloud.compute.types import NodeState
import winrm
from winrm.protocol import Protocol

from plumbery.polishers.base import NodeConfiguration
from plumbery.plogging import plogging


class WindowsConfiguration(NodeConfiguration):
    __name__ = 'WindowsConfiguration'
    _element_name_ = 'windows'
    _configuration_ = {
    }

    def __init__(self, engine, facility):
        self.secret = engine.get_shared_secret()
        # todo: provide a fittings-wide override.
        self.username = 'administrator'
        plogging.debug('Loading windows polisher')

    def _try_winrm(self, node):
        ip = node.private_ips[0]
        p = Protocol(
                endpoint='http://%s:5985/wsman' % ip,  # RFC 2732
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
        ip = node.private_ips[0]
        p = Protocol(
                endpoint='http://%s:5985/wsman' % ip,  # RFC 2732
                transport='ntlm',
                username=self.username,
                password=self.secret,
                server_cert_validation='ignore')
        shell_id = p.open_shell()
        std_out_logs = []
        std_err_logs = []

        # run the commands in sequence.
        for command, params in commands:
            command_id = p.run_command(shell_id, command, params)
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
        ip = node.private_ips[0]
        plogging.debug("Testing out quick function on %s", ip)
        out = run_cmd(
            'echo hello',
            args=[],
            user=self.username,
            password=self.secret,
            host=ip)
        plogging.info(out)
        plogging.debug("Running winexe to remotely configure %s", ip)
        cmds = [
            "winrm quickconfig -quiet",
            "winrm set winrm/config/service/auth @{Basic=\"true\"}",
            "winrm set winrm/config/service @{AllowUnencrypted=\"true\"}"
        ]
        for cmd in cmds:
            plogging.debug('Running command "%s"', cmd)
            out = run_cmd(
                cmd,
                args=[],
                user=self.username,
                password=self.secret,
                host=ip)
            plogging.info(out)

    def _lockdown_winrm(self, node):
        """
        Setup WinRM on a remote node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`
        """
        ip = node.private_ips[0]
        plogging.debug("Running winexe to remotely deconfigure %s", ip)
        cmds = [
            "winrm set winrm/config/service/auth @{Basic=\"false\"}",
            "winrm set winrm/config/service @{AllowUnencrypted=\"false\"}"
        ]
        for cmd in cmds:
            plogging.debug('Running command "%s"', cmd)
            out = run_cmd(
                cmd,
                args=[],
                user=self.username,
                password=self.secret,
                host=ip)
            plogging.info(out)

    def validate(self, settings):
        return True

    def reap(self, *args):
        plogging.debug('Reap for windows polisher (noop)')
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
        if self._element_name_ in settings:
            plogging.info("preparing node '{}'".format(settings['name']))
            if node is None:
                plogging.info("- not found")
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
                    plogging.info("- skipped - node is not running")
                    return

            ipv6 = node.extra['ipv6']
            ip = node.private_ips[0]
            if ipv6 is None:
                plogging.error('No ipv6 address for node, cannot configure')
                return

            # Check to see if WinRM works..
            try:
                self._try_winrm(node)
            except winrm.exceptions.InvalidCredentialsError:
                plogging.warn('initial login to %s failed, trying to setup winrm remotely',
                             ip)
                self._setup_winrm(node)
                self._try_winrm(node)
            except requests.exceptions.ConnectionError:
                plogging.warn('initial connection to %s failed, trying to setup winrm remotely',
                             ip)
                self._setup_winrm(node)
                self._try_winrm(node)

            # OK, we're all ready. Let's look at the node config and start commands
            cmds = []
            hostname = settings[self._element_name_].get('hostname', None)
            if hostname is not None and isinstance(hostname, str):
                cmds.append(('powershell.exe', ['Rename-Computer', '-NewName', hostname]))

            extra_cmds = settings[self._element_name_].get('cmds', [])
            for command in extra_cmds:
                command = command.rstrip()
                command_parts = command.split(' ')
                cmds.append((command_parts[0], command_parts[1:]))

            out, err = self._winrm_commands(node, cmds)
            plogging.info(out)
            plogging.warning(err)

            plogging.debug('locking down winrm')
            self._lockdown_winrm(node)
        else:
            return False
