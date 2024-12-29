import os

import re

# Implements this:
# https://stackoverflow.com/a/7071358/441652
version_file = "src/argrelay/_version.py"
version_content = open(version_file, "rt").read()
version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
regex_match = re.search(version_regex, version_content, re.M)
if regex_match:
    version_string = regex_match.group(1)
else:
    raise RuntimeError(f"Unable to find version string: ${version_file}")

import setuptools

tests_require = [
    "tox",
    "responses",
    "mongomock",
    "pandas",
    "icecream",
    "jsonpath-ng",
]

# To install these extra dev dependencies:
# pip install --editable .[tests]
extras_require = {
    "tests": tests_require,
}


def list_dir(
    # Path relative to the `setup.py` (relative to the repo root `@/`):
    top_dir_path,
):
    file_paths = []
    for (parent_dir_path, child_dir_names, child_file_names) in os.walk(top_dir_path):
        for child_file_name in child_file_names:
            file_paths.append(os.path.join(
                parent_dir_path,
                child_file_name,
            ))
    # All paths start with `top_dir_path`:
    return file_paths


setuptools.setup(
    name = "argrelay",
    version = version_string,
    author = "uvsmtid",
    author_email = "uvsmtid@gmail.com",
    description = "A data server to CLI tools with attribute search & Tab-completion in Bash shell",
    long_description = """
See: https://github.com/argrelay/argrelay
    """,
    long_description_content_type = "text/markdown",
    keywords = "argparse, argcomplete, bash, complete",
    url = "https://github.com/argrelay/argrelay",
    project_urls = {
        "Bug Tracker": "https://github.com/argrelay/argrelay/issues",
    },
    classifiers = [
        "Development Status :: 3 - Alpha",

        "Environment :: Console",
        "Framework :: Flask",
        "Intended Audience :: Information Technology",

        "Topic :: Terminals",
        "Topic :: System :: Shells",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Text Processing :: Indexing",

        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: Apache Software License",

        "Operating System :: POSIX :: Linux",
    ],
    # See sample layout:
    # https://docs.python.org/3/distutils/setupscript.html#installing-package-data
    packages = (
        setuptools.find_packages(
            where = "src",
        ) + [
            "argrelay_docs",
        ]
    ),
    # See:
    # https://docs.python.org/3/distutils/setupscript.html#listing-whole-packages
    # Instead of specifying directory of the specific package:
    # "argrelay": "src/argrelay",
    # Specify directory of "root" package:
    # "": "src",
    # Apparently, this makes `argrelay.egg-info` dir appear in `src` on editable mode rather than in root `.`.
    package_dir = {
        "": "./src/",
        "argrelay_docs": "./",
        "argrelay_data": "./",
    },
    package_data = {
        "argrelay": [

            # Config files:
            "sample_conf/argrelay_client.json",
            "sample_conf/argrelay_server.yaml",
            "sample_conf/argrelay_plugin.yaml",
            "sample_conf/check_env_plugin.conf.bash",
            "sample_conf/check_env_plugin.conf.yaml",

            # GUI client:
            "relay_server/gui_static/argrelay_client.js",
            "relay_server/gui_static/argrelay_favicon_16.ico",
            "relay_server/gui_static/argrelay_style.css",
            "relay_server/gui_static/external_link.svg",
            "relay_server/gui_templates/argrelay_main.html",

            # Other resource files:
            "custom_integ_res/argrelay_common_lib.bash",
            "custom_integ_res/shell_env.bash",
            "custom_integ_res/bootstrap_env.bash",
            "custom_integ_res/check_env.bash",
            "custom_integ_res/dev_shell.bash",
            "custom_integ_res/init_shell_env.bash",
            "custom_integ_res/upgrade_env_packages.bash",

            # Files in `script_plugin.d`:
            "custom_integ_res/script_plugin.d/check_env_plugin.all_argrelay_plugins.bash",
            "custom_integ_res/script_plugin.d/check_env_plugin.bash_version.bash",
            "custom_integ_res/script_plugin.d/check_env_plugin.git_version.bash",

        ],
        "argrelay_docs": list_dir("./docs/") + [
            "readme.md",
        ],
        "argrelay_data": list_dir("./data/"),
    },
    include_package_data = True,
    python_requires = ">=3.8",
    install_requires = [
        "Flask",
        "Werkzeug",
        "PyYaml",
        "jsonschema",
        "flasgger",
        "marshmallow",
        "marshmallow-oneofschema",
        "apispec",
        "pymongo",
        "GitPython",
        # Use `mongomock` as replacement for Mongo DB in simple prod cases:
        "mongomock",
        "requests",
        "cachetools",
    ],
    tests_require = tests_require,
    extras_require = extras_require,
)
