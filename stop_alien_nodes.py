from collections import namedtuple

from libcloud.compute.types import NodeState

from plumbery import Plumbery

plumbery = Plumbery()

# inventory of network domains
domains = {}
Domain = namedtuple('Domain', 'description, status, name')

# enumerate existing domains
for domain in plumbery.region.ex_list_network_domains(location=plumbery.location):

	# identify domains that are part of our fittings
	status = 'alien'
	if domain.name in plumbery.fittings.domains:
		status = 'citizen'
	else:
		for blueprint in plumbery.fittings.blueprints:
			if domain.name == blueprint.values()[0]['domain']:
				status = 'citizen'
				break

	# remember for later use
	domains[domain.id] = Domain(
		description = domain.description,
		status = status,
		name = domain.name
		)

# inventory of nodes
nodes = {}
Node = namedtuple('Node', 'cpuCount, deployedTime, description, status, memoryMb, name, networkDomainId, operatingSystemType, sourceImageId, state, uuid')

# enumerate existing nodes
for node in plumbery.region.list_nodes():

	# skip nodes from other locations
	if node.extra['datacenterId'] != plumbery.location.id:
		continue

	# identify nodes that are part of our fittings
	status = 'alien'
	if node.name in plumbery.fittings.nodes:
		status = 'citizen'

	# this node is part of a citizen network domain
	elif domains[node.extra['networkDomainId']].status == 'citizen':
		status = 'citizen'

	# this node has been named in the fittings
	else:
		for blueprint in plumbery.fittings.blueprints:
			if node.name in blueprint.values()[0]['nodes']:
				status = 'citizen'
				break

	# remember for later use
	nodes[node.id] = Node(
		cpuCount = node.extra['cpuCount'],
		deployedTime = node.extra['deployedTime'],
		description = node.extra['description'],
		status = status,
		memoryMb = node.extra['memoryMb'],
		name = node.name,
		networkDomainId = node.extra['networkDomainId'],
		operatingSystemType = node.extra['OS_type'],
		sourceImageId = node.extra['sourceImageId'],
		state = node.state,
		uuid = node.uuid
		)

# report on the hard work
aliens = 0
citizens = 0

# list alien nodes
for id in nodes:

	# skip regular node
	if nodes[id].status != 'alien':
		citizens += 1
		continue

	# offer to shutdown running alien nodes
	aliens += 1
	if nodes[id].state is NodeState.RUNNING:
		print nodes[id].name, 'has been deployed on', nodes[id].deployedTime[0:10], 'and is not part of our fittings'
		feedback = raw_input('Should this node been stopped? [y/N/q] ').lower()

		# we are asked to shutdown this node
		if len(feedback) > 0 and feedback[0] == 'y':

			if plumbery.safeMode:
				print "Would have stopped node '{}' if not in safe mode".format(nodes[id].name)

			else:
				print "Stopping node '{}'".format(nodes[id].name)

				# we may have to wait for busy resources
				while True:

					try:
						plumbery.region.ex_shutdown_graceful(plumbery.region.ex_get_node_by_id(id))
						print "- in progress"

					except Exception as feedback:

						# resource is busy, wait a bit and retry
						if 'RESOURCE_BUSY' in str(feedback):
							plumbery.wait_and_tick()
							continue

						# fatal error
						else:
							print "Error: unable to stop node '{}'!".format(nodes[id].name)
							print feedback
							exit(-1)

					# quit the loop
					break


		# quit this loop immediately
		elif len(feedback) > 0 and feedback[0] == 'q':
			break

# report on the hard work
print "{} nodes have been processed in total, including {} alien nodes".format(len(nodes), aliens)




