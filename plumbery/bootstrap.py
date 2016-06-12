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

import argparse
import os
import requests
import six
import sys

if six.PY2:
    from urlparse import urljoin as up
else:
    from urllib.parse import urljoin as up


def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-o', '--output', help='output directory')
    parser.add_argument('files', nargs='+', help='The URL for remote files')
    return parser.parse_args(args)


def main(args):
    if args.output is None:
        args.output = os.getcwd()
    for url in args.files:
        filename = url.split('/')[-1]
        if filename == 'manifest.mf':
            download_manifest(url, args.output)
        else:
            download_file(url, args.output)


def download_manifest(url, output_dir):
    download_file(url, output_dir)
    with open(os.path.join(output_dir, 'manifest.mf'), 'r') as manifest_file:
        lines = manifest_file.readlines()
        for i in lines:
            download_file(up(url, i), output_dir)


def download_file(url, output_dir):
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(os.path.join(output_dir, local_filename), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    main(args)