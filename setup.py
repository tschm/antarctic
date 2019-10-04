#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='antarctic',
    version='0.0.1',
    packages=find_packages(include=["antarctic*"]),
    author='Thomas Schmelzer',
    author_email='thomas.schmelzer@gmail.com',
    description='', install_requires=['requests>=2.21.0', 'pandas>=0.24.0', 'pymongo', 'pyarrow>=0.14.1'],
    license='LICENSE.txt'
)
