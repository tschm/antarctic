#!/usr/bin/env python
from setuptools import setup, find_packages
from antarctic import __version__ as version

# read the contents of your README file
with open('README.md') as f:
    long_description = f.read()

setup(
    name='antarctic',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=version,
    packages=find_packages(include=["antarctic*"]),
    author='Thomas Schmelzer',
    author_email='thomas.schmelzer@gmail.com',
    url='https://github.com/tschm/antarctic',
    description='Storing Pandas Data in a MongoDB database',
    install_requires=['pandas>=0.25.3', 'pymongo>=3.10.1', 'mongoengine>=0.19.1'],
    license='MIT'
)
