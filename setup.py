# -*- coding: utf-8 -*-
"""
Setup script for EasyCut
For packaging: python setup.py sdist bdist_wheel
"""


from setuptools import setup, find_packages
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from __version__ import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="EasyCut",
    version=__version__,
    author="Deko Costa",
    description="YouTube Video Downloader and Audio Converter with OAuth Authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dekouninter/EasyCut",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.10",
    install_requires=[
        "yt-dlp>=2024.3.10",
        "keyring>=24.0.0",
        "pillow>=10.0.0",
        "google-auth-oauthlib>=1.2.0",
        "google-auth-httplib2>=0.3.0",
        "requests>=2.32.0",
    ],
    extras_require={
        "dev": [
            "pyinstaller>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "easycut=main:main",
        ],
    },
)
