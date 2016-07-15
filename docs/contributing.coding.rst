How to code for or with Plumbery?
=================================

This page describes Plumbery development process and contains general
guidelines and information on how to contribute to the project.

If you are looking for the code itself, you could look at documentation
extracted from pyton source files: :ref:`modindex` and :ref:`genindex`. And then
of course there is the `Plumbery repository at GitHub`_ to browse everything.

We welcome contributions of any kind (ideas, code, tests, documentation,
examples, ...). Everything that is given to the community will be governed
by the `Apache License (2.0)`_.

* Any non-trivial change must contain tests. For more information, refer to the
  :ref:`Testing <test-conventions>` section below.
* All the functions and methods must contain Sphinx docstrings which are used
  to generate the API documentation. For more information, refer to the
  :ref:`Docstring conventions <docstring-conventions>` section below.
* If you are adding a new feature, make sure to add a corresponding
  documentation.

Code style guide
----------------

* We follow `PEP8 Python Style Guide`_
* Use 4 spaces for a tab
* Use 79 characters in a line
* Make sure edited file doesn't contain any trailing whitespace
* You can verify that your modifications don't break any rules by running the
  ``flake8`` script - e.g. ``flake8 plumbery/edited_file.py`` or
  ``make lint``.
  Second command will run flake8 on all the files in the repository.

And most importantly, follow the existing style in the file you are editing and
**be consistent**.

.. _code-conventions:

Code conventions
----------------

This section describes some general code conventions you should follow when
writing code for Plumbery.

Import ordering
~~~~~~~~~~~~~~~

Organize the imports in the following order:

1. Standard library imports
2. Third-party library imports
3. Local library (plumbery) imports

Each section should be separated with a blank line. For example:

.. sourcecode:: python

    import sys
    import base64

    import paramiko

    from plumbery.polisher import PlumberyPolisher
    from plumbery.nodes import PlumberyNodes

Function and method ordering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions in a module and methods on a class should be organized in the
following order:

1. "Public" functions / methods
2. "Private" functions / methods (methods prefixed with an underscore)
3. "Internal" methods (methods prefixed and suffixed with a double underscore)

For example:

.. sourcecode:: python

    class Unicorn(object):
        def __init__(self, name='fluffy'):
            self._name = name

        def make_a_rainbow(self):
            pass

        def _get_rainbow_colors(self):
            pass

        def __eq__(self, other):
            return self.name == other.name

Methods on a polisher class should be organized in the following order:

1. Methods which are part of the standard API
2. Extension methods
3. "Private" methods (methods prefixed with an underscore)
4. "Internal" methods (methods prefixed and suffixed with a double underscore)

Methods which perform a similar functionality should be grouped together and
defined one after another.

For example:

.. sourcecode:: python

    class MyPolisher(object):
        def __init__(self):
            pass

        def go(self, engine):
            pass

        def move_to(self, facility):
            pass

        def shine_container(self, container):
            pass

        def shine_node(self, node, settings, container):
            pass

        def ex_proud_extension(self):
            pass

        def _to_representation(self, stuff):
            pass


Methods should be ordered this way for the consistency reasons and to make
reading and following the generated API documentation easier.

Prefer keyword over regular arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For better readability and understanding of the code, prefer keyword over
regular arguments.

Good:

.. sourcecode:: python

    some_method(public_ips=public_ips, private_ips=private_ips)

Bad:

.. sourcecode:: python

    some_method(public_ips, private_ips)

Don't abuse \*\*kwargs
~~~~~~~~~~~~~~~~~~~~~~

You should always explicitly declare arguments in a function or a method
signature and only use ``**kwargs`` and ``*args`` respectively when there is a
valid use case for it.

Using ``**kwargs`` in many contexts is against Python's "explicit is better
than implicit" mantra and makes it for a bad and a confusing API. On top of
that, it makes many useful things such as programmatic API introspection hard
or impossible.

A use case when it might be valid to use ``**kwargs`` is a decorator.

Good:

.. sourcecode:: python

    def my_method(self, name, description=None, public_ips=None):
        pass

Bad (please avoid):

.. sourcecode:: python

    def my_method(self, name, **kwargs):
        description = kwargs.get('description', None)
        public_ips = kwargs.get('public_ips', None)

When returning a dictionary, document its structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dynamic nature of Python can be very nice and useful, but if (ab)use it in a
wrong way it can also make it hard for the API consumer to understand what is
going on and what kind of values are being returned.

If you have a function or a method which returns a dictionary, make sure to
explicitly document in the docstring which keys the returned dictionary
contains.

Prefer to use "is not None" when checking if a variable is provided or defined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When checking if a variable is provided or defined, prefer to use
``if foo is not None`` instead of ``if foo``.

If you use ``if foo`` approach, it's easy to make a mistake when a valid value
can also be falsy (e.g. a number ``0``).

For example:

.. sourcecode:: python

    class SomeClass(object):
        def some_method(self, domain=None):
            params = {}

            if domain is not None:
                params['Domain'] = domain

.. _docstring-conventions:

Docstring conventions
---------------------

For documenting the API we we use Sphinx and reStructuredText syntax. Docstring
conventions to which you should adhere to are described below.

* Docstrings should always be used to describe the purpose of methods,
  functions, classes, and modules.
* Method docstring should describe all the normal and keyword arguments. You
  should describe all the available arguments even if you use ``*args`` and
  ``**kwargs``.
* All parameters must be documented using ``:param p:`` or ``:keyword p:``
  and ``:type p:`` annotation.
* ``:param p: ...`` -  A description of the parameter ``p`` for a function
  or method.
* ``:keyword p: ...`` - A description of the keyword parameter ``p``.
* ``:type p: ...`` The expected type of the parameter ``p``.
* Return values must be documented using ``:return:`` and ``:rtype``
  annotation.
* ``:return: ...`` A description of return value for a function or method.
* ``:rtype: ...`` The type of the return value for a function or method.
* Required keyword arguments must contain ``(required)`` notation in
  description. For example: ``:keyword image:  OS Image to boot on node. (required)``
*  Multiple types are separated with ``or``
   For example: ``:type auth: :class:`.NodeAuthSSHKey` or :class:`.NodeAuthPassword```
* For a description of the container types use the following notation:
  ``<container_type> of <objects_type>``. For example:
  ``:rtype: `list` of :class:`Node```

For more information and examples, please refer to the following links:

* Sphinx Documentation - http://sphinx-doc.org/markup/desc.html#info-field-lists

.. _test-conventions:

Testing
-------

Running all tests
~~~~~~~~~~~~~~~~~

To run the tests manually, you first need to install all of the dependencies
mentioned above. After that simply go to the root of the repository and use the
following command:

.. sourcecode:: bash

    PYTHONPATH=. make test


Running one test file
~~~~~~~~~~~~~~~~~~~~~

To run the tests located in a single test file, move to the root of the
repository and run the following command:

.. sourcecode:: bash

    PYTHONPATH=. python tests/<path to test file>

For example:

.. sourcecode:: bash

    PYTHONPATH=. python tests/test_engine.py


Generating test coverage report
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To generate the test coverage run the following command:

.. sourcecode:: bash

    PYTHONPATH=. make coverage

When it completes you should see a new ``coverage_html_report`` directory which
contains the test coverage.


.. _`PEP8 Python Style Guide`: http://www.python.org/dev/peps/pep-0008/
.. _`Plumbery repository at GitHub`: https://github.com/bernard357/plumbery
.. _`Apache License (2.0)`: http://www.apache.org/licenses/LICENSE-2.0
