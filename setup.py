import os

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
    # See `docs/dev_notes/version_format.md`:
    version = "0.5.2.dev0",
    author = "uvsmtid",
    author_email = "uvsmtid@gmail.com",
    description = "Tab-completion & data search server - total recall",
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
    },
    package_data = {
        "argrelay": [

            # config files:
            "sample_conf/argrelay.server.yaml",
            "sample_conf/argrelay.client.json",

            # GUI client:
            "relay_server/gui_static/argrelay_client.js",
            "relay_server/gui_static/argrelay_style.css",
            "relay_server/gui_static/external_link.svg",
            "relay_server/gui_templates/argrelay_main.html",

            # other resource files:
            "custom_integ_res/argrelay_rc.bash",
            "custom_integ_res/bootstrap_dev_env.bash",
            "custom_integ_res/dev_shell.bash",
            "custom_integ_res/init_shell_env.bash",

        ],
        "argrelay_docs": list_dir("./docs/") + [
            "readme.md",
        ],
    },
    include_package_data = True,
    python_requires = ">=3.7",
    install_requires = [

        # Use Flask 2.2.3 to avoid this error:
        # ImportError: cannot import name 'JSONEncoder' from 'flask.json'
        # https://stackoverflow.com/a/76116905/441652
        "Flask==2.2.3",

        # Use Werkzeug < 3.0.0 to avoid this error:
        # ImportError: cannot import name 'url_quote' from 'werkzeug.urls'
        # https://stackoverflow.com/a/77214086
        "Werkzeug<3.0",

        "PyYaml",
        "jsonschema",
        "flasgger",
        "marshmallow",
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
