#!/usr/bin/env python3

from __future__ import annotations

import logging

from proto_code import (
    AbstractCachingStateBootstrapper,
    EnvContext,
    EnvState,
    main,
    StateValueType,
)

logger = logging.getLogger()


# noinspection PyPep8Naming
class Bootstrapper_state_custom_value(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_custom,
            state_parents=[
                EnvState.state_env_conf_gen_file_data,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        bootstrapped_value: str = f"[{self.__class__.__name__}]"
        logger.info(f"[{bootstrapped_value}]")
        return bootstrapped_value


def customize_env_context():
    env_ctx = EnvContext()

    env_ctx.register_bootstrapper(Bootstrapper_state_custom_value(env_ctx))

    env_ctx.populate_dependencies()

    env_ctx.universal_sink = env_ctx.state_bootstrappers[EnvState.state_custom]

    return env_ctx


if __name__ == "__main__":
    main(customize_env_context)
