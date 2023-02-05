import setuptools

with open("readme.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

tests_require = [
    "tox",
    "responses",
    "mongomock",
    "pandas",
]

extras_require = {
    "tests": tests_require,
}

setuptools.setup(
    name = "argrelay",
    version = "0.0.0.dev16",
    author = "uvsmtid",
    author_email = "uvsmtid@gmail.com",
    description = "Bash Tab-completion (data) server",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    keywords = "argparse, argcomplete, bash, complete",
    url = "https://github.com/uvsmtid/argrelay",
    project_urls = {
        "Bug Tracker": "https://github.com/uvsmtid/argrelay/issues",
    },
    classifiers = [
        "Environment :: Console",
        "Framework :: Flask",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Shells",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Terminals",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 2 - Pre-Alpha",
    ],
    # See sample layout:
    # https://docs.python.org/3/distutils/setupscript.html#installing-package-data
    packages = setuptools.find_packages(
        where = "src",
    ),
    # See:
    # https://docs.python.org/3/distutils/setupscript.html#listing-whole-packages
    # Instead of specifying directory of the specific package:
    # "argrelay": "src/argrelay",
    # Specify directory of "root" package:
    # "": "src",
    # Apparently, this makes `argrelay.egg-info` dir appear in `src` on editable install rather than in root `.`.
    package_dir = {
        "": "src",
    },
    package_data = {
        "argrelay": [
            "relay_demo/argrelay.server.yaml",
            "relay_demo/argrelay.client.json",
            "relay_demo/build-git-env.bash",
            "relay_demo/build-pip-env.bash",
            "relay_demo/deploy-artifacts.bash",
            "relay_demo/dev-init.bash",
            "relay_demo/dev-shell.bash",
            "relay_demo/argrelay-rc.bash",
        ],
    },
    include_package_data = True,
    python_requires = ">=3.7",
    install_requires = [
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
    ],
    tests_require = tests_require,
    extras_require = extras_require,
)
