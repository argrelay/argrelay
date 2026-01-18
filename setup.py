import os

import setuptools

# The "distribution root" refers to the top-level directory where your project code resides.
# It is the root directory that contains the `setup.py` file itself.
# In the case of `argrelay`, it may confusingly appear it is an equivalent to `argrelay_dir`
# (because it contains `setup.py`), but it is not - when installed, `setup.py` will run from the extracted archive:
distrib_root = os.path.dirname(os.path.abspath(__file__))


def list_dir(
    top_dir_abs_path: str,
) -> list[str]:
    """
    List files recursively from `top_dir_abs_path` with paths relative to `top_dir_abs_path`.
    """
    file_rel_paths = []
    for parent_dir_abs_path, child_dir_names, child_file_names in os.walk(
        top_dir_abs_path
    ):
        for child_file_name in child_file_names:
            file_abs_path: str = os.path.join(
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

# All static metadata (`name`, `version`, `dependencies`, etc.) is now defined in `pyproject.toml`.
# This `setup.py` only exists to handle the imperative logic for packaging data files,
# which cannot be expressed declaratively in `pyproject.toml` (until later conversion).
setuptools.setup(
    # See the sample layout:
    # https://docs.python.org/3.8/distutils/setupscript.html#installing-package-data
    # List all packages/sub-packages (so that they are taken by `package_dir` below):
    packages=setuptools.find_packages(
        where=f"{distrib_root}/src/",
    )
    + [
        "argrelay_docs",
        "argrelay_data",
    ],
    # See:
    # https://docs.python.org/3.8/distutils/setupscript.html#listing-whole-packages
    #     The keys to this dictionary are package names,
    #     and an empty package name stands for the root package.
    #     The values are directory names relative to your distribution root.
    #     See "distribution root" above - during installation, `setup.py` will run from the extracted archive.
    package_dir={
        # fmt: off
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
        # fmt: on
    },
    # See:
    # https://docs.python.org/3.8/distutils/setupscript.html#installing-package-data
    #     The paths are interpreted as relative to the directory containing the package
    #     (information from the `package_dir` mapping is used if appropriate);
    #     that is, the files are expected to be part of the package in the source directories.
    package_data={
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
    include_package_data=True,
    # Because `argrelay_docs` and `argrelay_data` share the same `package_dir` config,
    # exclude overlapping files explicitly (opposite of `package_data` config):
    exclude_package_data={
        "argrelay_docs": argrelay_data_files,
        "argrelay_data": argrelay_docs_files,
    },
)
