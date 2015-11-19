#!/usr/bin/env python
#
"""Are you looking for a cloud plumber? We hope that this one will be useful to you"""

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

# standard libraries
import os
from pprint import pprint
import sys
import time
import traceback

# yaml for fittings description - http://pyyaml.org/wiki/PyYAMLDocumentation
import yaml

# paramiko for ssh communications - https://github.com/paramiko/paramiko
import paramiko

# Apache Libcloud - https://libcloud.readthedocs.org/en/latest/compute/index.html
from libcloud.compute.base import NodeAuthPassword
from libcloud.compute.providers import get_driver
from libcloud.compute.types import NodeState
from libcloud.compute.types import Provider
from libcloud.common.dimensiondata import DimensionDataConnection

# turn a dictionary to an object
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class Plumbery:
	"""Cloud automation at Dimension Data with Apache Libcloud"""

	# the list of available images to create nodes
	images = None

	# the target data center
	location = None

	# the description of the fittings
	fittings = None

	# the handle to Dimension Data cloud API
	region = None

	# safe mode or not
	safeMode = True

	# the password to access remote servers
	sharedSecret = None

	# the resource to access remote servers - ON THE TODO LIST
	ssh = None


	def __init__(self, fileName=None):
		"""Ignite the plumbering engine"""

		# read fittings description from YAML file - region, location, domains, nodes, etc.
		self.parse_layout(fileName)

		# get API credentials from environment - with bash, edit ~/.bash_profile to export your credentials in local environment
		self.mcpUserName = os.getenv('MCP_USERNAME', "Set environment variable MCP_USERNAME with credentials given to you")
		self.mcpPassword = os.getenv('MCP_PASSWORD', "Set environment variable MCP_PASSWORD with credentials given to you")

		# get root password from environment - with bash, edit ~/.bash_profile to export SHARED_SECRET in local environment
		self.sharedSecret = os.getenv('SHARED_SECRET')
		if self.sharedSecret is None or len(self.sharedSecret) < 3:
			print "Error: set environment variable SHARED_SECRET with the password to access nodes remotely!"
			exit(-1)

		# get libcloud driver for Managed Cloud Platform (MCP) of Dimension Data
		self.driver = get_driver(Provider.DIMENSIONDATA)

		# configure the API endpoint - regional parameter is related to federated structure of cloud services
		self.region = self.driver(self.mcpUserName, self.mcpPassword, region=self.fittings.regionId)

		# focus at one specific location - and attempt to use the API over the network
		try:
			self.location = self.region.ex_get_location_by_id(self.fittings.locationId)
			print "Working at '{}' {} ({})".format(self.location.id, self.location.name, self.location.country)
		except Exception as feedback:
			print "Error: unable to communicate with API endpoint - have you checked http_proxy environment variable?"
			print feedback
			exit(-1)

		# fetch the list of available images only once from the API
		self.images = self.region.list_images(location=self.location)

		# a ready-to use ssh factory
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


	def build_all_blueprints(self):
		"""Build all blueprints"""

		print "Building all blueprints"

		for blueprint in self.fittings.blueprints:
			self.build_blueprint(blueprint.keys()[0])


	def build_blueprint(self, name):
		"""Build a named blueprint"""

		print "Building blueprint '{}'".format(name)

		# get the blueprint
		blueprint = self.get_blueprint(name)

		# create the network domain if it does not exist
		self.build_domain(blueprint)

		# create the network if it does not exist
		self.build_network(blueprint)

		# create nodes that do not exist
		self.build_nodes(blueprint)


	def build_domain(self, blueprint):
		"""Create network domain if it does not exist"""

		# check the target network domain
		if 'domain' not in blueprint:
			print "Error: no network domain has been defined for the '{}' blueprint!".format(blueprint['target'])
			exit(-1)

		# seek for an existing network domain with this name
		self.domain = None
		for self.domain in self.region.ex_list_network_domains(location=self.location):
			if self.domain.name == blueprint['domain']:
				print "Network domain '{}' already exists".format(blueprint['domain'])
				break

		# create a network domain if needed
		if self.domain is None or self.domain.name != blueprint['domain']:

			if self.safeMode:
				print "Would have created network domain '{}' if not in safe mode".format(blueprint['domain'])
				exit(0)

			else:
				print "Creating network domain '{}'".format(blueprint['domain'])

				# we may have to wait for busy resources
				while True:

					try:
						self.domain = self.region.ex_create_network_domain(
							location = self.location,
							name = blueprint['domain'],
							service_plan = 'ESSENTIALS',
							description = '#plumbery')
						print "- in progress"

					except Exception as feedback:

						# resource is busy, wait a bit and retry
						if 'RESOURCE_BUSY' in str(feedback):
							self.wait_and_tick()
							continue

						# fatal error
						else:
							print "Error: unable to create network domain '{}'!".format(blueprint['domain'])
							print feedback
							exit(-1)

					# quit the loop
					break



	def build_network(self, blueprint):
		"""Create Ethernet network if it does not exist"""

		# check name of the target network
		if 'ethernet' not in blueprint:
			print "Error: no ethernet network has been defined for the '{}' blueprint!".format(blueprint['target'])
			exit(-1)

		# check addresses to use for the target network
		if 'subnet' not in blueprint:
			print "Error: no IPv4 subnet (e.g., '10.0.34.0') as been defined for the '{}' blueprint!".format(blueprint['target'])
			exit(-1)

		# seek for an existing network with this name
		self.network = None
		for self.network in self.region.ex_list_vlans(location=self.location, network_domain=self.domain):
			if self.network.name == blueprint['ethernet']:
				print "Ethernet network '{}' already exists".format(blueprint['ethernet'])
				break

		# create a network if needed
		if self.network is None or self.network.name != blueprint['ethernet']:

			if self.safeMode:
				print "Would have created Ethernet network '{}' if not in safe mode".format(blueprint['ethernet'])
				exit(0)

			else:
				print "Creating Ethernet network '{}'".format(blueprint['ethernet'])

				# we may have to wait for busy resources
				while True:

					try:
						self.network = self.region.ex_create_vlan(
							network_domain = self.domain,
							name = blueprint['ethernet'],
							private_ipv4_base_address = blueprint['subnet'],
							description = '#plumbery')
						print "- in progress"

					except Exception as feedback:

						# resource is busy, wait a bit and retry
						if 'RESOURCE_BUSY' in str(feedback):
							self.wait_and_tick()
							continue

						# fatal error
						else:
							print "Error: unable to create Ethernet network '{}'!".format(blueprint['ethernet'])
							print feedback
							exit(-1)

					# quit the loop
					break



	def build_nodes(self, blueprint):
		"""Create nodes if they do not exist"""

		# ensure that we have some nodes described here
		if 'nodes' not in blueprint:
			print "Error: no nodes have been defined for the '{}' blueprint!".format(blueprint['target'])
			exit(-1)

		# respect the order of nodes defined in the fittings description
		for item in blueprint['nodes']:

			# node has several explicit attributes
			if type(item) is dict:
				nodeName = item.keys()[0]
				nodeAttributes = item.values()[0]

			# node has only a name
			else:
				nodeName = item
				nodeAttributes = None

			# node may already exist
			if self.get_node(nodeName):
				print "Node '{}' already exists".format(nodeName)

			# create a new node
			else:

				# the description attribute is a smart way to tag resources
				description = '#plumbery'
				if type(nodeAttributes) is dict and 'description' in nodeAttributes:
					description = nodeAttributes['description'] + ' #plumbery'

				# define which image to use
				if type(nodeAttributes) is dict and 'appliance' in nodeAttributes:
					imageName = nodeAttributes['appliance']
				else:
					imageName = 'Ubuntu'

				# find suitable image to use
				image = None
				for image in self.images:
					if imageName in image.name:
						break

				# Houston, we've got a problem
				if image is None or imageName not in image.name:
					print "Error: unable to find image for '{}'!".format(imageName)
					exit(-1)

				# safe mode
				if self.safeMode:
					print "Would have created node '{}' if not in safe mode".format(nodeName)

				# actual node creation
				else:
					print "Creating node '{}'".format(nodeName)

					# we may have to wait for busy resources
					while True:

						try:
							node = self.region.create_node(
								name = nodeName,
								image = image,
								auth = NodeAuthPassword(self.sharedSecret),
								ex_network_domain = self.domain,
								ex_vlan = self.network,
								ex_is_started = False,
								ex_description = description)
							print "- in progress"

						except Exception as feedback:

							# resource is busy, wait a bit and retry
							if 'RESOURCE_BUSY' in str(feedback):
								self.wait_and_tick()
								continue

							# fatal error
							else:
								print "Error: unable to create node '{}'!".format(nodeName)
								print feedback
								exit(-1)

						# quit the loop
						break



	def destroy_all_nodes(self):
		"""Destroy all nodes"""

		print "Destroying nodes from all blueprints"

		# destroy in reverse order
		for blueprint in self.fittings.blueprints:
			self.destroy_nodes(blueprint.keys()[0])



	def destroy_nodes(self, name):
		"""Destroy nodes"""

		print "Destroying nodes from blueprint '{}'".format(name)

		# get the blueprint
		blueprint = self.get_blueprint(name)

		# ensure that some nodes have been described
		if 'nodes' not in blueprint:
			return

		# check the target network domain
		if 'domain' not in blueprint:
			print "Error: no network domain has been defined for the '{}' blueprint!".format(blueprint['target'])
			exit(-1)

		# seek for an existing network domain with this name
		self.domain = None
		for self.domain in self.region.ex_list_network_domains(location=self.location):
			if self.domain.name == blueprint['domain']:
				break

		# destroy in reverse order
		for item in reversed(blueprint['nodes']):

			# find the name of the node to be destroyed
			if type(item) is dict:
				nodeName = item.keys()[0]
			else:
				nodeName = str(item)

			# enumerate existing nodes
			node = self.get_node(nodeName)

			# destroy an existing node
			if node is not None:

				# safe mode
				if self.safeMode:
					print "Would have destroyed node '{}' if not in safe mode".format(nodeName)

				# actual node destruction
				else:
					print "Destroying node '{}'".format(nodeName)

					# we may have to wait for busy resources
					while True:

						try:
							self.region.destroy_node(node)
							print "- in progress"

						except Exception as feedback:

							# resource is busy, wait a bit and retry
							if 'RESOURCE_BUSY' in str(feedback):
								self.wait_and_tick()
								continue

							# node is up and running, would have to stop it first
							elif 'SERVER_STARTED' in str(feedback):
								print "- skipped - server is up and running"

							# fatal error
							else:
								print "Error: unable to destroy node '{}'!".format(nodeName)
								print feedback
								exit(-1)

						# quit the loop
						break


	def get_blueprint(self, name):
		"""Get a blueprint by name"""

		for blueprint in self.fittings.blueprints:
			if name in blueprint.keys()[0]:
				blueprint = blueprint[name]
				blueprint['target'] = name
				return blueprint

		print "Error: no '{}' blueprint in these fittings!".format(name)
		exit(-1)


	def get_node(self, name):
		"""Get a node by name"""

		# enumerate existing nodes
		node = None
		for node in self.region.list_nodes():

			# skip nodes from other locations
			if node.extra['datacenterId'] != self.location.id:
				continue

			# skip nodes from other network domains
			if node.extra['networkDomainId'] != self.domain.id:
				continue

			# found an existing node with this name
			if node.name == name:
				return node

		# not found
		return None


	def parse_layout(self, fileName=None):
		"""Read description of the fittings"""

		# get file name from the environment, or use default name
		if not fileName:
			fileName = os.getenv('PLUMBERY', 'fittings.yaml')

		# maybe file cannot be read or YAML is broken
		try:
			with open(fileName, 'r') as stream:

				# turn dictionary to an object
				fittingsAsDict = yaml.load(stream)
				self.fittings = Struct(**fittingsAsDict)

		except Exception as feedback:
			print "Error: unable to load file '{}'!".format(fileName)
			print feedback
			exit(-1)

		# apply configuration
		if 'safeMode' in fittingsAsDict:
			self.safeMode = fittingsAsDict['safeMode']

		# are we in safe mode?
		if self.safeMode:
			print "Running in safe mode - no actual change will be made to the fittings"


	def start_all_nodes(self):
		"""Start all nodes"""

		print "Starting nodes from all blueprints"

		for blueprint in self.fittings.blueprints:
			self.start_nodes(blueprint.keys()[0])



	def start_nodes(self, name):
		"""Start nodes"""

		print "Starting nodes from blueprint '{}'".format(name)

		# get the blueprint
		blueprint = self.get_blueprint(name)

		# ensure that some nodes have been described
		if 'nodes' not in blueprint:
			return

		# check the target network domain
		if 'domain' not in blueprint:
			print "Error: no network domain has been defined for the '{}' blueprint!".format(blueprint['target'])
			exit(-1)

		# seek for an existing network domain with this name
		self.domain = None
		for self.domain in self.region.ex_list_network_domains(location=self.location):
			if self.domain.name == blueprint['domain']:
				break

		# start nodes
		for item in blueprint['nodes']:

			# find the name of the node to be destroyed
			if type(item) is dict:
				nodeName = item.keys()[0]
			else:
				nodeName = str(item)

			# enumerate existing nodes
			node = self.get_node(nodeName)

			# start an existing node
			if node is not None:

				# safe mode
				if self.safeMode:
					print "Would have started node '{}' if not in safe mode".format(nodeName)

				# actual node start
				else:
					print "Starting node '{}'".format(nodeName)

					# we may have to wait for busy resources
					while True:

						try:
							self.region.ex_start_node(node)
							print "- in progress"

						except Exception as feedback:

							# resource is busy, wait a bit and retry
							if 'RESOURCE_BUSY' in str(feedback):
								self.wait_and_tick()
								continue

							# fatal error
							else:
								print "Error: unable to start node '{}'!".format(nodeName)
								print feedback
								exit(-1)

						# quit the loop
						break


	def stop_all_nodes(self):
		"""Stop all nodes"""

		print "Stopping nodes from all blueprints"

		for blueprint in self.fittings.blueprints:
			self.stop_nodes(blueprint.keys()[0])


	def stop_nodes(self, name):
		"""Stop nodes"""

		print "Stopping nodes from blueprint '{}'".format(name)

		# get the blueprint
		blueprint = self.get_blueprint(name)

		# ensure that some nodes have been described
		if 'nodes' not in blueprint:
			return

		# check the target network domain
		if 'domain' not in blueprint:
			print "Error: no network domain has been defined for the '{}' blueprint!".format(blueprint['target'])
			exit(-1)

		# seek for an existing network domain with this name
		self.domain = None
		for self.domain in self.region.ex_list_network_domains(location=self.location):
			if self.domain.name == blueprint['domain']:
				break

		# start nodes
		for item in blueprint['nodes']:

			# find the name of the node to be destroyed
			if type(item) is dict:
				nodeName = item.keys()[0]
			else:
				nodeName = str(item)

			# enumerate existing nodes
			node = self.get_node(nodeName)

			# stop an existing node
			if node is not None:

				# safe mode
				if self.safeMode:
					print "Would have stopped node '{}' if not in safe mode".format(nodeName)

				# actual node stop
				else:
					print "Stopping node '{}'".format(nodeName)

					# we may have to wait for busy resources
					while True:

						try:
							self.region.ex_shutdown_graceful(node)
							print "- in progress"

						except Exception as feedback:

							# resource is busy, wait a bit and retry
							if 'RESOURCE_BUSY' in str(feedback):
								self.wait_and_tick()
								continue

							# fatal error
							else:
								print "Error: unable to stop node '{}'!".format(nodeName)
								print feedback
								exit(-1)

						# quit the loop
						break


	def wait_and_tick(self):
		"""Animate the screen while delaying next call to the API"""

		sys.stdout.write('-\r')
		sys.stdout.flush()
		time.sleep(3)
		sys.stdout.write('\\\r')
		sys.stdout.flush()
		time.sleep(3)
		sys.stdout.write('|\r')
		sys.stdout.flush()
		time.sleep(3)
		sys.stdout.write('/\r')
		sys.stdout.flush()
		time.sleep(3)
		sys.stdout.write(' \r')

#					print "Configuring node '{}'".format(nodeName)
#
#					# connect via ssh
#					try:
#						self.ssh.connect(node.private_ips[0], username='root', password=self.sharedSecret)
#			#			ssh.connect(node.private_ips[0], username='<username>', password='<password>', key_filename='<path/to/openssh-private-key-file>')
#						stdin, stdout, stderr = ssh.exec_command('ls')
#						print stdout.readlines()
#					except:
#						print "Error: unable to ssh to node '{}'!".format(nodeName)
#					finally:
#						self.ssh.close()





