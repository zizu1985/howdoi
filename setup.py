#!/usr/bin/env python

from setuptools import setup, find_packages
import howdoi
import os

# For dependency list add argparse when Python version < 2.7.
# Retrun list for extra installation -> [] or ['argparse']
def extra_dependencies():
    import sys
    return ['argparse'] if sys.version_info < (2, 7) else []


# From list of files suffix build dict which would be used
# to create long_description in package metadata.
# Files have to end with txt or rst suffix. First is taken. If not give string "No description for <name> found."
def read(*names):
    values = dict()
    for name in names:
        value = 'No description for {0} found!'.format(name)
        for extension in ('.txt', '.rst'):
            filename = name + extension
            if os.path.isfile(filename):
                with open(filename) as in_file:
                    value = in_file.read()
                break
        values[name] = value
    return values

# Description used in application metadata.
# String formatting used.
long_description = """
%(README)s

News
====

%(CHANGES)s

""" % read('README', 'CHANGES')

# Using <package>.__version__ is ok, because find_packages()
# function is used, so it clasify package if it has __init__.py file
setup(
    name='howdoi',
    version=howdoi.__version__,
    description='Instant coding answers via the command line',
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Documentation",
    ],
    keywords='howdoi help console command line answer',
    author='Benjamin Gleitzman',
    author_email='gleitz@mit.edu',
    maintainer='Benjamin Gleitzman',
    maintainer_email='gleitz@mit.edu',
    url='https://github.com/gleitz/howdoi',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'howdoi = howdoi.howdoi:command_line_runner',
        ]
    },
    install_requires=[
        'pyquery',
        'pygments',
        'requests',
        'requests-cache'
    ] + extra_dependencies(),
)
