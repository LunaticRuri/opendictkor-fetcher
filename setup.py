from setuptools import setup, find_packages

import io
from setuptools import find_packages, setup

with open("README.md", 'r') as f:
    long_desc = f.read()

setup(
    name='opendictkor-fetcher',
    version='1.0',
    author='LunaticRuri',
    author_email='nuriyonsei@yonsei.ac.kr',
    description='Fetching data from \'우리말샘\'(https://opendict.korean.go.kr/)',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url='',
    install_requires=[],
    packages=find_packages(),
    python_requires='>=3',
    classifiers=[
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
    ]
)
