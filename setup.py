#!/usr/bin/env python

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FitBridge",
    version="0.4",
    author="Mohsen Tahmasebi",
    author_email="moh53n@moh53n.ir",
    description="A simple script to sync Gadgetbridge exported data to Google Fit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moh53n/FitBridge",
    project_urls={
        "Bug Tracker": "https://github.com/moh53n/FitBridge/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    license='GPLv3',
    install_requires=['requests', 'google-auth-oauthlib==0.4.1', 'google-api-python-client', 'appdirs'],
    entry_points = {
        'console_scripts': [
            'FitBridge = FitBridge:main',
        ],
    },
)