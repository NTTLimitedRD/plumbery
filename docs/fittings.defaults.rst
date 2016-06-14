Using defaults
==============

In the first document of a fittings file, you can add a ``defaults:`` directive. This will contain default attributes for each of the nodes in the blueprints of subsequent documents.

For example:

.. sourcecode:: yaml

    defaults:

      # all nodes will have this description by default
      #
      description: "Deployed using Plumbery"

      # all nodes will have at least these cloud-init settings
      #
      cloud-config:
        ssh_keys:
          rsa_private: |
            {{ key.rsa_private }}
          rsa_public: "{{ key.rsa_public }}"
        users:
          - default
          - name: ubuntu
            sudo: 'ALL=(ALL) NOPASSWD:ALL'
            ssh-authorized-keys:
              - "{{ key.rsa_public }}"
              - "{{ local.rsa_public }}"
        disable_root: true
        ssh_pwauth: false

This will mean that every node deployed will have SSH keys, the ubuntu user, root disabled and a description of "Deployed using plumbery".

Declaring classes of nodes
--------------------------

If the keyword ``default`` is used for the configuration of a node, then plumbery will look for related settings, like in the folloowing example:

.. sourcecode:: yaml

    ---
    defaults:

      master-node:
        description: "this is a master node"

      slave-node:
        description: "this is a slave node"

    ---

    blueprints:

      - masters:

          master01:
            default: master-node
            description: "I am the master"

          master02:
            default: master-node

      - slaves:

          slave01:
            default: slave-node

This approach saves a lot of typings, and avoid duplications. It is recommended when a fittings file is relying on multiple similar nodes.

Declaring default network domain and network
--------------------------------------------

In many cases the same network domain and VLAN are used across multiple blueprints. In that case you are advised to put related definitions only once, in the ``defaults`` section.

Example:

.. sourcecode:: yaml

    ---
    defaults:

      domain:
        name: MyDomain

      ethernet:
        name: MyNetwork

    ---

    location Id: EU6

    blueprints:

      - blueprint1:

          # no need to repeat domain: nor ethernet: here, default settings will apply

    ---

    location Id: NA12

    blueprints:

      - blueprint1:

          # no need to repeat domain: nor ethernet: here, default settings will apply

In the case of multi-geography deployments, this approach ensures that the infrastructure will be configured the same way everywhere.



