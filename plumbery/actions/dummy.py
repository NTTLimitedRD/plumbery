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

from plumbery.action import PlumberyAction
from plumbery.plogging import plogging


class DummyAction(PlumberyAction):
    """
    Dummy action used for tests

    :param settings: specific settings for this action
    :type param: ``dict``

    Look at another file in this directory if you are looking for something
    to derive for your own needs.
    """

    def ignite(self, engine):
        plogging.info("Action: dummy")
        plogging.info("- ignite engine")

    def enter(self, facility):
        plogging.info("- enter facility")

    def handle(self, blueprint):
        plogging.info("- handle blueprint")

    def quit(self):
        plogging.info("- quit facility")

    def reap(self):
        plogging.info("- reap")
