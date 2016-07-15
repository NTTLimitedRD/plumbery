Using Plumbery as a python library
==================================

Since Plumbery is easy to load, you can use it interactively like in the
following example:

.. sourcecode:: python

    >>>from plumbery.engine import PlumberyEngine
    >>>PlumberyEngine('fittings.yaml').build_blueprint('beachhead control')
    ...

If you are writing some code using Plumbery as a library, you would import
the engine and use it, as with any other python module. For example:

.. sourcecode:: python

    from plumbery.engine import PlumberyEngine

    engine = PlumberyEngine('fittings.yaml')
    engine.do('build', 'docker')
    engine.do('start', 'docker')
    engine.do('prepare', 'docker')


The source code is available on-line, check the `Plumbery repository at GitHub`_.


.. _`YAML`: https://en.wikipedia.org/wiki/YAML
.. _`available on PyPi`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery package at PiPy`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery repository at GitHub`: https://github.com/bernard357/plumbery
.. _`download the reference fittings plan`: https://raw.githubusercontent.com/bernard357/plumbery/master/demos/fittings.yaml


