#!/usr/bin/env python

import setuptools

import snptk.release

install_requires = [
]

setuptools.setup(
    name='snptk',
    url='https://github.com/usf-hii/snptk',
    version=snptk.release.__version__,
    description='Helps analyze,translate SNP entries from NCBI dbSNP and others',
    author='Kevin Counts',
    author_email='counts@digicat.org',
    license='GPLv3',
    packages=[
        'snptk',
    ],
    entry_points={
        'console_scripts': [
            'snptk = snptk.cli:main',
        ]
    },
    install_requires=install_requires
)
