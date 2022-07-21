from setuptools import find_packages, setup

with open("README.md", 'r') as f:
    long_desc = f.read()

setup(
    name='opendictkor-fetcher',
    version='1.0',
    author='LunaticRuri',
    author_email='nuriyonsei@yonsei.ac.kr',
    description='A simple python crawler for fetching \'우리말샘\'(https://opendict.korean.go.kr/)',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url='https://github.com/LunaticRuri/opendictkor-fetcher',
    install_requires=["beautifulsoup4", "tqdm", 'requests', 'urllib3'],
    packages=find_packages(),
    python_requires='>=3',
    classifiers=[
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
