#!/usr/bin/env python

"""
Tests for `text` module.
"""

import unittest
import yaml

import six

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

from plumbery.engine import PlumberyEngine
from plumbery.text import PlumberyText, PlumberyContext, PlumberyNodeContext
from plumbery import __version__

input1 = """
var http = require('http');
http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Hello World\n');
}).listen(8080, '{{ node.private }}');
console.log('Server running at http://{{ node.private }}:8080/');
"""

expected1 = input1.replace('{{ node.private }}', '12.34.56.78')

input2 = {
    'packages': ['ntp', 'nodejs', 'npm'],
    'ssh_pwauth': True,
    'disable_root': False,
    'bootcmd':
        ['curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -'],
    'write_files': [{
        'content': input1,
        'path': '/root/hello.js'}],
    'runcmd': ['sudo npm install pm2 -g', 'pm2 start /root/hello.js']}

expected2 = {
    'packages': ['ntp', 'nodejs', 'npm'],
    'ssh_pwauth': True,
    'disable_root': False,
    'bootcmd':
        ['curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -'],
    'write_files': [{
        'content': expected1,
        'path': '/root/hello.js'}],
    'runcmd': ['sudo npm install pm2 -g', 'pm2 start /root/hello.js']}

input3 = """
disable_root: false
ssh_pwauth: True
bootcmd:
  - "curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -"
packages:
  - ntp
  - nodejs
  - npm
write_files:
  - content: |
      var http = require('http');
      http.createServer(function (req, res) {
        res.writeHead(200, {'Content-Type': 'text/plain'});
        res.end('Hello World\\n');
      }).listen(8080, '{{ node.public }}');
      console.log('Server running at http://{{ node.public }}:8080/');
    path: /root/hello.js
runcmd:
  - sudo npm install pm2 -g
  - pm2 start /root/hello.js
"""

expected3 = input3.replace('{{ node.public }}', '12.34.56.78')

input4 = """
locationId: EU6 # Frankfurt in Europe
regionId: dd-eu

blueprints:

  - nodejs:
      domain:
        name: NodejsFox
        service: essentials
        ipv4: 2
      ethernet:
        name: nodejsfox.servers
        subnet: 192.168.20.0
      nodes:
        - nodejs01:
            cpu: 2
            memory: 8
            monitoring: essentials
            glue:
              - internet 22 8080
            cloud-config:
              disable_root: false
              ssh_pwauth: True
              bootcmd:
                - "curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -"
              packages:
                - ntp
                - nodejs
                - npm
              write_files:
                - content: |
                    var http = require('http');
                    http.createServer(function (req, res) {
                      res.writeHead(200, {'Content-Type': 'text/plain'});
                      res.end('Hello World\\n');
                    }).listen(8080, '{{ node.public }}');
                    console.log('Server running at http://{{ node.public }}:8080/');
                  path: /root/hello.js
              runcmd:
                - sudo npm install pm2 -g
                - pm2 start /root/hello.js
"""

input5 = """
write_files:
  - content: |
      #! /usr/bin/sed -i
      s/tcp-keepalive ([0-9]+)/tcp-keepalive 60/
      /^bind 127.0.0.1/s/^/#/
      /^#requirepass/s/^#//
      s/requirepass (.*)$/requirepass {{ random.secret }}/
      /^#maxmemory-policy/s/^#//
      s/maxmemory-policy (.*)$/maxmemory-policy noeviction/
    path: /root/edit_redis_conf.sed
"""

input6 = """
conf:
   ca_cert: |
     {{ certificate }} has multiple lines, but all of them
     should be nicely left-aligned since variable is first element on line
"""

dict6 = {
    'certificate': "-----BEGIN CERTIFICATE-----\n"
    "MIICCTCCAXKgAwIBAgIBATANBgkqhkiG9w0BAQUFADANMQswCQYDVQQDDAJjYTAe\n"
    "Fw0xMDAyMTUxNzI5MjFaFw0xNTAyMTQxNzI5MjFaMA0xCzAJBgNVBAMMAmNhMIGf\n"
    "MA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCu7Q40sm47/E1Pf+r8AYb/V/FWGPgc\n"
    "b014OmNoX7dgCxTDvps/h8Vw555PdAFsW5+QhsGr31IJNI3kSYprFQcYf7A8tNWu\n"
    "1MASW2CfaEiOEi9F1R3R4Qlz4ix+iNoHiUDTjazw/tZwEdxaQXQVLwgTGRwVa+aA\n"
    "qbutJKi93MILLwIDAQABo3kwdzA4BglghkgBhvhCAQ0EKxYpUHVwcGV0IFJ1Ynkv\n"
    "T3BlblNTTCBHZW5lcmF0ZWQgQ2VydGlmaWNhdGUwDwYDVR0TAQH/BAUwAwEB/zAd\n"
    "BgNVHQ4EFgQUu4+jHB+GYE5Vxo+ol1OAhevspjAwCwYDVR0PBAQDAgEGMA0GCSqG\n"
    "SIb3DQEBBQUAA4GBAH/rxlUIjwNb3n7TXJcDJ6MMHUlwjr03BDJXKb34Ulndkpaf\n"
    "+GAlzPXWa7bO908M9I8RnPfvtKnteLbvgTK+h+zX1XCty+S2EQWk29i2AdoqOTxb\n"
    "hppiGMp0tT5Havu4aceCXiy2crVcudj3NFciy8X66SoECemW9UYDCb9T5D0d\n"
    "-----END CERTIFICATE-----"}

expected6 = """
conf: \
\n  ca_cert: |
      -----BEGIN CERTIFICATE-----
      MIICCTCCAXKgAwIBAgIBATANBgkqhkiG9w0BAQUFADANMQswCQYDVQQDDAJjYTAe
      Fw0xMDAyMTUxNzI5MjFaFw0xNTAyMTQxNzI5MjFaMA0xCzAJBgNVBAMMAmNhMIGf
      MA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCu7Q40sm47/E1Pf+r8AYb/V/FWGPgc
      b014OmNoX7dgCxTDvps/h8Vw555PdAFsW5+QhsGr31IJNI3kSYprFQcYf7A8tNWu
      1MASW2CfaEiOEi9F1R3R4Qlz4ix+iNoHiUDTjazw/tZwEdxaQXQVLwgTGRwVa+aA
      qbutJKi93MILLwIDAQABo3kwdzA4BglghkgBhvhCAQ0EKxYpUHVwcGV0IFJ1Ynkv
      T3BlblNTTCBHZW5lcmF0ZWQgQ2VydGlmaWNhdGUwDwYDVR0TAQH/BAUwAwEB/zAd
      BgNVHQ4EFgQUu4+jHB+GYE5Vxo+ol1OAhevspjAwCwYDVR0PBAQDAgEGMA0GCSqG
      SIb3DQEBBQUAA4GBAH/rxlUIjwNb3n7TXJcDJ6MMHUlwjr03BDJXKb34Ulndkpaf
      +GAlzPXWa7bO908M9I8RnPfvtKnteLbvgTK+h+zX1XCty+S2EQWk29i2AdoqOTxb
      hppiGMp0tT5Havu4aceCXiy2crVcudj3NFciy8X66SoECemW9UYDCb9T5D0d
      -----END CERTIFICATE----- has multiple lines, but all of them
      should be nicely left-aligned since variable is first element on line
"""

input7 = """
write_files: \
\n  - content: |
        #!/bin/sh
        /usr/bin/expect <<EOF
        spawn "/usr/bin/vncpasswd"
        expect "Password:"
        send "{{ vnc.secret }}\\r"
        expect "Verify:"
        send "{{ vnc.secret }}\\r"
        expect eof
        exit
        EOF

"""

dict7 = {'vnc.secret': 'fake'}

expected7 = input7.replace('{{ vnc.secret }}', 'fake')

input8 = """
content: |
    #!/usr/bin/sed
    /bind-address/s/127.0.0.1/::/
    s/#server-id/server-id/
    /server-id/s/= 1/= 123/
    s/#log_bin.*/log-bin = mysql-bin/
    /max_binlog_size/a log-slave-updates\\nbinlog_format = MIXED\\nenforce-gtid-consistency\\ngtid-mode = ON
    /enforce-gtid-consistency/s/^#//
    /gtid-mode/s/^#//
    $!N; /^\\(.*\\)\\n\\1$/!P; D
"""

input9 = """
ssh-authorized-keys:
- "{{ rsa_public.local }}"
"""

input10 = """
runcmd: \
\n  - echo "===== Installing Let's Chat"
  - cp -n /etc/ssh/ssh_host_rsa_key /home/ubuntu/.ssh/id_rsa
  - cp -n /etc/ssh/ssh_host_rsa_key.pub /home/ubuntu/.ssh/id_rsa.pub
  - chown ubuntu:ubuntu /home/ubuntu/.ssh/*

"""


class FakeNode1:

    id = '1234'
    name = 'mongo_mongos01'
    public_ips = ['168.128.12.163']
    private_ips = ['192.168.50.11']
    extra = {'ipv6': '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f',
             'datacenterId': 'EU6'}


class FakeNode2:

    id = '5678'
    name = 'mongo_mongos02'
    public_ips = ['168.128.12.164']
    private_ips = ['192.168.50.12']
    extra = {'ipv6': '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f',
             'datacenterId': 'EU6'}


class FakeRegion:

    def list_nodes(self):
        return [FakeNode1(), FakeNode2()]

    def get_node(self, name):
        return FakeNode2()


class FakeFacility:

    plumbery = PlumberyEngine()
    region = FakeRegion()
    backup = None

    def list_nodes(self):
        return ['mongo_mongos01', 'mongo_mongos02']

    def power_on(self):
        pass

    def get_location_id(self):
        return 'EU6'


class FakeContainer:

    facility = FakeFacility()
    region = FakeRegion()


class TestPlumberyText(unittest.TestCase):

    def setUp(self):
        self.text = PlumberyText()

    def tearDown(self):
        pass

    def test_dictionary(self):

        template = 'little {{ test }} with multiple {{test}} and {{}} as well'
        context = PlumberyContext(dictionary={'test': 'toast'})
        expected = 'little toast with multiple toast and {{}} as well'
        self.assertEqual(
            self.text.expand_string(template, context), expected)

    def test_engine(self):

        engine = PlumberyEngine()
        context = PlumberyContext(context=engine)

        template = "we are running plumbery {{ plumbery.version }}"
        expected = "we are running plumbery "+__version__
        self.assertEqual(
            self.text.expand_string(template, context), expected)

        engine.set_user_name('fake_name')
        engine.set_user_password('fake_password')

        template = "{{ name.credentials }} {{ password.credentials }}"
        expected = engine.get_user_name()+" "+engine.get_user_password()
        self.assertEqual(
            self.text.expand_string(template, context), expected)

    def test_input1(self):

        context = PlumberyContext(dictionary={'node.private': '12.34.56.78'})
        self.assertEqual(
            self.text.expand_string(input1, context), expected1)

    def test_input2(self):

        context = PlumberyContext(dictionary={})
        transformed = yaml.load(self.text.expand_string(input2, context))
        unmatched = {o: (input2[o], transformed[o])
                     for o in input2.keys()
                     if input2[o] != transformed[o]}
        if unmatched != {}:
            print(unmatched)
        self.assertEqual(len(unmatched), 0)

        context = PlumberyContext(dictionary={'node.private': '12.34.56.78'})
        transformed = yaml.load(self.text.expand_string(input2, context))
        unmatched = {o: (expected2[o], transformed[o])
                     for o in expected2.keys()
                     if expected2[o] != transformed[o]}
        if unmatched != {}:
            print(unmatched)
        self.assertEqual(len(unmatched), 0)

    def test_input3(self):

        loaded = yaml.load(input3)
        context = PlumberyContext(dictionary={'node.public': '12.34.56.78'})
        transformed = yaml.load(self.text.expand_string(loaded, context))
        self.assertEqual(transformed, yaml.load(expected3))

    def test_input4(self):

        loaded = yaml.load(input4)
        context = PlumberyContext(dictionary={})
        transformed = yaml.load(self.text.expand_string(loaded, context))
        self.assertEqual(transformed, loaded)

    def test_input5(self):

        loaded = yaml.load(input5)
        context = PlumberyContext(dictionary={})
        transformed = yaml.load(self.text.expand_string(loaded, context))
        self.assertEqual(transformed, loaded)

    def test_input6(self):

        loaded = yaml.load(input6)
        context = PlumberyContext(dict6)
        transformed = self.text.expand_string(loaded, context)
        self.assertEqual(transformed.strip(), expected6.strip())

    def test_input7(self):

        loaded = yaml.load(input7)
        context = PlumberyContext(dict7)
        transformed = self.text.expand_string(loaded, context)
        self.assertEqual(transformed.strip(), expected7.strip())

    def test_input8(self):

        loaded = yaml.load(input8)
        context = PlumberyContext(dictionary={})
        expanded = self.text.expand_string(loaded, context)
        self.assertEqual(expanded.strip(), input8.strip())

    def test_input9(self):

        loaded = yaml.load(input9)
        context = PlumberyContext(context=PlumberyEngine())
        expanded = self.text.expand_string(loaded, context)
        self.assertEqual(('  - |' in expanded), False)

    def test_input10(self):

        loaded = yaml.load(input10)
        context = PlumberyContext(dictionary={})
        expanded = self.text.expand_string(loaded, context)
        self.assertEqual(expanded.strip(), input10.strip())

    def test_node1(self):

        template = "{{ mongo_mongos01.public }}"
        context = PlumberyNodeContext(node=FakeNode1())
        expected = '168.128.12.163'
        self.assertEqual(
            self.text.expand_string(template, context), expected)

        template = "{{mongo_mongos01.private }}"
        expected = '192.168.50.11'
        self.assertEqual(
            self.text.expand_string(template, context), expected)

        template = "{{ mongo_mongos01}}"
        expected = '192.168.50.11'
        self.assertEqual(
            self.text.expand_string(template, context), expected)

        template = "{{ mongo_mongos01.ipv6 }}"
        expected = '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f'
        self.assertEqual(
            self.text.expand_string(template, context), expected)

    def test_node2(self):

        template = "{{ mongo_mongos02.public }}"
        context = PlumberyNodeContext(node=FakeNode1(),
                                      container=FakeContainer())
        expected = '168.128.12.164'
        self.assertEqual(
            self.text.expand_string(template, context), expected)

        template = "{{ mongo_mongos02.private }}"
        expected = '192.168.50.12'
        self.assertEqual(
            self.text.expand_string(template, context), expected)

        template = "{{ mongo_mongos02 }}"
        expected = '192.168.50.12'
        self.assertEqual(
            self.text.expand_string(template, context), expected)

        template = "{{ mongo_mongos02.ipv6 }}"
        expected = '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f'
        self.assertEqual(
            self.text.expand_string(template, context), expected)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
