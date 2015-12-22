====================================
How to contribute to Plumbery?
====================================

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You are not a developer? We are glad that you are involved
----------------------------------------------------------

You can contribute in many ways:

* submit feedback
* report bugs
* write documentation
* fix bugs
* implement features

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue. The place to go is
`Plumbery issues at GitHub`_. There you can check if your feedback is new, or
if you can align with others.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Report Bugs
~~~~~~~~~~~

Have you identified some bug? Thanks to go to `Plumbery issues at GitHub`_.
This is the place where issues are documented, discussed, and fixed. We really
value your time and effort to report bugs.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Plumbery could always use more documentation, whether as part of the
official plumbery docs, in docstrings, or even on the web in blog posts,
articles, and such.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Ready to contribute? Here's how to set up Plumbery for local development
------------------------------------------------------------------------

1. Fork the `plumbery` repo on `GitHub`_. If you do not have an account there
   yet, you have to create one, really. This is provided for free, and will
   make you a proud member of a global community that matters. Once you have
   authenticated, visit the `Plumbery repository at GitHub`_ and click
   on the `Fork` link.

2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/plumbery.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper
   installed, this is how you set up your fork for local development::

    $ mkvirtualenv plumbery
    $ cd plumbery/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the tests::

    $ make lint
    $ make test
    $ make coverage

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.

2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in ``README.rst``.

3. Check `Plumbery continuous integration at Travis CI`_
   and make sure that the tests pass there.

.. _`GitHub`: https://github.com/
.. _`Plumbery repository at GitHub`: https://github.com/bernard357/plumbery
.. _`Plumbery issues at GitHub`: https://github.com/bernard357/plumbery/issues
.. _`Plumbery continuous integration at Travis CI`: https://travis-ci.org/bernard357/plumbery
