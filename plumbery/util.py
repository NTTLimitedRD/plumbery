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

import time
from functools import wraps

from plumbery.plogging import plogging


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=plogging):
    """
    Retries calling the decorated function using an exponential backoff.

    http://thecodeship.com/patterns/guide-to-python-function-decorators/

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple

    :param tries: number of times to try (not retry) before giving up
    :type tries: int

    :param delay: initial delay between retries in seconds
    :type delay: int

    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int

    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance

    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg1 = "{}".format(str(e))
                    msg2 = "- retrying in {} seconds...".format(mdelay)
                    if logger:
                        logger.warning(msg1)
                        logger.warning(msg2)
                    else:
                        print(msg1)
                        print(msg2)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


class PlumberyParameters(object):
    """
    Manages parameters

    :param dictionary: pre-populated set of named parameters
    :type dictionary: ``dict``

    """

    def __init__(self, dictionary=None):

        if dictionary is None:
            self.dictionary = {}
        elif not isinstance(dictionary, dict):
            raise TypeError("invalid type for parameter 'dictionary'")
        else:
            self.dictionary = dictionary

    def set(self, parameter, value):
        """
        Remembers the value of a parameter

        :param parameter: the parameter
        :type parameter: ``str``

        :param value: the value
        :type value: any

        """

        self.dictionary[parameter] = value

    def get(self, parameter, default=None):
        """
        Retrieves the value of a parameter

        :param parameter: the parameter
        :type parameter: ``str``

        :param default: default value to return if the parameter has not been set
        :type default: any

        :return: the value of this parameter, or None

        """

        if parameter in self.dictionary:
            return self.dictionary[parameter]

        return default

