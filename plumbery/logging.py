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

# this is required because we called this file logging.py
#
from __future__ import absolute_import

import logging
import colorlog


class PlumberyLogging(object):

    def __init__(self):

        # logging to console
        #
        handler = colorlog.StreamHandler()
        formatter = colorlog.ColoredFormatter(
            "%(asctime)-2s %(log_color)s%(message)s",
            datefmt='%H:%M:%S',
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )
        handler.setFormatter(formatter)
        logging.getLogger('').addHandler(handler)

        self.reset()

    def reset(self):
        self.errors = 0

    def foundErrors(self):
        return self.errors > 0

    def debug(self, *args):
        logging.debug(*args)

    def info(self, *args):
        logging.info(*args)

    def warning(self, *args):
        logging.warning(*args)

    def error(self, *args):
        logging.error(*args)
        self.errors += 1

    def critical(self, *args):
        logging.critical(*args)
        self.errors += 1

    def getEffectiveLevel(self):
        return logging.getLogger('').getEffectiveLevel()

    def setLevel(self, level):
        logging.getLogger('').setLevel(level)


plogging = PlumberyLogging()
