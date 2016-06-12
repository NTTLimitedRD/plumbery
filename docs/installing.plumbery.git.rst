Installing plumbery from GitHub
===============================


Maybe you want to upgrade the on-line documentation of Plumbery. For this
you have to edit the `.rst` files that are in the `docs` directory. Or you
want to extend plumbery engine, for a new or special usage.
Or you would like to troubleshoot an issue and put some `print()` statements in
the code. And why not fix a bug or even implement a new feature?

In all these situations, you would like to get a full copy of all files, and
change them at will on your own computer.

Install the plumbery development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some precautions are needed if you really want to contribute to the Plumbery project.
This is not really difficult, if you follow comprehensive instructions provided
at :doc:`contributing`

On the other hand, to dump a full copy of the software then you can clone
the latest development version from `Plumbery repository at GitHub`_:

.. sourcecode:: bash

    $ sudo apt-get install python-pip python-dev git
    $ sudo pip install -e git+https://github.com/bernard357/plumbery.git#egg=plumbery

Remove the plumbery development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type the following command to clean the python runtime:

.. sourcecode:: bash

    $ python setup.py develop --uninstall

Then you have to go back to the directory where plumbery was downloaded,
and remove files by yourself.


.. _`Plumbery repository at GitHub`: https://github.com/bernard357/plumbery


