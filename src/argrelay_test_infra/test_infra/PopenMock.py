from __future__ import annotations

import subprocess
from typing import Union

_orig_Popen = subprocess.Popen


class PopenMock:
    """
    This class mocks expectation of `subprocess.Popen` based on config in `expected_args_to_output`.
    If it sees unexpected CLI args (not specified in `expected_args_to_output`), it throws an error.
    Otherwise:
    *   If configured tuple is not `None`, it delegates calls to `ConfiguredPopenMockDelegatee`
        (which returns configured tuple (returncode, stdout, stderr) to the `Popen` caller).
    *   If configured tuple is `None`, it passes calls through to the original `Popen` (see `_orig_Popen`).

    Ideas for inspiration:
    *   https://stackoverflow.com/a/53793739/441652
    *   https://stackoverflow.com/a/25693097/441652
    """

    def __init__(
        self,
        expected_args_to_output: dict[Union[str, tuple[str, ...]], tuple[int, str, str]],
        *args,
        **kwargs,
    ):
        self.expected_args_to_output = expected_args_to_output
        """
        Collection of expected input lists of CLI args (`tuple`-s of `str` as keys to `dict`) mapped to
        the output `tuple` of (exit_code, stdout_str, stderr_str).
        """

    def __call__(
        self,
        cli_args,
        *args,
        **kwargs,
    ):
        if isinstance(cli_args, str):
            # Popen with `shell = True` is called with single string arg (full command line).
            # Nevertheless, the config for expected args should specify it as singleton `tuple` (instead of `str`):
            config_key = cli_args
        elif isinstance(cli_args, list):
            config_key = tuple(cli_args)
        else:
            raise ValueError(f"unknown CLI args type: {type(cli_args)}")

        if config_key in self.expected_args_to_output:
            p_output_config_tuple = self.expected_args_to_output[config_key]
            if p_output_config_tuple is None:
                return _orig_Popen(cli_args, *args, **kwargs)
            else:
                # The call to `Popen` with CLI args matching one of the expected ones:
                # all these fields will (potentially) be inspected through other calls to `Popen` - configure them:
                return ConfiguredPopenMockDelegatee(
                    cli_args,
                    *p_output_config_tuple,
                )
        else:
            raise ValueError(
                f"unexpected CLI args: `{cli_args}` expected CLI args: `{self.expected_args_to_output.keys()}`"
            )


class ConfiguredPopenMockDelegatee:

    def __init__(
        self,
        args: Union[str, list[str]],
        returncode: int,
        stdout: str,
        stderr: str,
    ):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def __enter__(
        self,
        *args,
        **kwargs,
    ):
        return self

    def __exit__(
        self,
        *args,
        **kwargs,
    ):
        pass

    def wait(
        self,
        *args,
        **kwargs,
    ):
        return self.returncode

    def kill(
        self,
        *args,
        **kwargs,
    ):
        pass

    def communicate(
        self,
        *args,
        **kwargs,
    ):
        return (
            self.stdout,
            self.stderr,
        )

    def poll(
        self,
        *args,
        **kwargs,
    ):
        return self.returncode
