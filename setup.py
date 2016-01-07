#!/usr/bin/env python
'''
    Package build script
'''

import os
import sys
import setuptools

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.remove(CURRENT_DIRECTORY)
sys.path.insert(0, os.path.join(CURRENT_DIRECTORY, 'cozy_management'))

# from setuptools import setup, find_packages

setuptools.setup(
    name='cozy_management',
    version='0.0.4',
    description='Module to help self hosted cozy management',
    long_description=open('README.md').read(),
    author='Cozy Cloud',
    author_email='contact@cozycloud.cc',
    url='https://github.com/cozy/python_cozy_management',
    keywords=['cozy'],
    license='LGPL',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'cozy_management = cozy_management.cli:main'
        ]
    },
    install_requires=['docopt', 'requests'],
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
    ]
)
