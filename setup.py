import os
import sys
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "celerium",
    version = "0.1",
    author = "Alexander Koval",
    author_email = "kovalidis@gmail.com",
    description = ("A library to use solr in python projects."),
    license = "BSD",
    keywords = "celery events monitoring solr solar",
    url = "https://github.com/anti-social/celerium",
    packages=find_packages(exclude=["tests.*", "tests"]),
    long_description=read("README.rst"),
    entry_points = {
        'console_scripts': [
            'celerium = celery.manage:manager.run',
         ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
