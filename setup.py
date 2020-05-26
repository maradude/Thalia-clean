"""A setuptools based setup module."""
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

install_requires = [
    "flask",
    "flask-login >= 0.5",
    "flask-migrate",
    "flask-wtf",
    "pandas",
    "dash",
    "humanize",
]


tests_require = ["pytest", "coverage"]

extras_require = {"dev": ["black", "flake8", "pre-commit", "selenium"], "test": tests_require}

setup(
    name="Thalia",
    version="0.3.0",
    packages=find_packages(),
    install_requires=install_requires,
    extras_require=extras_require,
)
