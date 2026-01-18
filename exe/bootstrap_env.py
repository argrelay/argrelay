#!/usr/bin/env python3

if __name__ == "__main__":

    proto_kernel_rel_path = "./proto_code/proto_kernel.py"

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # Boilerplate to import `proto_kernel` from `protoprimer`
    import os
    import importlib.util

    proto_spec = importlib.util.spec_from_file_location(
        "proto_kernel",
        os.path.join(
            os.path.dirname(__file__),
            proto_kernel_rel_path,
        ),
    )
    proto_kernel = importlib.util.module_from_spec(proto_spec)
    proto_spec.loader.exec_module(proto_kernel)
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    proto_kernel.run_main(
        "protoprimer.primer_kernel",
        "main",
    )
