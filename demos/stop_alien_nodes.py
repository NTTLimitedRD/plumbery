
from libcloud.compute.types import NodeState

from plumbery.engine import PlumberyEngine

# report on the hard work
aliensCount = 0
nodesCount = 0

# load the full description of fittings
plumbery = PlumberyEngine('fittings.yaml')

# look at each facility
for facility in plumbery.facilities:
	facility.focus()

	# enumerate domains described in blueprints
	citizenDomainNames = set()
	for blueprint in facility.fittings.blueprints:
		attributes = blueprint.values()[0]
		citizenDomainNames.add(attributes['domain']['name'])

	# turn these names to actual unique ids
	citizenDomainIds = []
	for domain in facility.region.ex_list_network_domains(location=facility.location):
		if domain.name in citizenDomainNames:
			citizenDomainIds.append(domain.id)

	# enumerate nodes described in blueprints
	citizenNodeNames = set()
	for blueprint in facility.fittings.blueprints:
		for item in blueprint.values()[0]['nodes']:
			citizenNodeNames.add(item.keys()[0])

	# now we can look at each deployed node
	for node in facility.region.list_nodes():

		# skip nodes from other facilities
		if node.extra['datacenterId'] != facility.location.id:
			continue

		# work begin
		nodesCount += 1

		# node is part of our fittings -- good boy
		if node.name in citizenNodeNames:
			continue

		# node is part of a citizen network domain -- good boy too
		if node.extra['networkDomainId'] in citizenDomainIds:
			continue

		# we found an alien
		aliensCount += 1

		# offer to shutdown running alien nodes
		if node.state is NodeState.RUNNING:
			print("'{}' has been deployed but is not part of our fittings".format(node.name))
			feedback = raw_input('Should this node been stopped? [y/N/q] ').lower()

			# we are asked to shutdown this node
			if len(feedback) > 0 and feedback[0] == 'y':

				if plumbery.safeMode:
					print("Would have stopped node '{}' if not in safe mode".format(node.name))

				else:
					print("Stopping node '{}'".format(node.name))

					# we may have to wait for busy resources
					while True:

						try:
							facility.region.ex_shutdown_graceful(plumbery.region.ex_get_node_by_id(node.id))
							print "- in progress"

						except Exception as feedback:

							# resource is busy, wait a bit and retry
							if 'RESOURCE_BUSY' in str(feedback):
								facility.wait_and_tick()
								continue

							# other exception
							else:
								print("Error: unable to stop node '{}'!".format(node.name))
								print feedback

						# quit the loop
						break


			# quit this loop immediately
			elif len(feedback) > 0 and feedback[0] == 'q':
				break

# report on the hard work
print("{} nodes have been processed in total, including {} alien nodes".format(nodesCount, aliensCount))




