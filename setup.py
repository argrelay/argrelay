import setuptools

with open("readme.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

tests_require = [
    "responses",
]

extras_require = {
    "test": tests_require,
}

setuptools.setup(
    name = "argrelay",
    version = "0.0.0.dev3",
    author = "uvsmtid",
    author_email = "uvsmtid@gmail.com",
    description = "TODO",
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
        "Development Status :: 1 - Planning",
    ],
    package_dir = {
        "": "src",
    },
    packages = setuptools.find_packages(
        where = "src",
    ),
    python_requires = ">=3.7",
    install_requires = [
        "PyYaml",
        "jsonschema",
        "flasgger",
        "marshmallow",
        "apispec",
        "pymongo",
    ],
    tests_require = tests_require,
    extras_require = extras_require,
)
