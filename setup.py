import os

import re

# The "distribution root" refers to the top-level directory where your project code resides,
# is the root directory that contains the `setup.py` file itself.
# In case of `argrelay`, it may confusingly appear it is equivalent to `argrelay_dir`
# (because it contains `setup.py`), but it is not - when installed, `setup.py` will run from extracted archive:
distrib_root = os.path.dirname(os.path.abspath(__file__))

# Implements this:
# https://stackoverflow.com/a/7071358/441652
version_file = f"{distrib_root}/src/argrelay/_version.py"
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
    "import-linter",
]

# To install these extra dev dependencies:
# pip install --editable "${argrelay_dir}/"[tests]
extras_require = {
    "tests": tests_require,
}


def list_dir(
    top_dir_abs_path,
) -> list[str]:
    """
    List files recursively from `top_dir_abs_path` with paths relative to `top_dir_abs_path`.
    """
    file_rel_paths = []
    for (parent_dir_abs_path, child_dir_names, child_file_names) in os.walk(top_dir_abs_path):
        for child_file_name in child_file_names:
            file_abs_path = os.path.join(
                parent_dir_abs_path,
                child_file_name,
            )
            file_rel_path = os.path.relpath(
                file_abs_path,
                top_dir_abs_path,
            )
            file_rel_paths.append(file_rel_path)
    return file_rel_paths


def prefix_file_rel_paths(
    prefix_rel_path: str,
    file_rel_paths: list[str],
) -> list[str]:
    """
    Prefix every given path in `file_rel_paths` with `prefix_rel_path`.
    """
    file_prefixed_rel_paths = []
    for file_rel_path in file_rel_paths:
        file_prefixed_rel_path = os.path.join(
            prefix_rel_path,
            file_rel_path,
        )
        file_prefixed_rel_paths.append(file_prefixed_rel_path)
    return file_prefixed_rel_paths


argrelay_docs_files = prefix_file_rel_paths(
    "./docs/",
    list_dir(f"{distrib_root}/docs/"),
) + prefix_file_rel_paths(
    "./",
    [
        "readme.md",
    ],
)

argrelay_data_files = prefix_file_rel_paths(
    "./data/",
    list_dir(f"{distrib_root}/data/"),
)

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
    # https://docs.python.org/3.8/distutils/setupscript.html#installing-package-data
    # List all packages/sub-packages (so that they are taken by `package_dir` below):
    packages = setuptools.find_packages(
        where = f"{distrib_root}/src/",
    ) + [
        "argrelay_docs",
        "argrelay_data",
    ],
    # See:
    # https://docs.python.org/3.8/distutils/setupscript.html#listing-whole-packages
    #     The keys to this dictionary are package names,
    #     and an empty package name stands for the root package.
    #     The values are directory names relative to your distribution root.
    #     See "distribution root" above - during
    package_dir = {
        "argrelay":
            "./src/argrelay/",
        "argrelay_api_plugin_abstract":
            "./src/argrelay_api_plugin_abstract/",
        "argrelay_api_plugin_check_env_abstract":
            "./src/argrelay_api_plugin_check_env_abstract/",
        "argrelay_api_plugin_client_abstract":
            "./src/argrelay_api_plugin_client_abstract/",
        "argrelay_api_plugin_server_abstract":
            "./src/argrelay_api_plugin_server_abstract/",
        "argrelay_api_server_cli":
            "./src/argrelay_api_server_cli/",
        "argrelay_app_check_env":
            "./src/argrelay_app_check_env/",
        "argrelay_app_bootstrap":
            "./src/argrelay_app_bootstrap/",
        "argrelay_app_client":
            "./src/argrelay_app_client/",
        "argrelay_app_server":
            "./src/argrelay_app_server/",
        "argrelay_docs":
            "./",
        "argrelay_data":
            "./",
        "argrelay_lib_check_env_plugin_core":
            "./src/argrelay_lib_check_env_plugin_core/",
        "argrelay_lib_root":
            "./src/argrelay_lib_root/",
        "argrelay_lib_server_plugin_check_env":
            "./src/argrelay_lib_server_plugin_check_env/",
        "argrelay_lib_server_plugin_core":
            "./src/argrelay_lib_server_plugin_core/",
        "argrelay_lib_server_plugin_demo":
            "./src/argrelay_lib_server_plugin_demo/",
        "argrelay_schema_config_check_env":
            "./src/argrelay_schema_config_check_env/",
        "argrelay_schema_config_client":
            "./src/argrelay_schema_config_client/",
        "argrelay_schema_config_server":
            "./src/argrelay_schema_config_server/",
        "argrelay_test_infra":
            "./src/argrelay_test_infra/",
    },
    # See:
    # https://docs.python.org/3.8/distutils/setupscript.html#installing-package-data
    #     The paths are interpreted as relative to the directory containing the package
    #     (information from the `package_dir` mapping is used if appropriate);
    #     that is, the files are expected to be part of the package in the source directories.
    package_data = {
        "argrelay": [
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
        "argrelay_app_bootstrap": [
            # Config files:
            "sample_conf/argrelay_client.json",
            "sample_conf/argrelay_server.yaml",
            "sample_conf/argrelay_plugin.yaml",
            "sample_conf/check_env_plugin.conf.bash",
            "sample_conf/check_env_plugin.conf.yaml",
        ],
        "argrelay_app_server": [
            # GUI client:
            "argrelay_app_server/relay_server/gui_static/argrelay_client.js",
            "argrelay_app_server/relay_server/gui_static/argrelay_favicon_16.ico",
            "argrelay_app_server/relay_server/gui_static/argrelay_style.css",
            "argrelay_app_server/relay_server/gui_static/external_link.svg",
            "argrelay_app_server/relay_server/gui_templates/argrelay_main.html",
        ],
        "argrelay_docs": argrelay_docs_files,
        "argrelay_data": argrelay_data_files,
    },
    include_package_data = True,
    # Because `argrelay_docs` and `argrelay_data` share the same `package_dir` config,
    # exclude overlapping files explicitly (opposite of `package_data` config):
    exclude_package_data = {
        "argrelay_docs": argrelay_data_files,
        "argrelay_data": argrelay_docs_files,
    },
    # FS_84_11_73_28: supported python versions:
    python_requires = ">=3.9",
    install_requires = [
        "Flask",
        "Werkzeug",
        "PyYaml",
        "jsonschema",
        "flasgger",
        "marshmallow<4.0.0",
        "marshmallow-oneofschema",
        "apispec",
        "pymongo",
        "GitPython",
        # Use `mongomock` as replacement for Mongo DB in simple prod cases:
        "mongomock",
        "requests",
        "cachetools",
    ],
    extras_require = extras_require,
)
