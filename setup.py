#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import join as pjoin
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


requirements = [
    'apache-libcloud',
    'colorlog',
    'netifaces',
    'paramiko',
    'pywinexe',
    'pywinrm',
    'PyYAML',
    'requests',
    'requests_mock']

test_requirements = []

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
    url='https://github.com/DimensionDataCBUSydney/plumbery',
    packages=['plumbery'],
    package_dir={'plumbery': 'plumbery'},
    include_package_data=True,
    install_requires=requirements,
    entry_points = {
        'console_scripts': ['plumbery=plumbery.__main__:main'],
    },
    license='Apache License (2.0)',
    zip_safe=False,
    keywords='plumbery',
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
