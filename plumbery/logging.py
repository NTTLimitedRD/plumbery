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
import logging
import colorlog

loggers = {}


class PlumberyLogFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """
    def filter(self, record):
        return True


def setup_logging(engine=None):
    global loggers
    if loggers.get('plumbery'):
        return loggers.get('plumbery')
    else:
        formatter = colorlog.ColoredFormatter(
            "%(asctime)-2s %(module)s %(funcName)-6s %(log_color)s%(message)s",
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
        log = logging.getLogger('plumbery')
        log.setLevel(logging.getLogger().getEffectiveLevel())
        if len(log.filters) == 0:
            f = PlumberyLogFilter()
            log.addFilter(f)
        if len(log.handlers) == 0:
            handler = colorlog.StreamHandler()
            handler.setFormatter(formatter)
            log.addHandler(handler)
        loggers.update(dict(name=log))
        return log