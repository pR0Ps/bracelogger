#!/usr/bin/env python

from setuptools import setup
import os.path


try:
    DIR = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(DIR, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = None


setup(
    name="bracelogger",
    version="1.0.0",
    description="Use brace-style string formatting in log messages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pR0Ps/bracelogger",
    license="LGPLv3",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: Developers",
        "Topic :: System :: Logging",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    ],
    py_modules=["bracelogger"],
    extras_require={
        "tests": ["pytest", "pytest-cov"],
    },
)
