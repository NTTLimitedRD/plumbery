#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import join as pjoin
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


requirements = ['libcloud']

test_requirements = [
    # TODO: put package test requirements here
]

# get version from package itself
def get_version():
    version = None
    sys.path.insert(0, pjoin(os.getcwd()))
    from plumbery import __version__
    version = __version__
    sys.path.pop(0)
    return version

# get description from README.rst
def get_long_description():
    description = ''
    with open('README.rst') as stream:
        description = stream.read()
    return description

setup(
    name='plumbery',
    version=get_version(),
    description="Cloud automation at Dimension Data with Apache Libcloud",
    long_description=get_long_description(),
    author="Bernard Paques",
    author_email='bernard.paques@gmail.com',
    url='https://github.com/bernard357/plumbery',
    packages=['plumbery'],
    package_dir={'plumbery': 'plumbery'},
    include_package_data=True,
    install_requires=requirements,
    license='Apache License (2.0)',
    zip_safe=False,
    keywords='plumbery',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    test_suite='tests',
    tests_require=test_requirements
)
