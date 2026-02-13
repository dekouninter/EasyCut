# -*- coding: utf-8 -*-
"""
Setup script para EasyCut
Para empacotar: python setup.py py2exe
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="EasyCut",
    version="1.0.0",
    author="Deko Costa",
    description="YouTube Video Downloader and Audio Converter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dekouninter/EasyCut",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.8",
    install_requires=[
        "yt-dlp>=2024.3.10",
        "keyring>=24.0.0",
    ],
    extras_require={
        "dev": [
            "pyinstaller>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "easycut=src.easycut:main",
        ],
    },
)
