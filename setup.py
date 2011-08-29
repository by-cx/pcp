#!/usr/bin/python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "wsgiadmin",
    version = "0.1.0",
    author = "Adam Strauch",
    author_email = "cx@initd.cz",
    description = ("Webhosting administration"),
    license = "BSD",
    keywords = "hosting administration webhosting email",
    url = "https://github.com/creckx/pcp",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    package_data = {"": ["*.html", "*.conf"]},
    include_package_data = True,
    install_requires=[
        
        ],
    entry_points="""
    [console_scripts]
    wsgiadmin-manage = wsgiadmin.manage:main
    """
)
