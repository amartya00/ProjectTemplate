from setuptools import setup
from os import path
from io import open
import sys

here = path.abspath(path.dirname(__file__))

version_maj = sys.version_info[0]
version_min = sys.version_info[1]

if version_maj < 3:
    sys.exit("Need python 3 to run. You are trying to install this with python " + str(version_maj) + "." + str(version_min))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="bob",
    version="1.6",
    description="A python based build system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amartya00/ProjectTemplate",  # Optional
    author="Amartya Datta Gupta",
    author_email="amartya00@gmail.com",  # Optional
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: GPLV2',
        'Programming Language :: Python :: 3.6',
    ],
    packages=["modules", "modules.bootstrap", "modules.build", "modules.config", "modules.workflow", "modules.package"],
    install_requires=["boto3", "botocore"],
    extras_require={
        'dev': [],
        'test': ["coverage"],
    },
    entry_points={
        "console_scripts": [
            "bob=modules:main",
        ],
    },
    project_urls={
        "Source": "https://github.com/amartya00/ProjectTemplate"
    },
)
