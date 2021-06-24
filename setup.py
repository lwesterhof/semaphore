#!/usr/bin/env python
import importlib
import importlib.util
from pathlib import Path
from setuptools import find_packages, setup


def import_by_path(module_name, path):
    """Import the module name and not its parent package.
    Return the module.
    """
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


meta = import_by_path('meta', Path(__file__).parent / 'semaphore' / 'meta.py')

# Get the long description from the README file
with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'anyio<3.0.0',
    'attrs==18.2.0',
    'python_dateutil==2.8.1',
]

setup(
    name="semaphore-bot",
    version=meta.__version__,
    author=meta.__author__,
    author_email=meta.__email__,
    description=(
        "Semaphore: A simple (rule-based) bot library for Signal Private Messenger."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lwesterhof/semaphore",
    license=meta.__license__,
    packages=find_packages(),
    install_requires=requirements,
    extras_require={'dev': [
        'flake8',
        'flake8-import-order',
        'darglint',
        'mypy',
        'types-python-dateutil',
        'sphinx',
        'sphinx_rtd_theme',
    ]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        (
            'License :: OSI Approved :: '
            'GNU Affero General Public License v3 or later (AGPLv3+)'
        ),
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    project_urls={
        'Bug Reports': 'https://github.com/lwesterhof/semaphore/issues',
        'Source': 'https://github.com/lwesterhof/semaphore',
    },
)
