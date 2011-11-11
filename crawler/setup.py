#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name="jira-crawler",
    version="0.1",
    description="JIRA Crawler Daemon",
    packages=find_packages(exclude=[
            "*.test", "*.test.*", "test.*", "test",
            "*.integration_test", "*.integration_test.*", "integration_test.*", "integration_test"]),
    data_files=[("conf", ['conf/logging.conf'])],
    install_requires=[
    ],
    dependency_links = [
    ],
    entry_points={
        'console_scripts': [
        ],
    },
    classifiers=[
            'Environment :: Console',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
    ],
)
