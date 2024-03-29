#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name="jirareports",
    version="0.1",
    packages=find_packages(),
    namespace_packages=['jirareports'],
    install_requires=[
        'SOAPpy',
        'suds'
    ]
)
