#!/usr/bin/env python3
# FT_85_17_35_21.boot_env.md: see also `@/exe/bootstrap_env.bash`


def import_proto_kernel(proto_kernel_rel_path):
    """
    `protoprimer` entry script boilerplate function to import `proto_kernel`.
    """
    import os
    import importlib.util

    module_spec = importlib.util.spec_from_file_location(
        "proto_kernel",
        os.path.join(
            os.path.dirname(str(__file__)),
            proto_kernel_rel_path,
        ),
    )
    assert module_spec is not None
    loaded_proto_kernel = importlib.util.module_from_spec(module_spec)
    assert module_spec.loader is not None
    module_spec.loader.exec_module(loaded_proto_kernel)
    return loaded_proto_kernel


if __name__ == "__main__":
    proto_kernel = import_proto_kernel("./proto_code/proto_kernel.py")
    proto_kernel.boot_env("argrelay_app_bootstrap.cmd_bootstrap_env:custom_main")
