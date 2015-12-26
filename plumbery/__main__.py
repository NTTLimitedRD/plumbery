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

import argparse
import logging
import sys

from plumbery.engine import PlumberyEngine
from plumbery.exception import PlumberyException
from plumbery import __version__


def main(args=[], engine=None):
    """
    Runs plumbery from the command line

    Example::

        $ python -m plumbery fittings.yaml build web

    In this example, plumbery loads fittings plan from ``fittings.yaml``, then
    it builds the blueprint named ``web``.

    If no blueprint is mentioned, then plumbery looks at all blueprint
    definitions in the fittings plan. In other terms, the following command
    builds the entire fittings plan, eventually across multiple facilities::

        $ python -m plumbery fittings.yaml build

    Of course, plumbery can be invoked through the entire life cycle of your
    fittings::

        $ python -m plumbery fittings.yaml build
        $ python -m plumbery fittings.yaml start
        $ python -m plumbery fittings.yaml polish

        ... nodes are up and running here ...

        $ python -m plumbery fittings.yaml stop
        $ python -m plumbery fittings.yaml destroy

    To focus at a single location, put the character '@' followed by the id.
    For example, to build fittings only at 'NA12' you would type::

        $ python -m plumbery fittings.yaml build @NA12

    To apply a polisher just mention its name on the command line. For example,
    if fittings plan has a blueprint for nodes running Docker, then you may
    use following statements to bootstrap each node::

        $ python -m plumbery fittings.yaml build docker
        $ python -m plumbery fittings.yaml start docker
        $ python -m plumbery fittings.yaml rub docker

        ... Docker is up and running at multiple nodes ...

    If you create a new polisher and put it in the directory
    ``plumbery\polishers``, then it will become automatically available::

        $ python -m plumbery fittings.yaml my_special_stuff

    To get some help, you can type::

        $ python -m plumbery -h

    """

    parser = argparse.ArgumentParser(
                prog='plumbery',
                description='Plumbing infrastructure with Apache Libcloud.')

    parser.add_argument(
                'fittings',
                nargs=1,
                help='File that is containing fittings plan')

    parser.add_argument(
                'action',
                nargs=1,
                help="Either 'build', 'start', 'polish', 'stop', 'destroy'"
                    " or the name of a polisher, e.g., 'ansible', 'rub', etc.")

    parser.add_argument(
                'tokens',
                nargs='*',
                help="One blueprint, or several, e.g., 'web' or 'web sql'."
                    'If omitted, all blueprints will be considered. '
                    "Zero or more locations, e.g., 'NA12'. "
                    'If omitted, all locations will be considered.',
                default=None)

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
                '-d', '--debug',
                help='Log as much information as possible',
                action='store_true')

    group.add_argument(
                '-q', '--quiet',
                help='Silent mode, log only warnings and errors',
                action='store_true')

    parser.add_argument(
                '-v', '--version',
                action='version',
                version='%(prog)s ' + __version__)

    args = parser.parse_args(args)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    else:
        logging.getLogger().setLevel(logging.INFO)

    if 'version' in args:
        print(args.version)

    if engine is None:
        try:
            engine = PlumberyEngine(args.fittings[0])

        except Exception as feedback:
            logging.info("{}: error: cannot read fittings plan from '{}'"
                  .format('plumbery', args.fittings[0]))
            logging.debug(str(feedback))
            sys.exit(2)

    blueprints = []
    facilities = []
    for token in args.tokens:
        if token[0] == '@':
            facilities.append(token[1:])
        else:
            blueprints.append(token)
    logging.debug('blueprints: '+' '.join(blueprints))
    if len(facilities) < 1:
        facilities = None
    else:
        logging.debug('facilities: '+' '.join(facilities))

    verb = args.action[0].lower()
    if verb == 'build':
        if len(blueprints) < 1:
            engine.build_all_blueprints(facilities)
        else:
            engine.build_blueprint(blueprints, facilities)

    elif verb == 'start':
        if len(blueprints) < 1:
            engine.start_all_nodes(facilities)
        else:
            engine.start_nodes(blueprints, facilities)

    elif verb == 'polish':
        if len(blueprints) < 1:
            engine.polish_all_blueprints(filter=None, facilities=facilities)
        else:
            engine.polish_blueprint(blueprints, facilities)

    elif verb == 'stop':
        if len(blueprints) < 1:
            engine.stop_all_nodes(facilities)
        else:
            engine.stop_nodes(blueprints, facilities)

    elif verb == 'destroy':
        if len(blueprints) < 1:
            engine.destroy_all_blueprints(facilities)
        else:
            engine.destroy_blueprint(blueprints, facilities)

    else:
        try:
            if len(blueprints) < 1:
                polished = engine.polish_all_blueprints(filter=verb,
                                                        facilities=facilities)
            else:
                polished = engine.polish_blueprint(blueprints,
                                                   filter=verb,
                                                   facilities=facilities)
        except PlumberyException as feedback:
            polished = False

        if not polished:
            logging.getLogger().setLevel(logging.INFO)
            print("{}: error: unrecognised action '{}'"
                  .format('plumbery', verb))
            parser.print_help()
            sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])
