#!/usr/bin/env python
'''
Setup script to create a pip/pypi package via setuptools.
'''

from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().strip().split('\n')

with open('requirements-dev.txt') as f:
    requirements_dev = f.read().strip().split('\n')

setup(

    #
    # Package informations
    #

    name='cryptobob',

    description='CryptoBob package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    use_scm_version=True,

    author='Dominique Barton',

    license='MIT',

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

    #
    # Package content
    #

    packages=[
        'cryptobob',
    ],

    entry_points={
        'console_scripts': [
            'cryptobob=cryptobob.cli:main',
        ],
    },

    include_package_data=True,

    #
    # Requirements
    #

    python_requires='>=3.11',

    setup_requires=[
        'setuptools_scm',
    ],

    install_requires=requirements,

    extras_require={
        'dev': requirements_dev
    },

)
