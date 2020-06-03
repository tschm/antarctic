#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='antarctic',
    version='0.0.1',
    packages=find_packages(include=["antarctic*"]),
    author='Thomas Schmelzer',
    author_email='thomas.schmelzer@gmail.com',
    description='', install_requires=['requests>=2.23.0', 'pandas>=0.25.3', 'pymongo'],
    license='LICENSE.txt'
)
