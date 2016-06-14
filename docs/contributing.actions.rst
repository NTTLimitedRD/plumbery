How to extend Plumbery with polishers?
======================================

Polishers are the foreseen extension mechanism for plumbery. It allows anyone to create a python script derived from PlumberyPolisher,
and ask plumbery to invoke it from the command line. Plumbery will look at every live node and pass it to the polisher.
Functionally, it is equivalent to “for node in listAllNodes(): polish(node)”.

For the time being, plumbery has 4 polishers:
- configure – this polisher is launched automatically by plumbery when blueprints are built. It wait for nodes to be created, then assign IP public addresses, manages pools for load balancers, and the like
- ansible – this polisher builds an inventory file that can be used directly with ansible. Quite useful if ansible and plumbery have been installed on the same machine…
- inventory – dump a YAML inventory of all known information about nodes. This could be put in a database, or used for inspection…
- prepare – execute post-start commands via ssh

Prepare can be quite useful, yet it is not intended to supplement an efficient configuration management system.
For example, ansible can be far more efficient in installing and configuring docker than plumbery is.
Maybe we should limit prepare to configure some client software in a global configuration system.
For example: install a chef client and provide the IP address of the chef server. Or do the same with Puppet, etc. You get the idea.

