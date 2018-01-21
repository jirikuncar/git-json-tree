# -*- coding: utf-8 -*-

"""Git-JSON-Tree."""

import os
import re

from setuptools import setup

# Get the version string.  Cannot be done with import!
with open(os.path.join('git_json_tree.py'), 'rt') as f:
    version = re.search(
        '__version__\s*=\s*"(?P<version>.*)"\n',
        f.read()
    ).group('version')

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'coverage>=4.0.0',
    'isort>=4.2.2',
    'mock>=1.0.0',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=2.1.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.6.6',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    extras_require['all'].extend(reqs)

install_requires = [
    'click>=6.7',
    'dulwich>=0.18.6',
]

setup(
    name='git-json-tree',
    version=version,
    url='http://github.com/jirikuncar/git-json-tree/',
    license='MIT',
    author='Jiri Kuncar',
    author_email='jiri.kuncar+gjt@gmail.com',
    description=__doc__,
    long_description=open('README.rst').read(),
    py_modules=['git_json_tree'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    setup_requires=[
        'pytest-runner>=2.6.2',
        'setuptools>=17.1',
    ],
    extras_require=extras_require,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 1 - Planning',
    ],
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points={
        'console_scripts': [
            'git-json-tree = git_json_tree:cli',
        ],
    },
)
