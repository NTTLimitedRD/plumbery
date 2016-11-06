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
import subprocess

from plumbery.plogging import plogging


class Terraform(object):
    def __init__(self, working_directory):
        self.working_directory = working_directory
        self.tf_path = os.getenv('TERRAFORM_PATH')
        if self.tf_path is None or not os.path.exists(self.tf_path):
            plogging.debug("Could not locate terraform binary. "
                           "Please check TERRAFORM_PATH ENV var."
                           "Ignore if no multicloud fittings are present")

    def build(self, settings):
        tf_path = settings.get('tf_path', None)
        if tf_path is None:
            # default back to the directory of the fittings file.
            tf_path = self.working_directory

        parameters = settings.get('parameters', {})
        with open(os.path.join(tf_path, '.tfvars'), 'w') as tf_vars:
            for (key, value) in parameters.items():
                tf_vars.write('%s = "%s"\n' % (key, value))

        ret, o, err = self._run_tf(
            'plan', tf_path,
            var_file=os.path.join(tf_path, '.tfvars'),
            input=False,
            detailed_exitcode=True,
            out=os.path.join(tf_path, '.tfstate'))
        plogging.debug("STDOUT from terraform plan %s", o)
        if err != '' or None:
            plogging.error(err)

        if ret == 2:
            _, o, err = self._run_tf('apply', os.path.join(tf_path, '.tfstate'))
            plogging.debug("STDOUT from terraform apply %s", o)
            if err != '' or None:
                plogging.error(err)
        if os.path.isfile(os.path.join(tf_path, '.tfstate')):
            os.remove(os.path.join(tf_path, '.tfstate'))
        if os.path.isfile(os.path.join(tf_path, '.tfvars')):
            os.remove(os.path.join(tf_path, '.tfvars'))

    def destroy(self, settings, safe=True):
        tf_path = settings.get('tf_path', None)
        if tf_path is None:
            # default back to the directory of the fittings file.
            tf_path = self.working_directory

        parameters = settings.get('parameters', {})
        with open(os.path.join(tf_path, '.tfvars'), 'w') as tf_vars:
            for (key, value) in parameters.items():
                tf_vars.write('%s = "%s"\n' % (key, value))
        if safe:
            _, o, _ = self._run_tf(
                'plan', tf_path,
                var_file=os.path.join(tf_path, '.tfvars'),
                input=False,
                detailed_exitcode=True,
                destroy=True)
            plogging.debug("STDOUT from terraform %s", o)
        else:
            _, o, _ = self._run_tf(
                'destroy', tf_path,
                var_file=os.path.join(tf_path, '.tfvars'),
                input=False,
                force=True)
            plogging.debug("STDOUT from terraform %s", o)

    def graph(self, state_directory):
        _, graph_data, _ = self._run_tf('graph', state_directory)
        graph_file_path = os.path.join(state_directory, 'multicloud.dot')
        with open(graph_file_path, 'w') as dot:
            dot.write(graph_data)

    def _run_tf(self, command, state_directory, **kwargs):
        if self.tf_path is None:
            plogging.error("Could not locate terraform binary. "
                           "Please check TERRAFORM_PATH ENV var.")
            raise RuntimeError("Missing terraform binary")
        params = [self.tf_path, command]
        for (key, value) in kwargs.items():
            params.append("-%s=%s" % (key.replace('_', '-'), value))
        params.append(state_directory)
        plogging.debug(params)
        process = subprocess.Popen(params, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        retcode = process.returncode
        return (retcode, stdout, stderr)
