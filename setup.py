#!/usr/bin/env python3
"""
Setup configuration for bank-analyzer
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bank-analyzer",
    version="0.1.0",
    author="Utilisateur",
    description="Outil d'analyse personnelle des relevés bancaires",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/bank-analyzer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.9",
)
