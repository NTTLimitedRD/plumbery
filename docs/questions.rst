Frequently asked questions
==========================

About project governance
------------------------

Where is this project coming from?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The plumbery project is an initiative from software teams of Dimension Data. It has been created by orchestration experts in Europe, and has been endorsed by the global research and development organisation.

Is this software available to anyone?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. The software and the documentation have been open-sourced from the outset, so that it can be useful to the global community of IoT and of digital practioners. The plumbery project is based on the [Apache License](https://www.apache.org/licenses/LICENSE-2.0).

Do you accept contributions to this project?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. There are multiple ways for end-users and for non-developers to contribute to this project. For example, if you hit an issue, please report it at GitHub. This is where we track issues and report on corrective actions.

And if you know [how to clone a GitHub project](https://help.github.com/articles/cloning-a-repository/), we are happy to consider [pull requests](https://help.github.com/articles/about-pull-requests/) with your modifications. This is the best approach to submit additional reference configuration files, or updates of the documentation, or even evolutions of the python code.

About project deployment
------------------------

How to install the full system?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use [detailed instructions](installing.rst) that explain what you have to do step by step.

Is it required to know python?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fortunately not. Plumbery makes extensive usage of separate configuration files that can be modified at will.

About troubleshooting
---------------------

How to troubleshoot cloud-init?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect to the target server over SSH. Then check the existence and content of the cloud-init log file::

    $ less /var/log/cloud-init-output.log

If the file does not exist, or if its content does not reflect statements put in the plumbery configuration file, then you can inspect user data that have been uploaded, and then run cloud-init manually::

    $ cd /var/lib/cloud/seed/nocloud-net/
    $ less user-data
    $ sudo cloud-init --debug --file user-data single

Check error messages thrown by cloud-init and react accordingly.
