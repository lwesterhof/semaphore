#!/usr/bin/env python
from setuptools import find_packages, setup

from semaphore import __author__, __email__, __license__, __version__

# Get the long description from the README file
with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'attrs==18.2.0',
    'attr==0.3.1',
    'python_dateutil==2.8.1',
]

setup(
    name="semaphore",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description=(
        "Semaphore: A simple (rule-based) bot library for Signal Private Messenger."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lwesterhof/semaphore",
    license=__license__,
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.6',
    project_urls={
        'Bug Reports': 'https://github.com/lwesterhof/semaphore/issues',
        'Source': 'https://github.com/lwesterhof/semaphore',
    },
)
