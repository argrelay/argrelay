import importlib


def verify_package_version(
    module_obj,
) -> bool:
    """
    Test that the version returned for the metadata of the installed package matches its `__version__` variable.
    """

    # given:

    module_version = getattr(
        module_obj,
        "__version__",
    )

    package_version = importlib.metadata.version("argrelay")

    # when:
    # then:

    return module_version == package_version
