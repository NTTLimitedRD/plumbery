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
import os
import yaml

import netifaces

from libcloud.compute.deployment import FileDeployment
from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.deployment import ScriptDeployment
from libcloud.compute.deployment import SSHKeyDeployment
from libcloud.compute.ssh import SSHClient

from plumbery.exceptions import PlumberyException
from plumbery.polisher import PlumberyPolisher


class RubPolisher(PlumberyPolisher):
    """
    Bootstraps nodes via ssh

    This polisher looks at each node in sequence, and contact selected nodes
    via ssh to rub them. The goal here is to accelerate post-creation tasks as
    much as possible.

    Bootstrapping steps can consist of multiple tasks:

    * push a SSH public key to allow for automated secured communications
    * ask for package update
    * install docker
    * install any pythons script
    * install Stackstorm
    * configure a Chef client
    * register a node to a monitoring dashboard
    * ...

    To activate this polisher you have to mention it in the fittings plan,
    like in the following example::

        ---
        safeMode: False
        polishers:
          - rub:
              key: ~/.ssh/id_rsa.pub
        ---
        # Frankfurt in Europe
        locationId: EU6
        regionId: dd-eu
        ...

    Plumbery will only rub nodes that have been configured for it. The example
    below demonstrates how this can be done for multiple docker containers::

        # some docker resources
        - docker:
            domain: *vdc1
            ethernet: *containers
            nodes:
              - docker1:
                  rub: &docker
                    - run rub.update.sh
                    - run rub.docker.sh
              - docker2:
                  rub: *docker
              - docker3:
                  rub: *docker


    In the real life when you have to rub any appliance, you need to be close
    to the stuff and to touch it. This is the same for virtual fittings.
    This polisher has the need to communicate directly with target
    nodes over the network.

    This connectivity can become quite complicated because of the potential mix
    of private and public networks, firewalls, etc. To stay safe plumbery
    enforces a simple beachheading model, where network connectivity with end
    nodes is a no brainer.

    This model is based on predefined network addresses for plumbery itself,
    as in the snippet below::

        ---
        # Frankfurt in Europe
        locationId: EU6
        regionId: dd-eu

        # network subnets are 10.1.x.y
        rub:
          - beachhead: 10.1.3.4

    Here nodes at EU6 will be rubbed only if the machine that is
    executing plumbery has the adress 10.1.3.4. In other cases, plumbery will
    state that the location is out of reach.

    """

    def _apply_rubs(self, node, steps):
        """
        Does the actual job over SSH

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param steps: the various steps of the rubbing
        :type steps: :class:`libcloud.compute.deployment.MultiStepDeployment`

        :returns: ``bool``
            - ``True`` if everything went fine, ``False`` otherwise

        """

        # select the address to use
        if len(node.public_ips) > 0:
            target_ip = public_ips[0]
        elif node.extra['ipv6']:
            target_ip = node.extra['ipv6']
        else:
            target_ip = node.private_ips[0]

        # use libcloud to communicate with remote nodes
        session = SSHClient(hostname=target_ip,
                            port=22,
                            username='root',
                            password=self.secret,
                            key_files=None,
                            timeout=6)

        try:
            session.connect()
            node = steps.run(node, session)

        except Exception as feedback:
            logging.info("Error: unable to rub '{}' at '{}'!".format(node.name,
                                                             target_ip))
            logging.info(str(feedback))
            result = False

        else:
            result = True

        try:
            session.close()
        except:
            pass

        return result

    def _get_rubs(self, node, settings):
        """
        Defines the set of actions to be done on a node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        :returns: a list of { 'description': ..., 'genius': ... }

        """

        if not isinstance(settings, dict) or 'rub' not in settings:
            return []

        rubs = []

        if self.key is not None:
            rubs.append({
                'description': 'deploy SSH public key',
                'genius': SSHKeyDeployment(self.key)})

        if settings['rub'] is not None:
            for script in settings['rub']:

                tokens = script.split(' ')
                if len(tokens) == 1:
                    tokens.insert(0, 'run')

                if tokens[0] == 'run':

                    script = tokens[1]
                    if len(tokens) > 2:
                        args = tokens[2:]
                    else:
                        args = None

                    try:
                        with open(os.path.dirname(__file__)+'/'+script) as stream:
                            text = stream.read()
                            if text:
                                rubs.append({
                                    'description': ' '.join(tokens),
                                    'genius': ScriptDeployment(script=text,
                                                                 args=args)})

                    except IOError:
                        raise PlumberyException("Error: cannot read '{}'"
                                                            .format(script))

                elif tokens[0] == 'put':

                    file = tokens[1]
                    if len(tokens) > 2:
                        destination = tokens[2]
                    else:
                        destination = './'+file

                    try:
                        source = os.path.dirname(__file__)+'/'+file
                        with open(source) as stream:
                            text = stream.read()
                            if text:
                                rubs.append({
                                    'description': ' '.join(tokens),
                                    'genius': FileDeployment(source=source,
                                                         target=destination)})

                    except IOError:
                        raise PlumberyException("Error: cannot read '{}'"
                                                            .format(file))

                else:
                    raise PlumberyException("Error: unknown directive '{}'"
                                                    .format(' '.join(tokens)))


        return rubs

    def go(self, engine):
        """
        Starts the rubbing process

        :param engine: access to global parameters and functions
        :type engine: :class:`plumbery.PlumberyEngine`

        """

        self.engine = engine

        self.report = []

        self.secret = engine.get_shared_secret()

        self.key = None
        if 'key' in self.settings:
            try:
                path = os.path.expanduser(self.settings['key'])

                with open(path) as stream:
                    self.key = stream.read()
                    stream.close()

            except IOError:
                pass

    def move_to(self, facility):
        """
        Checks if we can beachhead at this facility

        :param facility: access to local parameters and functions
        :type facility: :class:`plumbery.PlumberyFacility`


        """

        self.facility = facility

        self.beachheading = False

        try:

            self.addresses = []
            for interface in netifaces.interfaces():
                addresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addresses.keys():
                    for address in addresses[netifaces.AF_INET]:
                        self.addresses.append(address['addr'])
                if netifaces.AF_INET6 in addresses.keys():
                    for address in addresses[netifaces.AF_INET6]:
                        self.addresses.append(address['addr'])

        except Exception as feedback:
            pass

        for item in self.facility.fittings.rub:
            if not isinstance(item, dict):
                continue
            if 'beachhead' not in item.keys():
                continue
            if item['beachhead'] in self.addresses:
                self.beachheading = True
                break

        if self.beachheading:
            logging.info("- beachheading at '{}'".format(self.facility.fittings.locationId))
        else:
            logging.info("- '{}' is unreachable".format(self.facility.fittings.locationId))

    def shine_node(self, node, settings):
        """
        Rubs a node

        :param node: the node to be polished
        :type node: :class:`libcloud.compute.base.Node`

        :param settings: the fittings plan for this node
        :type settings: ``dict``

        """

        if not self.beachheading:
            self.report.append({node.name: {
                'status': 'unreachable'
                }})
            return

        rubs = self._get_rubs(node, settings)
        if len(rubs) < 1:
            self.report.append({node.name: {
                'status': 'skipped - nothing to do'
                }})
            return

        descriptions = []
        steps = []
        for item in rubs:
            descriptions.append(item['description'])
            steps.append(item['genius'])

        if self._apply_rubs(node, MultiStepDeployment(steps)):
            logging.info('- done')
            self.report.append({node.name: {
                'status': 'completed',
                'rubs': descriptions
                }})

        else:
            logging.info('- failed')
            self.report.append({node.name: {
                'status': 'failed',
                'rubs': descriptions
                }})

    def reap(self):
        """
        Reports on rubbing

        """

        if 'reap' in self.settings:
            fileName = self.settings['reap']
        else:
            fileName = 'rub.yaml'

        logging.info("Reporting in '{}'".format(fileName))
        with open(fileName, 'w') as stream:
            stream.write(yaml.dump(self.report, default_flow_style=False))
            stream.close()
