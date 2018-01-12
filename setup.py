#!/usr/bin/env python
import platform

from setuptools import setup, find_packages

python_version = platform.python_version().rsplit(".", 1)[0]


install_requires = [
]

if python_version < "3.5":
    install_requires.append("typing>=3.6.1")

setup(
    name="failfast",
    version="0.0.2",
    author="Matias Surdi",
    author_email="matias@surdi.net",
    keywords=["circuitbreaker", "circuit", "breaker"],
    url="https://github.com/ticketea/failfast",
    description="Pythonic Circuit Breaker",
    long_description="Kinesis based python eventbus",
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    platforms="any",
    install_requires=install_requires,
    tests_require=["tox"],
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
)
