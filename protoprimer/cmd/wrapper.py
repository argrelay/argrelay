#!/usr/bin/env python3

from __future__ import annotations

import logging

from proto_copy import (
    AbstractCachingStateBootstrapper,
    EnvContext,
    EnvState,
    main,
    StateValueType,
    TargetState,
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
            state_parents=[
                TargetState.target_full_proto_bootstrap,
            ],
            env_state=EnvState.state_custom,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        # Bootstrap all dependencies:
        for env_state in self.state_parents:
            self.env_ctx.bootstrap_state(env_state)

        bootstrapped_value: str = f"{self.get_env_state()}"
        logger.info(f"completed with `bootstrapped_value` [{bootstrapped_value}]")
        return bootstrapped_value


def customize_env_context():
    env_ctx = EnvContext()

    env_ctx.register_bootstrapper(Bootstrapper_state_custom_value(env_ctx))

    env_ctx.populate_dependencies()

    env_ctx.universal_sink = EnvState.state_custom

    return env_ctx


if __name__ == "__main__":
    main(customize_env_context)
