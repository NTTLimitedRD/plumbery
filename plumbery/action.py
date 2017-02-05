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

import os

from plumbery.plogging import plogging
from plumbery.util import PlumberyParameters

__all__ = ['PlumberyAction', 'PlumberyActionLoader']


class PlumberyAction(object):
    """
    Performs some action on elements described in the fittings plan

    :param parameters: specific parameters for this action
    :type parameters: :class:`PlumberyParameters` or ``dict``

    An action is an imperative given to plumbery, such as
    'build', 'stop' or 'dispose'. It is commonly expressed as a verb, but
    not always. For example, 'information' asks plumbery to describe
    elements of the fittings plan.

    The engine provides a simple way to trigger an action. For example::

        from plumbery.engine import PlumberyEngine
        PlumberyEngine('fittings.yaml').do('start')

    """

    def __init__(self, parameters=PlumberyParameters()):
        if parameters is None:
            parameters = PlumberyParameters()
        elif not isinstance(parameters, PlumberyParameters):
            raise TypeError("'parameters' should have type PlumberyParameters")

        self.parameters = parameters

    def get_banner(self, location):
        """
        Informs the end-user
        """

        return "Plumbing at {}".format(location)

    def get_label(self):
        """
        Provides the label of the action

        :return: The label, such as 'build' or 'stop'
        :rtype: ``str``

        """

        return self.label

    def get_parameter(self, name, default=None):
        """
        Provides settings for this action

        :param name: the parameter
        :type name: ``str``

        :param default: returned if the parameter has not been set
        :type default: any

        :return: the value of this parameter, or None

        """

        return self.parameters.get(name, default)

    def begin(self, engine):
        """
        Binds to a plumbery engine

        :param engine: the plumbery engine itself
        :type engine: :class:`plumbery.PlumberyEngine`

        This function is called once, before all others.
        You can override it for any specific initialisation.

        """

        self.engine = engine

        plogging.info("Using '{}'".format(self.get_label()))

    def enter(self, facility):
        """
        Enters a facility to process blueprints there

        :param facility: a targeted facility
        :type facility: :class:`plumbery.PlumberyFacility`

        This function is called once for each facility that is visited during
        the process. You can override it for any specific
        initialisation that you would require.

        """

        self.facility = facility

        plogging.info(self.get_banner(facility))

    def process(self, blueprint):
        """
        Prepares one blueprint

        :param blueprint: a targeted blueprint
        :type blueprint: :class:`plumbery.PlumberyBlueprint`

        This is where the hard work is done. You have to override this
        function in your own action.

        """

        pass

    def quit(self):
        """"
        Quits a facility

        This function can be useful for some cleaning after processing.
        """

        pass

    def end(self):
        """
        Reaps the outcome of all this action

        This function is called once, at the very end of the process. You
        can override it for any specific closure that you would require.

        """

        pass


class PlumberyActionLoader(object):
    """
    Loads action classes dynamically

    Plumbery is coming with a number of pre-defined actions that, together,
    cover the entire life cycle of virtual assets in the cloud.

    You can create actions of your own, or use actions from other
    persons. All actions have to be placed in the directory
    ``plumbery/actions``. Each action should be put in a separate
    python file, and define a class that repeats the file name. For example
    the file::

        plumbery/actions/configure.py

    should contain::

        class ConfigureAction(PlumberyAction):
        ...

    Once this is done properly, you can use the action from the command line,
    or via the API.

    Also, you can pass any parameters that the action would require.

    Example of configuration of ``fittings.yaml``::

        ---
        safeMode: False
        actions:
          - configure:
              file: nodes.yaml
          - ansible:
              file: inventory.yaml
        ---
        # Frankfurt in Europe
        locationId: EU6
        regionId: dd-eu
        ...

    """

    @classmethod
    def load_all(cls, settings={}):

        actions = {}

        there = os.path.abspath(os.path.dirname(__file__))+'/actions'
        for unused1, unused2, files in os.walk(there):
            plogging.debug("Loading actions from %s", there)

            for file in files:
                label, extension = file.split('.', 1)
                if len(label) < 2:
                    continue
                if label[0] in ('-', '_', '~'):
                    continue
                if extension == 'py':
                    plogging.debug("Loading action %s", file)

                    if label in settings:
                        parameters = settings[ label ]
                    else:
                        parameters = {}

                    actions[ label ] = PlumberyActionLoader.load(label,
                                                                 parameters)

        return actions


    @classmethod
    def load(cls, label, parameters=PlumberyParameters()):
        """
        Picks up an action from the shelf

        :param label: name of the action to use, e.g., ``inventory``
        :type label: ``str``

        :param parameters: specific parameters for this action
        :type parameters: ``dict``

        :return: instance of a action ready to use
        :rtype: :class:`plumbery.PlumberyAction`

        """

        moduleName = 'plumbery.actions.' + label
        actionName = label.capitalize() + 'Action'
        try:

            plogging.debug("Importing '{}'".format(moduleName))
            actionModule = __import__(
                moduleName,
                globals(),
                locals(),
                [actionName])

            plogging.debug("Instantiating '{}'".format(actionName))
            actionClass = getattr(actionModule, actionName)
            if parameters is None:
                parameters = PlumberyParameters()
            elif isinstance(parameters, dict):
                parameters = PlumberyParameters(parameters)
            action = actionClass(parameters)
            action.label = label
            return action

        except ImportError as feedback:
            plogging.debug("Unable to find module '{}'".format(moduleName))
            raise

        except TypeError as feedback:
            plogging.debug("Invalid parameters for '{}'".format(moduleName))
            raise

        except ValueError as feedback:
            plogging.debug("Invalid parameters for '{}'".format(moduleName))
            raise

        except Exception as feedback:
            plogging.debug("Unable to import '{}' from '{}'".format(
                actionName, moduleName))
            raise
