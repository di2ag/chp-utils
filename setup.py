"""Setup file for  chp-utils"""
from setuptools import setup, find_packages

with open('README.md', 'r') as stream:
    long_description = stream.read()

setup(
    name = 'chp_utils',
    version = '0.1.0',
    author = 'Luke Veenhuis',
    author_email = 'luke.j.veenhuis@dartmouth.edu',
    url = 'https://github.com/di2ag/chp_utils',
    description = 'A set of tools for any chp api',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    packages = find_packages(),
    package_data = {
        'chp_utils.schemas':['*.json']
    },
    include_package_data = True,
    install_requires=[],
    zip_safe=False,
    python_requires='>=3.6'
)
