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
Runs plumbery from the command line

Example::

    $ python -m plumbery fittings.yaml build web


To get some help, you can type::

    $ python -m plumbery -h

"""

import sys
import argparse

from plumbery.engine import PlumberyEngine
from plumbery import __version__

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
                'blueprint',
                nargs='?',
                help='Name of the selected blueprint. '
                    'If omitted, all blueprints will be considered',
                default=None)

parser.add_argument(
                '-v', '--version',
                action='version',
                version='%(prog)s ' + __version__)

args = parser.parse_args()

if 'version' in args:
    print(args.version)

engine = PlumberyEngine(args.fittings[0])

verb = args.action[0].lower()
if verb == 'build':
    if args.blueprint is None:
        engine.build_all_blueprints()
    else:
        engine.build_blueprint(args.blueprint)

elif verb == 'start':
    if args.blueprint is None:
        engine.start_all_nodes()
    else:
        engine.start_nodes(args.blueprint)

elif verb == 'polish':
    if args.blueprint is None:
        engine.polish_all_blueprints()
    else:
        engine.polish_blueprint(args.blueprint)

elif verb == 'stop':
    if args.blueprint is None:
        engine.stop_all_nodes()
    else:
        engine.stop_nodes(args.blueprint)

elif verb == 'destroy':
    if args.blueprint is None:
        engine.destroy_all_blueprints()
    else:
        engine.destroy_blueprint(args.blueprint)

else:
    try:
        if args.blueprint is None:
            polished = engine.polish_all_blueprints(verb)
        else:
            polished = engine.polish_blueprint(args.blueprint, verb)
    except:
        polished = False

    if not polished:
        print("{}: error: unrecognised action '{}'"
              .format('plumbery', args.action[0]))
        parser.print_help()
        sys.exit(2)
