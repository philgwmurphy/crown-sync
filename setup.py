#!/usr/bin/env python3
"""Setup script for Crown Land Atlas tool."""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='crown-land-atlas',
    version='1.0.0',
    description='Tool to access Ontario Crown Land Use Policy Atlas data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Crown Land Atlas Tool',
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'crown-land-atlas=__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: GIS',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
