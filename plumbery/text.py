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

import logging

from nodes import PlumberyNodes

__all__ = ['PlumberyText', 'PlumberyContext']


class PlumberyText:

    @classmethod
    def expand_variables(cls, text, context):
        """
        Binds variables

        :param text: the text to be expanded
        :type text: ``str``

        :param context: context for lookup of tokens
        :type context: :class:`PlumberyContext`

        :return: the expanded text
        :rtype: ``str``

        This function allows for dynamic binding of data known by plumbery.

        """

        opening = '{{'
        closing = '}}'

        expanded = ''
        index = 0

        while index < len(text):
            head = text.find(opening, index)
            if head < 0:
                expanded += text[index:]
                break

            tail = text.find(closing, head+len(opening))
            if tail < 0:
                expanded += text[index:]
                break

            token = text[head+len(opening):tail].strip()
            if len(token) < 1:
                expanded += text[index:tail+len(closing)]
                index = tail+len(closing)
                continue

            replacement = context.lookup(token)

            logging.debug("Expanding '{}' to '{}'".format(token, replacement))
            expanded += text[index:head]+replacement
            index = tail+len(closing)

        return expanded


class PlumberyContext:

    def __init__(self, dictionary=None, context=None):

        if dictionary is None or not isinstance(dictionary, dict):
            self.dictionary = {}
        else:
            self.dictionary = dictionary

        self.keys = self.dictionary.keys()

        self.context = context

    def lookup(self, token):

        if token in self.keys:
            return str(self.dictionary[token])

        if self.context is not None:
            return self.context.lookup(token)

        return ''

class PlumberyNodeContext:

    def __init__(self, node, container=None, context=None):

        self.node = node
        self.container = container
        self.context = context
        self.cache = {
            'node': node.private_ips[0],
            node.name: node.private_ips[0],
            'node.private': node.private_ips[0],
            node.name+'.private': node.private_ips[0],
            'node.ipv6': node.extra['ipv6'],
            node.name+'.ipv6': node.extra['ipv6'],
            'node.public': node.public_ips[0],
            node.name+'.public': node.public_ips[0],
            'node.id': node.id,
            node.name+'.id': node.id,
            'node.name': node.name,
            node.name+'.name': node.name,
            'node.private_host': node.private_ips[0].replace('.', '-'),
            node.name+'.private_host': node.private_ips[0].replace('.', '-')
            }

    def lookup(self, token):

        if token in self.cache:
            return str(self.cache[token])

        if self.container is not None:

            if 'local_nodes_inventory' not in self.cache:
                self.cache['local_nodes_inventory'] = \
                    self.container.facility.list_nodes()

            tokens = token.split('.')
            if len(tokens) < 2:
                tokens.append('private')

            if tokens[0] in self.cache['local_nodes_inventory']:

                nodes = PlumberyNodes(self.container.facility)
                node = nodes.get_node(tokens[0])
                self.cache[node.name] = node.private_ips[0]
                self.cache[node.name+'.private'] = node.private_ips[0]
                self.cache[node.name+'.ipv6'] = node.extra['ipv6']
                self.cache[node.name+'.public'] = node.public_ips[0]

                if tokens[1] == 'private':
                    return node.private_ips[0]

                if tokens[1] == 'ipv6':
                    return node.extra['ipv6']

                if tokens[1] == 'public':
                    return node.public_ips[0]

        if self.context is not None:
            return self.context.lookup(token)

        return ''
