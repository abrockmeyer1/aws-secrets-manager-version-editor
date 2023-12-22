from setuptools import setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sm-version-editor",
    version="0.0.1",
    description="Manage AWS Secrets Manager secret versions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aaron Brockmeyer",
    author_email="abrockme@gmail.com",
    packages=["sm_version_editor"],
    scripts=["smve"],
    entry_points={
        "console_scripts": [
            "smve=smve:cli",
        ],
    },
    install_requires=["boto3", "Click", "tabulate"],
)
