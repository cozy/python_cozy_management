#!/usr/bin/env python

import os
import sys

current_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.remove(current_directory)
sys.path.insert(0, os.path.join(current_directory, 'cozy_management'))

from setuptools import setup, find_packages
from version import VERSION

setup(name='cozy_management',
      version=VERSION,
      description='Module to help self hosted cozy management',
      long_description=open('README.md').read(),
      author='Cozy Cloud',
      author_email='contact@cozycloud.cc',
      url='https://github.com/cozy/python_cozy_management',
      keywords=['cozy'],
      license='LGPL',
      packages=find_packages(),
      install_requires=['requests'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'License :: OSI Approved :: ' +
          'GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
      ],
      )
