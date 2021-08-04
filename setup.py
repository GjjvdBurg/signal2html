#!/usr/bin/env python
# -*- coding: utf-8 -*-


import io
import os

from setuptools import find_packages
from setuptools import setup

# Package meta-data.
NAME = "signal2html"
DESCRIPTION = "Convert your Signal backup to pretty HTML"
URL = "https://github.com/GjjvdBurg/signal2html"
EMAIL = "gertjanvandenburg@gmail.com"
AUTHOR = "Gertjan van den Burg"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = None

# What packages are required for this module to be executed?
REQUIRED = [
    "emoji",
    "jinja2",
    'dataclasses;python_version=="3.6"',
    "pure-protobuf",
    "linkify-it-py",
]

docs_require = []
test_require = []
dev_require = ["green", "black", "isort"]

# What packages are optional?
EXTRAS = {
    "docs": docs_require,
    "tests": test_require,
    "dev": docs_require + test_require + dev_require,
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    entry_points={
        "console_scripts": ["signal2html=signal2html.__main__:main"],
    },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
