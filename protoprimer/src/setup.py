import os

import re

# The "distribution root" refers to the top-level directory where the code resides.
# It is the root directory that contains the `setup.py` file itself.
# When installed, `setup.py` will run from the extracted archive:
distrib_root = os.path.dirname(os.path.abspath(__file__))

# Implements this (using the single script directly without a separate `_version.py` file):
# https://stackoverflow.com/a/7071358/441652
version_file = f"{distrib_root}/main/protoprimer/proto_code.py"
version_content = open(version_file, "rt").read()
version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
regex_match = re.search(version_regex, version_content, re.M)
if regex_match:
    version_string = regex_match.group(1)
else:
    raise RuntimeError(f"Unable to find version string: ${version_file}")

import setuptools

tests_require = [
    "pyfakefs",
]

# To install these extra dev dependencies:
# pip install --editable "${client_dir}/"[test]
extras_require = {
    "test": tests_require,
}


setuptools.setup(
    name="protoprimer",
    version=version_string,
    author="uvsmtid",
    author_email="uvsmtid@gmail.com",
    description="bootstrap environment",
    keywords="boot env bootstrap environment dev",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Topic :: Terminals",
        "Topic :: System :: Shells",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    # See the sample layout:
    # https://docs.python.org/3.8/distutils/setupscript.html#installing-package-data
    # List all packages/sub-packages (so that they are taken by `package_dir` below):
    packages=setuptools.find_packages(
        where=f"{distrib_root}/main/",
    ),
    # See:
    # https://docs.python.org/3.8/distutils/setupscript.html#listing-whole-packages
    #     The keys to this dictionary are package names,
    #     and an empty package name stands for the root package.
    #     The values are directory names relative to your distribution root.
    #     See "distribution root" above - during installation, `setup.py` will run from the extracted archive.
    package_dir={
        "protoprimer": "./main/protoprimer/",
        # TODO: Move under "protoprimer"?
        "test_support": "./main/test_support/",
    },
    # See:
    # https://docs.python.org/3.8/distutils/setupscript.html#installing-package-data
    #     The paths are interpreted as relative to the directory containing the package
    #     (information from the `package_dir` mapping is used if appropriate);
    #     that is, the files are expected to be part of the package in the source directories.
    package_data={
        "protoprimer": [],
        # TODO: Move under "protoprimer"?
        "test_support": [],
    },
    include_package_data=False,
    # FS_84_11_73_28: supported python versions:
    python_requires=">=3.9",
    install_requires=[],
    extras_require=extras_require,
)
