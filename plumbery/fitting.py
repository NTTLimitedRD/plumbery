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

from plumbery.plogging import plogging

__all__ = ['PlumberyFitting', 'PlumberyFittingLoader']


class PlumberyFitting(object):
    """
    Represents some fitting

    :param engine: the automate that is coordinating
            plumbing activities at multiple facilities
    :type engine: :class:`plumbery.PlumberyEngine`

    :param facility: the place that is making a context for this fitting
    :type facility: :class:`plumbery.PlumberyFacility`

    Fittings are representation of cloud services, such as 'domain' or
    'node'. They are provided with settings that should be parsed and checked.
    A `ValueError` should be raised in case of invalid settings.

    """

    def __init__(self, engine, facility):
        self.engine = engine
        self.facility = facility

    def parse(self, settings):
        """
        Parses and checks settings

        :param settings: specific settings for this fittings
        :type settings: ``dict``

        This function raises a `ValueError` if invalid settings are provided.
        """

        raise NotImplementedError()

    def do(self, action, parameters=None):
        """
        Performs some action

        :param action: the action to perform
        :type action: ``str``

        :param parameters: the additional parameters, if any
        :type parameters: ``dict``

        This function dispatches the action to the member function of the
        same name. For example, ``fittings.do('start')`` will execute
        ``fittings.do_start()``.
        """

        method = getattr(self, 'do_'+action, None)
        if callable(method):
            return method(parameters)
        return True

class PlumberyFittingLoader(object):
    """
    Loads and set a fitting classe dynamically

    You can create fittings of your own, or use fittings from other
    persons. All fittings have to be placed in the directory
    ``plumbery/fittings``. Each fitting should be put in a separate
    python file, and define a class that repeats the file name. For example
    the file::

        plumbery/fittings/domain.py

    should contain::

        class DomainFitting(PlumberyFitting):
        ...

    Once this is done properly, plumbery will be able to parse related
    directives, and to process actions accordingly.

    """

    @classmethod
    def from_shelf(cls, label, engine, facility, settings={}):
        """
        Picks up fitting from the shelf

        :param label: name of fitting to use, e.g., ``domain``
        :type label: ``str``

        :param settings: specific settings for this fitting
        :type param: ``dict``

        :param engine: the automate that is coordinating
                plumbing activities at multiple facilities
        :type engine: :class:`plumbery.PlumberyEngine`

        :param facility: the place that is making a context for this fitting
        :type facility: :class:`plumbery.PlumberyFacility`

        :return: instance of fitting ready to use
        :rtype: :class:`plumbery.PlumberyFitting`

        """

        moduleName = 'plumbery.fittings.' + label
        fittingsName = label.capitalize() + 'Fitting'
        try:

            plogging.debug("Importing '{}'".format(moduleName))
            fittingsModule = __import__(
                moduleName,
                globals(),
                locals(),
                [fittingsName])

            plogging.debug("Instantiating '{}'".format(fittingsName))
            fittingsClass = getattr(fittingsModule, fittingsName)
            if settings is None:
                settings = {}
            fitting = fittingsClass(engine, facility)
            fitting.parse(settings)
            fitting.label = label
            return fitting

        except ImportError as feedback:
            plogging.debug("Unable to find module '{}'".format(moduleName))
            raise

        except TypeError as feedback:
            plogging.debug("Invalid settings for '{}'".format(moduleName))
            raise

        except ValueError as feedback:
            plogging.debug("Invalid settings for '{}'".format(moduleName))
            raise

        except Exception as feedback:
            plogging.debug("Unable to import '{}' from '{}'".format(
                fittingsName, moduleName))
            raise

