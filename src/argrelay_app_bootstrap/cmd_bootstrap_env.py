from __future__ import annotations

import logging

from protoprimer.primer_kernel import (
    EnvContext,
    proto_main,
)

logger = logging.getLogger()


def custom_main():
    proto_main(customize_env_context)


def customize_env_context():

    env_ctx = EnvContext()

    return env_ctx


if __name__ == "__main__":
    custom_main()
