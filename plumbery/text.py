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
import sys
import six
import yaml
from six import string_types
from plumbery.plogging import plogging
from plumbery.nodes import PlumberyNodes

__all__ = ['PlumberyText', 'PlumberyContext']

if six.PY2:
    b = bytes = ensure_string = str
else:
    def ensure_string(s):
        if isinstance(s, str):
            return s
        elif isinstance(s, bytes):
            return s.decode('utf-8')
        else:
            raise TypeError("Invalid argument %r for ensure_string()" % (s,))

class PlumberyText:

    @classmethod
    def expand_parameters(cls, text, context):
        """
        Binds parameters and produces a string

        :param text: the text to be expanded
        :type text: ``str``

        :param context: context for lookup of parameters
        :type context: :class:`PlumberyContext`

        :return: the expanded text
        :rtype: ``str``

        This function provides low-level binding of parameters.

        """

        opening = '{{'
        closing = '}}'

        if not isinstance(text, string_types):
            raise TypeError("Parameters expansion requires textual input")

        expanded = ''
        index = 0
        debugged = []

        while index < len(text):
            head = text.find(opening, index)
            if head < 0:
                expanded += text[index:]
                break

            tail = text.find(closing, head+len(opening))
            if tail < 0:
                expanded += text[index:]
                break

            while True:
                head_next = text.find(opening, head+len(opening), tail)
                if head_next > head:
                    head = head_next
                else:
                    break

            token = text[head+len(opening):tail].strip(' \\\t')
            if len(token) < 1:
                expanded += text[index:tail+len(closing)]
                index = tail+len(closing)
                continue

            if not token.startswith('parameter.'):
                expanded += text[index:tail+len(closing)]
                index = tail+len(closing)
                continue

            replacement = context.lookup(token)
            if replacement is None:
                raise KeyError("Missing parameter '{}'".format(token))

            if token not in debugged:
                plogging.debug("- '{}' -> '{}'".format(token, replacement))
                debugged.append(token)

            expanded += text[index:head]+str(replacement)
            index = tail+len(closing)

        return expanded

    @classmethod
    def expand_string(cls, text, context):
        """
        Binds variables and produces a string

        :param text: the text or the structure to be expanded
        :type text: ``str`` or ``dict``

        :param context: context for lookup of tokens
        :type context: :class:`PlumberyContext`

        :return: the expanded text
        :rtype: ``str``

        This function allows for dynamic binding of data known by plumbery.

        """

        opening = '{{'
        closing = '}}'

        serialized = False
        if not isinstance(text, string_types):  # serialize python object
            plogging.debug("- serializing object before expansion")
            if six.PY2:
                text = str(text)
            else:
                text = str(text)
            serialized = True

        expanded = ''
        index = 0
        debugged = []

        while index < len(text):
            head = text.find(opening, index)
            if head < 0:
                expanded += text[index:]
                break

            tail = text.find(closing, head+len(opening))
            if tail < 0:
                expanded += text[index:]
                break

            token = text[head+len(opening):tail].strip(' \\\t')
            if len(token) < 1:
                expanded += text[index:tail+len(closing)]
                index = tail+len(closing)
                continue

            replacement = context.lookup(token)
            if replacement is None:   # preserve unmatched tag
                if token not in debugged:
                    plogging.debug("- no match for '{}'".format(token))
                    debugged.append(token)

                expanded += text[index:tail+len(closing)]
                index = tail+len(closing)

            else:  # actual expansion
                if token not in debugged:
                    plogging.debug("- '{}' -> '{}'".format(token, replacement))
                    debugged.append(token)

                if serialized:  # preserve line breaks
                    replacement = ensure_string(replacement).replace('\n', '\\'+'n')

                expanded += text[index:head]+str(replacement)
                index = tail+len(closing)

        if serialized:  # from serialized python to yaml representation

            # protect  \ followed by \
            watermark1 = '-=_+*=-'
            expanded = expanded.replace('\\'+'\\', watermark1+'|'+watermark1)

            # protect  \ followed by '
            watermark2 = '-=*+_=-'
            expanded = expanded.replace('\\'+"'", watermark2+'|'+watermark2)

            # protect  None
            watermark3 = '=-_+*-='
            expanded = expanded.replace('None', watermark3+'None'+watermark3)

            instanciated = yaml.load(expanded)
            expanded = PlumberyText.dump(instanciated)

            expanded = expanded.replace(watermark1+'|'+watermark1, '\\')
            expanded = expanded.replace(watermark2+'|'+watermark2, "'")
            expanded = expanded.replace(watermark3+'None'+watermark3, 'None')

        return expanded

    @classmethod
    def could_expand(cls, content):
        """
        Checks if some bytes are expandable or not

        :param content: the blob to be tested
        :type content: ``str``

        :return: True if this could be expandable, False otherwise
        :rtype: ``bool``

        """

        textchars = bytearray({7, 8, 9, 10, 12, 13, 27}
                              | set(range(0x20, 0x100)) - {0x7f})

        if (sys.version_info > (3, 0)):
            is_binary = lambda bytes: bool(bytes.translate(textchars))
        else:
            is_binary = lambda bytes: bool(bytes.translate(None, textchars))

        return not is_binary(content)

    @classmethod
    def dump(cls, content):
        """
        Transforms a dictionary to a string

        :param content: the dictionary to transform
        :type content: ``dict``

        :return: the related string

        """
        return cls.dump_dict(content, spaces=0).strip()+'\n'

    @classmethod
    def dump_dict(cls, content, spaces=0):
        """
        Transforms a sub-dictionary to a string

        :param content: the dictionary to transform
        :type content: ``dict``

        :param spaces: shift to the right from containing elements
        :type spaces: ``int``

        :return: the related string

        """
        if isinstance(content, str):
            content = yaml.load(content)

        text = ''
        for key in content.keys():
            text += '\n' + ' ' * spaces + key + ': '

            value = content[key]

            if isinstance(value, dict):
                text += cls.dump_dict(value, spaces+2)

            elif isinstance(value, (list, tuple)):
                text += cls.dump_list(value, spaces+2)

            elif isinstance(value, bool):
                text += str(value).lower()

            else:
                text += cls.dump_str(str(value), spaces+2)

        return text

    @classmethod
    def dump_list(cls, content, spaces=0):
        """
        Transforms a list to a string

        :param content: the list to transform
        :type content: ``list``

        :param spaces: shift to the right from containing elements
        :type spaces: ``int``

        :return: the related string

        """
        if isinstance(content, str):
            content = yaml.load(content)

        text = ''
        for item in content:
            text += '\n' + ' ' * spaces + '- '

            if isinstance(item, dict):
                text += cls.dump_dict(item, spaces+2).lstrip()

            elif isinstance(item, list):
                text += cls.dump_list(item, spaces+2)

            elif isinstance(item, tuple):
                text += cls.dump_tuple(item, spaces+2)

            elif isinstance(item, bool):
                text += str(item).lower()

            else:
                text += cls.dump_str(str(item), spaces+2)

        return text

    @classmethod
    def dump_str(cls, content, spaces=0):
        """
        Transforms a string to a string

        :param content: the string to transform
        :type content: ``str``

        :param spaces: shift to the right from containing elements
        :type spaces: ``int``

        :return: the related string

        """

        lines = content.split('\n')
        if len(lines) == 1:              # that's a real hack...
            lines = content.split('\\n')

        if len(lines) == 1:              # quote string if it would fool yaml
            if len(content) > 0 and content[-1] in ('-', '\\', '|'):
                return '"'+content+'"'
            return content

        text = '|'
        spaces += 2
        for line in lines:
            text += '\n'
            if len(line) > 0:
                text += ' ' * spaces + line

        return text


class PlumberyContext:

    def __init__(self, dictionary=None, context=None):

        if dictionary is None or not isinstance(dictionary, dict):
            self.dictionary = {}
        else:
            self.dictionary = dictionary

        self.keys = self.dictionary.keys()

        self.context = context

    def lookup(self, token):
        """
        Retrieves the value attached to a token

        :param token: the token
        :type token: ``str``

        :return: the value attached to this token, or `None`

        """

        if token in self.keys:
            return str(self.dictionary[token])

        if self.context is not None:
            return self.context.lookup(token)

        return None


class PlumberyNodeContext:

    def __init__(self, node, container=None, context=None):

        self.node = node
        self.container = container
        self.context = context
        self.cache = {}

        if node is None:
            return

        self.cache = {
            'node': node.private_ips[0],
            node.name: node.private_ips[0],
            'node.private': node.private_ips[0],
            node.name+'.private': node.private_ips[0],
            'node.ipv6': node.extra['ipv6'],
            node.name+'.ipv6': node.extra['ipv6'],
            'node.id': node.id,
            node.name+'.id': node.id,
            'node.name': node.name,
            node.name+'.name': node.name,
            'node.private_host': node.private_ips[0].replace('.', '-'),
            node.name+'.private_host': node.private_ips[0].replace('.', '-')
            }

        if len(node.public_ips) > 0:
            self.cache['node.public'] = node.public_ips[0]
            self.cache[node.name+'.public'] = node.public_ips[0]

    def lookup(self, token):
        """
        Retrieves the value attached to a token

        :param token: the token, e.g., 'node.ipv6'
        :type token: ``str``

        :return: the value attached to this token, or `None`

        """

        if token in self.cache:
            return str(self.cache[token])

        value = None
        if self.context is not None:
            value = self.context.lookup(token)

        if value is not None:
            return value

        if self.container is None:
            return None

        tokens = token.split('.')
        if len(tokens) < 2:
            tokens.append('private')

        nodes = PlumberyNodes(self.container.facility)
        node = nodes.get_node(tokens[0])
        if node is None:
            return None

        if self.context is not None:
            self.context.remember(tokens[0], node.private_ips[0])
            self.context.remember(tokens[0]+'.private', node.private_ips[0])
            self.context.remember(tokens[0]+'.ipv6', node.extra['ipv6'])
            if len(node.public_ips) > 0:
                self.context.remember(tokens[0]+'.public', node.public_ips[0])

        if tokens[1] == 'private':
            return node.private_ips[0]

        if tokens[1] == 'ipv6':
            return node.extra['ipv6']

        if tokens[1] == 'public':
            if len(node.public_ips) > 0:
                return node.public_ips[0]
            else:
                return ''

        ethernet = self.container.get_ethernet(tokens[1])
        if ethernet is not None:

            if tokens[2] == 'gateway':

                if len(tokens) > 3 and tokens[3] == 'ipv6':
                    return ethernet.ipv6_gateway

                else:
                    return ethernet.ipv4_gateway

            elif tokens[2] == 'netmask':

                if len(tokens) > 3 and tokens[3] == 'ipv6':
                    return ethernet.ipv6_range_size

                else:
                    return ethernet.private_ipv4_range_address

        return None
