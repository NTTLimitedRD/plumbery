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

from __future__ import absolute_import

import hashlib
import logging
import os
import random
import requests
import string
import sys
import time
import uuid
import yaml
from six import string_types

try:
    from Cryptodome.PublicKey import RSA
    HAS_CRYPTO = True
except ImportError:
    logging.getLogger().error('No Cryptodome support loaded')
    HAS_CRYPTO = False


from libcloud.compute.providers import get_driver as get_compute_driver
from libcloud.compute.types import Provider as ComputeProvider
from libcloud.loadbalancer.providers import get_driver as get_balancer_driver
from libcloud.loadbalancer.types import Provider as BalancerProvider
from libcloud.backup.providers import get_driver as get_backup_driver
from libcloud.backup.types import Provider as BackupProvider

from plumbery import __version__
from plumbery.action import PlumberyActionLoader
from plumbery.exception import PlumberyException
from plumbery.facility import PlumberyFacility
from plumbery.plogging import plogging
from plumbery.polisher import PlumberyPolisher
from plumbery.text import PlumberyText, PlumberyContext


__all__ = ['PlumberyEngine']


class PlumberyEngine(object):
    """
    Infrastructure as code at Dimension Data with Apache Libcloud

    :param plan: the fittings plan
    :type plan: ``str`` or ``file`` or ``dict`` or ``list`` of ``dict``

    :param parameters: the external parameters
    :type plan: ``str`` or ``file`` or ``dict``

    Plumbery is a convenient tool for infrastructure managers at cloud times.
    It allows for easy and repeatable deployments of various
    fittings, including compute nodes and related storage. It allows also for
    quick dismandling of the fittings when required.
    The idea here is not to compete with respected solutions such as chef or
    puppet. At its name implies, plumbery is targeting pipes and fittings, the
    very basic utility stuff that sophisticated tools can leverage.

    Example::

        from plumbery.engine import PlumberyEngine
        engine = PlumberyEngine('fittings.yaml')
        engine.build_all_blueprints()

    In this example the overall plan, in textual format, is given to the engine
    in preparation of subsequent processing. The software is not trying to
    guess a name by default, so if you do not provide a name, no configuration
    file is loaded. You can load the plan at any stage, or restart the engine
    with an updated plan, by invoking the member function ``parse_layout()``

    Note:
        While plumbery is not making assumptions for your configuration files,
        if your infrastructure is simple enough to fit in one single file then
        you are highly encouraged to name it ``fittings.yaml``

    Beyond the plan for your fittings, plumbery is also requiring some specific
    credentials to connect to cloud providers. To preserve the confidentiality
    of such information, it is read from the environment, and not from any
    configuration file. Therefore the need for local setup before running
    plumbery. This is part of the installation process.

    Last but not least, plumbery sets the root password of any new server that
    it creates. For obvious security reasons this is not taken from the
    fittings plan but from the environment, or it can be set in code.

    Under Linux, you may want to edit ``~/.bash_profile`` like this::

        # credentials to access cloud resources from Dimension Data
        export MCP_USERNAME='foo.bar'
        export MCP_PASSWORD='WhatsUpDoc'

        # password to access nodes remotely
        export SHARED_SECRET='*you really want to put a tricky password here*'

    These simple precautions are aiming to protect your infrastructure as much
    as possible. The general goal is to minimize risks induced by exposure to
    your fittings plan. You may lead transformation towards so-called
    infrastructure as code, and for this you will add version control to your
    fittings plan. As a result, plans will be stored in git or equivalent, and
    shared across some people.

    """

    def __init__(self, plan=None, parameters=None):
        """
        Ignites the plumbing engine

        :param plan: the fittings plan
        :type plan: ``str`` or ``file`` or ``dict`` or ``list`` of ``dict``

        :param parameters: the external parameters
        :type plan: ``str`` or ``file`` or ``dict``

        """
        self.c0 = time.clock()
        self.t0 = time.time()

        self.defaults = {}

        self.facilities = []

        self.information = []

        self.links = {}

        self.safeMode = False

        self.parameters = {}

        self.polishers = []

        self.buildPolisher = 'configure'

        self._sharedUser = None

        self._sharedSecret = None

        self.secrets = {}
        self.secretsId = None

        self._userName = None

        self._userPassword = None

        # will be overridden to fittings path if provided
        self.working_directory = os.getcwd()
        self.set_parameters(parameters)
        self.set_fittings(plan)

    def set_parameters(self, parameters=None):
        """
        Changes the parameters of the running engine

        :param parameters: the new parameters
        :type parameters: ``str`` or ``file`` or ``dict``

        Parameters are a dictionary of key-value pairs.
        If a string is provided, it will contain a reference to some textual
        content (file name or URL).
        If a file handle is provided, content is read as YAML.

        """

        if not parameters:
            return

        if isinstance(parameters, string_types):

            if parameters.startswith(("https://", "http://")):
                response = requests.get(parameters)
                parameters = response.text
            else:
                parameters = open(parameters, 'r')
            parameters = yaml.load(parameters)

        if isinstance(parameters, list):
            pdict = {}
            for item in parameters:
                (key, value) = item.split('=')
                pdict[key] = value
            parameters = pdict

        plogging.debug("Parameters:")
        for key in parameters:
            if key not in self.parameters:
                self.parameters[key] = {}
            self.parameters[key]['value'] = parameters[key]
            plogging.debug("- {}: {}".format(
                key, self.parameters[key]['value']))

    def get_parameters(self):
        """
        Retrieves values of all parameters

        :return: a dictionary of all parameters
        :rtype: ``dict``

        """

        parameters = {}

        for key in self.parameters:
            parameters['parameter.'+key] = self.get_parameter(key)

        return parameters

    def get_parameter(self, label):
        """
        Retrieves value of some parameter

        :param label: the name of the parameter to be retrieved
        :type label: ``str``

        :return: the value set in fittings plan, or `None`
        :rtype: ``str`` most often, or ``dict`` or something else

        """

        label = label.split('.')[0]

        if label not in self.parameters:
            raise KeyError("Parameter '{}' is unknown".format(label))

        if 'value' in self.parameters[label]:
            return self.parameters[label]['value']

        if 'default' not in self.parameters[label]:
            raise ValueError("Parameter '{}' has no default value"
                             .format(label))

        return self.parameters[label]['default']

    def set_fittings(self, plan=None):
        """
        Loads the fittings plan for this engine instance

        :param plan: the file that contains fittings plan
        :type plan: ``str`` or ``file`` or ``dict`` or ``list`` of ``dict``

        The fittings plan is expected to follow YAML specifications, and it
        must have multiple documents in it. The first document provides
        general configuration parameters for the engine. Subsequent documents
        describe the various locations for the fittings.

        An example of a minimum fittings plan::

            # Frankfurt in Europe
            locationId: EU6

            blueprints:

              - myBluePrint:
                  domain:
                    name: myDC
                  ethernet:
                    name: myVLAN
                    subnet: 10.1.10.0
                  nodes:
                    - myServer

        In this example, the plan is to deploy a single node in the data centre
        at Frankfurt, in Europe. The node `myServer` will be placed in a
        network named `myVLAN`, and the network will be part of a network
        domain acting as a virtual data centre, `myDC`. The blueprint has a
        name, `myBluePrint`, so that it can be handled independently from
        other blueprints.

        """

        if plan is None:
            plan = os.getenv('PLUMBERY')

        if isinstance(plan, string_types):
            # hash reference to the fittings plan, not content of it
            self.secretsId = hashlib.md5(plan.encode('utf-8')).hexdigest()

            if plan.startswith(("https://", "http://")):
                response = requests.get(plan)
                plan = response.text

            elif plan == '-':
                plan = sys.stdin.read()

            elif '\n' not in plan:
                self.working_directory = os.path.dirname(plan)
                plan = open(plan, 'r').read()

            # load default values for parameters
            parameters = self.get_parameters()

            documents = plan.split('\n---')
            for document in documents:
                if '\n' in document:
                    settings = yaml.load(document)

                    if 'parameters' in settings:
                        for key in settings['parameters'].keys():
                            if 'parameter.'+key in parameters:
                                continue
                            parameters['parameter.'+key] = settings['parameters'][key]['default']
                    break

            # expand parameters
            environment = PlumberyContext(dictionary=parameters)
            plan = PlumberyText.expand_parameters(plan, environment)

        if not plan:
            return

        if isinstance(plan, dict):
            documents = [plan]
            self.secretsId = hashlib.md5(str(plan).encode('utf-8')).hexdigest()

        elif isinstance(plan, list):
            documents = plan
            self.secretsId = hashlib.md5(str(plan).encode('utf-8')).hexdigest()

        else:
            documents = list(yaml.load_all(plan))

        if not isinstance(documents, list):
            raise TypeError('Fittings should be a list of dictionaries')

        # first document contains engine settings
        if len(documents) > 1:
            self.set_settings(documents.pop(0))

        # then one document per facility
        for document in documents:
            self.add_facility(document)

        self.load_secrets()

        if self.safeMode:
            plogging.info(
                "Running in safe mode"
                " - no actual change will be made to the fittings")

    def set_settings(self, settings):
        """
        Changes the settings of the engine

        :param settings: the new settings
        :type settings: ``dict``

        """

        if not isinstance(settings, dict):
            raise TypeError('settings should be a dictionary')

        if 'buildPolisher' in settings:
            if not isinstance(settings['buildPolisher'], str):
                raise TypeError('buildPolisher should be a string')

            self.buildPolisher = settings['buildPolisher']
            plogging.debug("Build polisher: {}".format(self.buildPolisher))

        if 'defaults' in settings:
            if not isinstance(settings['defaults'], dict):
                raise TypeError('defaults should be a dictionary')

            plogging.debug("Default values:")
            for key in settings['defaults'].keys():
                self.defaults[key] = settings['defaults'][key]
                plogging.debug("- {}: {}".format(key, self.defaults[key]))

        if 'information' in settings:
            if isinstance(settings['information'], str):
                settings['information'] = \
                    settings['information'].strip('\n').split('\n')
            if not isinstance(settings['information'], list):
                raise TypeError('information should be a list')

            self.information = settings['information']

        if 'links' in settings:
            if not isinstance(settings['links'], dict):
                raise TypeError('links should be a dictionary')

            self.links = settings['links']

        if 'parameters' in settings:
            if not isinstance(settings['parameters'], dict):
                raise TypeError('parameters should be a dictionary')

            plogging.debug("Parameters:")
            for key in settings['parameters']:

                if key not in self.parameters:
                    self.parameters[key] = {}

                if 'information' not in settings['parameters'][key]:
                    raise ValueError("Parameter '{}' has no information"
                                     .format(key))
                self.parameters[key]['information'] = \
                    settings['parameters'][key]['information']

                if 'type' not in settings['parameters'][key]:
                    raise ValueError("Parameter '{}' has no type"
                                     .format(key))
                self.parameters[key]['type'] = \
                    settings['parameters'][key]['type']

                if 'default' not in settings['parameters'][key]:
                    plogging.warning("Parameter '{}' has no default value"
                                     .format(key))
                else:
                    self.parameters[key]['default'] = \
                        settings['parameters'][key]['default']
                    plogging.debug("- {}: {}".format(
                        key,
                        self.parameters[key]['default']))

        if 'polishers' in settings:
            if not isinstance(settings['polishers'], list):
                raise TypeError('polishers should be a list')

            plogging.debug("Polishers:")
            for item in settings['polishers']:
                key = list(item)[0]
                value = item[key]
                self.polishers.append(
                    PlumberyPolisher.from_shelf(key, value))
                plogging.debug("- {}".format(key))

        if 'safeMode' in settings:
            if settings['safeMode'] not in [True, False]:
                raise ValueError('safeMode should be either True or False')
            self.safeMode = settings['safeMode']

    def get_default(self, label, default=None):
        """
        Retrieves default settings

        :param label: the name of the settings to be retrieved
        :type label: ``str``

        :param default: the default value to return

        :return: the value set in fittings plan, or `None`
        :rtype: ``dict`` most often, or ``str`` or something else

        """

        if label in self.defaults:
            return self.defaults[label]

        return default

    def set_shared_user(self, user):
        """
        Changes the name used to access nodes remotely

        :param user: the user name to be used with ssh
        :type user: ``str``

        """

        self._sharedUser = user

    def get_shared_user(self):
        """
        Retrieves the name used to access nodes remotely

        :return: the user name to be used with ssh
        :rtype: ``str``

        This functions returns ``root`` until the member function
        ``set_shared_used()`` has been called.

        """

        if self._sharedUser is None:
            return 'root'

        return self._sharedUser

    def set_shared_secret(self, secret):
        """
        Changes the shared secret to be used with new nodes

        :param secret: the shared secret to be used with the API and with ssh
        :type secret: ``str``

        This function can be used to supplement the normal provision of
        the shared secret via the environment variable ``SHARED_SECRET``.

        """

        self._sharedSecret = secret

    def get_shared_secret(self):
        """
        Retrieves the secret that is communicated to new nodes during setup

        :return: the shared secret to be used with the API and with ssh
        :rtype: ``str``

        :raises: :class:`plumbery.PlumberyException`
            - if no shared secret can be found

        The shared secret is not put in the fittings plan, but is normally
        taken from the environment variable ``SHARED_SECRET``.

        Under Linux, you may want to edit ``~/.bash_profile`` like this::

            # password to access nodes remotely
            export SHARED_SECRET='*you really want to use a tricky password*'

        Alternatively, you can use the member function ``set_shared_secret()``
        to set this important attribute via code.

        """

        if self._sharedSecret is None:
            self._sharedSecret = os.getenv('SHARED_SECRET')
            if self._sharedSecret is None or len(self._sharedSecret) < 3:
                raise PlumberyException(
                    "Error: missing node password "
                    "in environment SHARED_SECRET")

        return self._sharedSecret

    def get_rsa_secret(self, id='rsa_private.pair'):
        """
        Returns a part of a RSA pair of keys

        :param id: name of the key
        :type id: ``str``

        """

        type = '.'.join([x for x in id.split('.')
                    if x in ('rsa_private', 'rsa_public')])

        name = '.'.join([x for x in id.split('.')
                    if x not in ('rsa_private', 'rsa_public')])

        id = type+'.'+name

        if id in self.secrets:
            return self.secrets[id]

        if id == 'rsa_private.local':
            raise LookupError("It is forbidden to use 'rsa_private.local'")

        if id == 'rsa_public.local':
            try:
                path = '~/.ssh/id_rsa.pub'

                with open(os.path.expanduser(path)) as stream:
                    plogging.info("- loading {} from {}".format(id, path))
                    text = stream.read().strip()
                    stream.close()
                    return text

            except IOError:
                plogging.error("- cannot load {} from {}".format(id, path))
                return ''

        if not HAS_CRYPTO:
            return None

        key = RSA.generate(2048)
        self.secrets['rsa_private.'+name] = key.exportKey('PEM')
        plogging.debug("- generating {}".format('rsa_private.'+name))

        pubkey = key.publickey()
        self.secrets['rsa_public.'+name] = pubkey.exportKey('OpenSSH')
        plogging.debug("- generating {}".format('rsa_public.'+name))

        self.save_secrets()
        return self.secrets[id]

    def get_secret(self, id='secret.random'):
        """
        Returns a secret

        :param id: name of this secret
        :type id: ``str``

        :return: a transient random secret
        :rtype: ``str``

        Random secrets can be used in scripts and in configuration files
        sent to nodes, for example to configure a database server.

        For this you would put ``{{ secret.random }}`` in your files and let
        plumbery provide a value for you.

        The `id` parameter designates one secret among several.

        By default this function builds a random string out of ASCII letters,
        digits, and a couple of punctuation letters, with 9 characters.

        If you put `.uuid` in the id, than the function ``uuid.uuid4()`` is
        called to generate a unique identifier of 36 letters.

        The `format` parameter specifies the kind of string that is expected:
        * 'sha1' - rather long string
        * 'md5' - rather long string too
        * 'sha256' - longest and most secure

        Some examples:

            {{ uuid.server1 }}
            {{ uuid.server2 }}
            {{ secret.sql_root }}
            {{ secret.redis.master.md5 }}
            {{ secret.redis.slave }}
            {{ secret.database357.sha1 }}

        In a nutshell, this function is giving you a lot of flexibility
        in the generation of secrets.

        """

        if id in self.secrets:
            return self.secrets[id]

        if id.startswith('uuid.') or id.endswith('.uuid'):
            secret = str(uuid.uuid4())

        elif id.startswith('http://') or id.startswith('https://'):
            plogging.debug('- fetching {}'.format(id))
            secret = requests.get(id).text

        else:
            secret = ''.join(random.choice(
                string.ascii_letters+string.digits+'-_!=')
                for i in range(9))

        if id.endswith('.sha256'):
            secret = hashlib.sha256(secret.encode('utf-8')).hexdigest()

        elif id.endswith('.md5'):
            secret = hashlib.md5(secret.encode('utf-8')).hexdigest()

        elif id.endswith('.sha1'):
            secret = hashlib.sha1(secret.encode('utf-8')).hexdigest()

        plogging.debug("- generating {}".format(id))
        self.secrets[id] = secret
        self.save_secrets()

        return secret

    def display_secrets(self):
        """
        Displays secrets attached to this fittings plan
        """

        plogging.info("Showing secrets")

        if len(self.secrets.keys()) < 1:
            plogging.info("- no secret found")

        for key in sorted(self.secrets):
            plogging.info("- {}: {}".format(key, self.secrets[key]))

    def save_secrets(self, plan=None):
        """
        Saves secrets attached to this fittings plan

        :param plan: the file that contains fittings plan
        :type plan: ``str`` or ``file`` or ``dict`` or ``list`` of ``dict``

        """

        if plan:
            secretsId = hashlib.md5(plan.encode('utf-8')).hexdigest()

        elif self.secretsId:
            secretsId = self.secretsId

        else:
            return

        secretsFile = secretsId+'.secrets'

        try:
            handle = open(secretsFile, 'w')
            for id in self.secrets:
                handle.write("{}: '{}'\n".format(
                    id, self.secrets[id].replace('\n', '\\n')))
            handle.close()

        except IOError:
            plogging.warning("Unable to save secrets")
            plogging.debug("- cannot write to file '{}'".format(
                secretsFile))

    def load_secrets(self, plan=None):
        """
        Loads secrets attached to this fittings plan

        :param plan: the file that contains fittings plan
        :type plan: ``str`` or ``file`` or ``dict`` or ``list`` of ``dict``

        """

        if plan:
            secretsId = hashlib.md5(plan.encode('utf-8')).hexdigest()

        elif self.secretsId:
            secretsId = self.secretsId

        else:
            return

        secretsFile = secretsId+'.secrets'
        plogging.debug("Loading secrets from '{}'".format(secretsFile))

        if os.path.isfile(secretsFile):
            try:
                handle = open(secretsFile, 'r')
                self.secrets = yaml.load(handle)
                handle.close()

                plogging.debug("- found {} secrets".format(
                    len(self.secrets)))

            except IOError:
                plogging.debug("- unable to load secrets")

    def forget_secrets(self, plan=None):
        """
        Destroys secrets attached to this fittings plan
        """

        if plan:
            secretsId = hashlib.md5(plan.encode('utf-8')).hexdigest()

        elif self.secretsId:
            secretsId = self.secretsId

        else:
            return

        secretsFile = secretsId+'.secrets'

        if self.safeMode:
            plogging.info("Secrets cannot be forgotten in safe mode")

        self.secrets = {}

        if os.path.isfile(secretsFile):
            try:
                os.remove(secretsFile)

            except IOError:
                plogging.warning("Unable to forget secrets")
                plogging.debug("- cannot delete file '{}'".format(
                    secretsFile))

    def set_user_name(self, name):
        """
        Changes the name used to authenticate to the API

        :param name: the user name to be used with the driver
        :type name: ``str``

        This function can be used to supplement the normal provision of
        a user name via the environment variable ``MCP_USERNAME``.

        """

        self._userName = name

    def get_user_name(self):
        """
        Retrieves user name to authenticate to the API

        :return: the user name to be used with the driver
        :rtype: ``str``

        :raises: :class:`plumbery.PlumberyException`
            - if no user name can be found

        The user name is not put in the fittings plan, but is normally taken
        from the environment variable ``MCP_USERNAME``.

        Under Linux, you may want to edit ``~/.bash_profile`` like this::

            # credentials to access cloud resources from Dimension Data
            export MCP_USERNAME='foo.bar'
            export MCP_PASSWORD='WhatsUpDoc'

        """

        if self._userName is None:
            self._userName = os.getenv('MCP_USERNAME')
            if self._userName is None or len(self._userName) < 3:
                raise PlumberyException(
                    "Error: missing credentials in environment MCP_USERNAME")

        return self._userName

    def set_user_password(self, password):
        """
        Changes the password used to authenticate to the API

        :param password: the user password to be used with the driver
        :type password: ``str``

        This function can be used to supplement the normal provision of
        a user password via the environment variable ``MCP_PASSWORD``.

        """

        self._userPassword = password

    def get_user_password(self):
        """
        Retrieves user password to authenticate to the API

        :return: the user password to be used with the driver
        :rtype: ``str``

        :raises: :class:`plumbery.PlumberyException`
            - if no user password can be found

        The user password is not put in the fittings plan, but is normally
        taken from the environment variable ``MCP_PASSWORD``.

        Under Linux, you may want to edit ``~/.bash_profile`` like this::

            # credentials to access cloud resources from Dimension Data
            export MCP_USERNAME='foo.bar'
            export MCP_PASSWORD='WhatsUpDoc'

        """

        if self._userPassword is None:
            self._userPassword = os.getenv('MCP_PASSWORD')
            if self._userPassword is None or len(self._userPassword) < 3:
                raise PlumberyException(
                    "Error: missing credentials in environment MCP_PASSWORD")

        return self._userPassword

    def add_facility(self, facility):
        """
        Extends the scope of this plumbing engine

        :param facility: description of an additional facility
        :type facility: ``dict`` or :class:`plumbery.PlumberyFacility`

        """

        if isinstance(facility, dict):
            facility = PlumberyFacility(self, facility)

        plogging.debug("Adding facility %s" % facility)
        for key in facility.settings:
            plogging.debug("- {}: {}".format(key, facility.settings[key]))

        self.facilities.append(facility)

    def list_facility(self, location=None):
        """
        Retrieves facilities by their location

        :param location: the target location, e.g., 'EU6'
        :type location: ``str`` or ``list`` of ``str``

        :return: the list of matching facilities
        :rtype: ``list`` of :class:`plumbery.PlumberyFacility` or ``[]``

        Examples::

            >>>engine.list_facility(location='EU6')
            ...

            >>>engine.list_facility(location='EU6 NA9')
            ...

            >>>engine.list_facility(location=['EU6', 'NA9'])
            ...

        """
        if location is None:
            return self.facilities

        if isinstance(location, str):
            location = location.split(' ')

        matches = []

        for item in location:
            if isinstance(item, PlumberyFacility):
                matches.append(item)

        for facility in self.facilities:
            if (facility.get_setting('locationId') in location or
                    facility.get_setting('apiHost') in location):
                matches.append(facility)

        return matches

    def document_elapsed(self, elapsed=None, www=None):
        """
        Reflects the amount of work done by plumbery

        :param elapsed: number of second spent in plumbing
        :type elapsed: ``int``

        :param www: number of second spent in the cloud
        :type www: ``int``

        """

        if elapsed is None:
            elapsed = int(time.clock() - self.c0 + 1)

        if www is None:
            www = int(time.time() - self.t0 + 1)

        www -= elapsed

        if elapsed < 2:
            elapsed = "in a blink"

        elif elapsed < 120:
            elapsed = "for {} seconds".format(elapsed)

        elif elapsed < 7200:
            elapsed = int(elapsed/60)
            elapsed = "for {} minutes".format(elapsed)

        elif elapsed < 86400:
            elapsed = int(elapsed/60)
            minutes = elapsed % 60
            hours = int(elapsed / 60)
            elapsed = "for {} hours and {} minutes".format(hours, minutes)

        if www < 120:
            www = "for {} seconds".format(www)

        elif www < 7200:
            www = int(www/60)
            www = "for {} minutes".format(www)

        elif www < 86400:
            www = int(www/60)
            minutes = www % 60
            hours = int(www/60)
            www = "for {} hours and {} minutes".format(hours, minutes)

        return "Worked for you {} locally, and {} in the cloud"     \
               .format(elapsed, www)

    def do(self, action, blueprints=None, facilities=None):
        """
        Applies an action to multiple blueprints at multiple locations

        :param action: 'deploy', 'dispose', etc., or a polisher name
        :type action: ``str``

        :param blueprints: a list of blueprints
        :type blueprints: ``list`` of ``str``, or None

        :param facilities: a list of facilities
        :type factilities: ``list`` of ``str``, or None

        """

        if action == 'build':
            if blueprints is None:
                self.build_all_blueprints(facilities)
            else:
                self.build_blueprint(blueprints, facilities)

        elif action == 'deploy':
            if blueprints is None:
                self.build_all_blueprints(facilities)
                self.start_all_blueprints(facilities)
                self.polish_all_blueprints(filter='prepare',
                                           facilities=facilities)
                self.polish_all_blueprints(filter='information',
                                           facilities=facilities)
            else:
                self.build_blueprint(blueprints, facilities)
                self.start_blueprint(blueprints, facilities)
                self.polish_blueprint(blueprints,
                                      filter='prepare',
                                      facilities=facilities)
                self.polish_blueprint(blueprints,
                                      filter='information',
                                      facilities=facilities)

        elif action == 'destroy':
            if blueprints is None:
                self.destroy_all_blueprints(facilities)
            else:
                self.destroy_blueprint(blueprints, facilities)

        elif action == 'dispose':
            if blueprints is None:
                self.stop_all_blueprints(facilities)
                self.destroy_all_blueprints(facilities)
            else:
                self.stop_blueprint(blueprints, facilities)
                self.destroy_blueprint(blueprints, facilities)

        elif action in ('polish', 'finalize', 'finalise'):
            if blueprints is None:
                self.polish_all_blueprints(filter=None,
                                           facilities=facilities)
            else:
                self.polish_blueprint(blueprints,
                                      filter=None,
                                      facilities=facilities)

        elif action == 'refresh':
            if blueprints is None:
                self.stop_all_blueprints(facilities)
                self.wipe_all_blueprints(facilities)
                time.sleep(30)
                self.build_all_blueprints(facilities)
                self.start_all_blueprints(facilities)
                self.polish_all_blueprints(filter='prepare',
                                           facilities=facilities)
                self.polish_all_blueprints(filter='information',
                                           facilities=facilities)
            else:
                self.stop_blueprint(blueprints, facilities)
                self.wipe_blueprint(blueprints, facilities)
                time.sleep(30)
                self.build_blueprint(blueprints, facilities)
                self.start_blueprint(blueprints, facilities)
                self.polish_blueprint(blueprints,
                                      filter='prepare',
                                      facilities=facilities)
                self.polish_blueprint(blueprints,
                                      filter='information',
                                      facilities=facilities)

        elif action == 'secrets':
            self.display_secrets()

        elif action == 'start':
            if blueprints is None:
                self.start_all_blueprints(facilities)
            else:
                self.start_blueprint(blueprints, facilities)

        elif action == 'stop':
            if blueprints is None:
                self.stop_all_blueprints(facilities)
            else:
                self.stop_blueprint(blueprints, facilities)

        elif action == 'wipe':
            if blueprints is None:
                self.wipe_all_blueprints(facilities)
            else:
                self.wipe_blueprint(blueprints, facilities)

        elif action == 'graph':
            raise NotImplementedError("Wait for 1.1.0")

        else:
            if blueprints is None:
                self.polish_all_blueprints(filter=action,
                                           facilities=facilities)
            else:
                self.polish_blueprint(blueprints,
                                      filter=action,
                                      facilities=facilities)

    def process_all_blueprints(self, action, facilities=None):
        """
        Handles elements described in the fittings plan

        :param action: the action to perform, e.g., 'start'
        :type action: ``str`` or :class:`plumbery.PlumberyAction`

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function triggers the provided action across facilities.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        """

        if isinstance(action, str):
            action = PlumberyActionLoader.from_shelf(action)

        action.ignite(self)

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.process_all_blueprints(action)

        action.reap()

    def process_blueprint(self, action, names, facilities=None):
        """
        Handles elements for one blueprint of the fittings plan

        :param action: the action to perform, e.g., 'start'
        :type action: ``str`` or :class:`plumbery.PlumberyAction`

        :param names: the name(s) of the targeted blueprint(s)
        :type names: ``str`` or ``list`` of ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function triggers the provided action across facilities.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        """

        if isinstance(action, str):
            action = PlumberyActionLoader.from_shelf(action)

        action.ignite(self)

        if isinstance(names, list):
            names = ' '.join(names)

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.process_blueprint(action, names)

        action.reap()

    def build_all_blueprints(self, facilities=None):
        """
        Builds all blueprints described in fittings plan

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to build all blueprints there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Examples::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').build_all_blueprints()

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').build_all_blueprints('EU6 NA9')

        """

        all = self.get_default('blueprints', None)
        if all is None:
            plogging.info("Building all blueprints")
        else:
            plogging.info("Building '{}'".format("', '".join(all.split(' '))))

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.build_all_blueprints()

        self.polish_all_blueprints(filter=self.buildPolisher,
                                   facilities=facilities)

    def build_blueprint(self, names, facilities=None):
        """
        Builds named blueprint from fittings plan

        :param names: the name(s) of the blueprint(s) to deploy
        :type names: ``str`` or ``list`` of ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to build one single blueprint there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').build_blueprints('sql')

        """

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        plogging.info("Building blueprint '{}'".format(label))

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.build_blueprint(names)

        self.polish_blueprint(names=names,
                              filter=self.buildPolisher,
                              facilities=facilities)

    def start_all_blueprints(self, facilities=None):
        """
        Starts all nodes described in the fittings plan

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to start all nodes there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        This function has no effect on nodes that are already up and running.

        """

        plogging.info("Starting nodes from all blueprints")

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.start_all_blueprints()

    def start_blueprint(self, names, facilities=None):
        """
        Starts nodes of one blueprint of the fittings plan

        :param names: the name(s) of the blueprint(s) to start
        :type names: ``str`` or ``list`` of ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to start nodes from some blueprint.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        This function has no effect on nodes that are already up and running.

        """

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        plogging.info("Starting nodes from blueprint '{}'".format(label))

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.start_blueprint(names)

    def polish_all_blueprints(self, filter=None, facilities=None):
        """
        Walks all resources and polishes them

        :param filter: the name of a single polisher to apply. If this
            parameter is missing, all polishers declared in the fittings plan
            will be applied
        :type filter: ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to apply polishers there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').polish_all_blueprints()

        """

        polishers = PlumberyPolisher.filter(self.polishers, filter)

        if len(polishers) < 1:
            return False

        plogging.info("Polishing all blueprints")

        for polisher in polishers:
            polisher.go(self)

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.polish_all_blueprints(polishers)

        for polisher in polishers:
            polisher.reap()

    def polish_blueprint(self, names, filter=None, facilities=None):
        """
        Walks resources from the target blueprint and polishes them

        :param names: the name(s) of the blueprint(s) to polish
        :type names: ``str`` or ``list`` of ``str``

        :param filter: the name of a single polisher to apply. If this
            parameter is missing, all polishers declared in the fittings plan
            will be applied
        :type filter: ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to apply one polisher to one blueprint.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').polish_blueprint('sql')

        """

        polishers = PlumberyPolisher.filter(self.polishers, filter)

        if len(polishers) < 1:
            plogging.debug('No polisher has been found')
            return

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        plogging.info("Polishing blueprint '{}'".format(label))

        for polisher in polishers:
            polisher.go(self)

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            for polisher in polishers:
                polisher.move_to(facility)
            facility.polish_blueprint(names, polishers)

        for polisher in polishers:
            polisher.reap()

    def stop_all_blueprints(self, facilities=None):
        """
        Stops all nodes of the fittings plan

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to stop all nodes there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        This function has no effect on nodes that are already stopped.

        """

        plogging.info("Stopping nodes from all blueprints")

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.stop_all_blueprints()

    def stop_blueprint(self, names, facilities=None):
        """
        Stops nodes of one blueprint of the fittings plan

        :param names: the name(s) of the blueprint(s) to stop
        :type names: ``str`` or ``list`` of ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to stop nodes from some blueprint.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        This function has no effect on nodes that are already stopped.

        """

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        plogging.info("Stopping nodes from blueprint '{}'".format(label))

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.stop_blueprint(names)

    def wipe_all_blueprints(self, facilities=None):
        """
        Destroys all nodes from fittings plan

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to destroy all nodes there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        plogging.info("Wiping all blueprints")

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.wipe_all_blueprints()

    def wipe_blueprint(self, names, facilities=None):
        """
        Destroys nodes for one or several blueprint(s) of the fittings plan

        :param names: the name(s) of the blueprint(s) to destroy
        :type names: ``str`` or ``list`` of ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to destroy nodes from one blueprint.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        plogging.info("Wiping blueprint '{}'".format(label))

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.wipe_blueprint(names)

    def destroy_all_blueprints(self, facilities=None):
        """
        Destroys all blueprints from fittings plan

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to destroy all blueprints there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        plogging.info("Destroying all blueprints")

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.destroy_all_blueprints()

    def destroy_blueprint(self, names, facilities=None):
        """
        Destroys one or several blueprint(s) from fittings plan

        :param names: the name(s) of the blueprint(s) to destroy
        :type names: ``str`` or ``list`` of ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to destroy one single blueprint.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        plogging.info("Destroying blueprint '{}'".format(label))

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.destroy_blueprint(names)

    def get_compute_driver(self, region=None, host=None):
        """
        Loads a compute driver from Apache Libcloud

        """

        driver = get_compute_driver(ComputeProvider.DIMENSIONDATA)

        instance = driver(
            key=self.get_user_name(),
            secret=self.get_user_password(),
            region=region,
            host=host)

        return instance

    def get_balancer_driver(self, region=None, host=None):
        """
        Loads a load balancer driver from Apache Libcloud

        """

        driver = get_balancer_driver(BalancerProvider.DIMENSIONDATA)

        instance = driver(
            key=self.get_user_name(),
            secret=self.get_user_password(),
            region=region,
            host=host)
        return instance

    def get_backup_driver(self, region=None, host=None):
        """
        Loads a backup driver from Apache Libcloud

        """

        driver = get_backup_driver(BackupProvider.DIMENSIONDATA)

        instance = driver(
            key=self.get_user_name(),
            secret=self.get_user_password(),
            region=region,
            host=host)
        return instance

    def lookup(self, token):
        """
        Retrieves the value attached to a token

        :param token: the token, e.g., 'sqlMaster.secret'
        :type token: ``str``

        :return: the value attached to this token, or `None`

        """

        if token == 'plumbery.version':
            return __version__

        if token == 'shared.user':
            return self.get_shared_user()

        if token == 'shared.secret':
            return self.get_shared_secret()

        if token in ('credentials.name', 'name.credentials'):
            return self.get_user_name()

        if token in ('credentials.password', 'password.credentials'):
            return self.get_user_password()

        if token.startswith('parameter.'):
            return self.get_parameter(token)

        if token.startswith('rsa_public.'):
            return self.get_rsa_secret(token)
        if token.endswith('.rsa_public'):
            return self.get_rsa_secret(token)
        if token.startswith('rsa_private.'):
            return self.get_rsa_secret(token)
        if token.endswith('.rsa_private'):
            return self.get_rsa_secret(token)

        if token.startswith('secret.'):
            return self.get_secret(token)
        if token.endswith('.secret'):
            return self.get_secret(token)

        if token.startswith('uuid.'):
            return self.get_secret(token)
        if token.endswith('.uuid'):
            return self.get_secret(token)

        if token.startswith('http://') or token.startswith('https://'):
            return self.get_secret(token)

        return None
