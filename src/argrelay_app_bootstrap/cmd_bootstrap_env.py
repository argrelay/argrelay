from __future__ import annotations

import enum
import importlib
import logging
import os
import shlex
import shutil
import subprocess
import sys
from typing import List

from protoprimer.primer_kernel import (
    AbstractCachingStateNode,
    EntryFunc,
    EnvContext,
    EnvState,
    run_process,
    TargetState,
    trivial_factory,
    ValueType,
)

logger = logging.getLogger()


def read_bash_array(conf_path: str, array_name: str) -> List[str]:
    """Source a bash config file and return the named bash array as a Python list."""
    script = f'source {shlex.quote(conf_path)}; printf "%s\\0" "${{{array_name}[@]}}"'
    result = subprocess.run(["bash", "-c", script], capture_output=True, check=True)
    return [item for item in result.stdout.decode().split("\0") if item]


def _get_module_file_path(module_name: str, rel_path: str) -> str:
    module = importlib.import_module(module_name)
    return os.path.join(os.path.dirname(module.__file__), rel_path)


def _install_file(
    src: str,
    dst: str,
    mode: str,
    override: bool,
    venv_abs_path: str,
) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    if os.path.lexists(dst):
        if not override:
            return
        os.remove(dst)
    if mode == "symlink_method":
        os.symlink(src, dst)
    elif mode == "copy_method":
        shutil.copy2(src, dst)
    elif mode == "detect_method":
        real_src = os.path.realpath(src)
        real_venv = os.path.realpath(venv_abs_path)
        if real_src.startswith(real_venv + os.sep):
            shutil.copy2(real_src, dst)
        else:
            os.symlink(real_src, dst)
    else:
        raise ValueError(f"unknown install mode: {mode}")


def _install_file_tuples(
    flat_tuples: List[str],
    argrelay_dir: str,
    venv_abs_path: str,
    mode: str,
    override: bool,
) -> None:
    assert len(flat_tuples) % 3 == 0, "module_path_file_tuples count not divisible by 3"
    for i in range(0, len(flat_tuples), 3):
        module_name = flat_tuples[i]
        src_rel = flat_tuples[i + 1]
        dst_rel = flat_tuples[i + 2]
        src_abs = _get_module_file_path(module_name, src_rel)
        dst_abs = os.path.join(argrelay_dir, dst_rel)
        _install_file(src_abs, dst_abs, mode, override, venv_abs_path)


def _generate_runner_script(
    path: str,
    python_path: str,
    script_rel: str,
    main_import: str,
) -> None:
    content = (
        f"#!{python_path}\n"
        f"# `argrelay`-generated integration file: https://github.com/argrelay/argrelay\n"
        f"# It is NOT supposed to be version-controlled per project as it:\n"
        f"# *   is generated\n"
        f"# *   differs per environment (due to different abs path to `venv`)\n"
        f"# It should rather be added to `.gitignore`.\n"
        f"\n"
        f"import os\n"
        f"\n"
        f"from argrelay_lib_root import misc_helper_common\n"
        f"\n"
        f"# FS_29_54_67_86 dir_structure: `@/{script_rel}` -> `@/`:\n"
        f"misc_helper_common.set_argrelay_dir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n"
        f"\n"
        f"{main_import}\n"
        f"\n"
        f"if __name__ == '__main__':\n"
        f"    main()\n"
    )
    with open(path, "w") as f:
        f.write(content)
    os.chmod(path, os.stat(path).st_mode | 0o100)


def _install_command_symlinks(argrelay_dir: str, command_names: List[str]) -> None:
    bin_dir = os.path.join(argrelay_dir, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    target = "../exe/run_argrelay_client"
    for name in command_names:
        symlink_path = os.path.join(bin_dir, name)
        if os.path.islink(symlink_path):
            if os.readlink(symlink_path) != target:
                logger.warning(
                    "symlink does not point to `@/exe/run_argrelay_client`: %s",
                    symlink_path,
                )
                os.remove(symlink_path)
                os.symlink(target, symlink_path)
        elif os.path.exists(symlink_path):
            raise RuntimeError(
                f"symlink creation obstructed by existing path (review and remove): {symlink_path}"
            )
        else:
            os.symlink(target, symlink_path)


def _update_check_env_bash(argrelay_dir: str, argrelay_module_dir: str) -> None:
    src = os.path.join(argrelay_module_dir, "custom_integ_res/check_env.bash")
    dst = os.path.join(argrelay_dir, "exe/check_env.bash")
    if os.path.islink(dst):
        if os.readlink(dst) != src:
            raise RuntimeError(
                f"exe/check_env.bash is a symlink to unexpected path - review and remove manually: {dst}"
            )
        os.remove(dst)
    elif os.path.exists(dst) and not os.path.isfile(dst):
        raise RuntimeError(
            f"exe/check_env.bash exists but is neither a symlink nor a file - review and remove manually: {dst}"
        )
    shutil.copy2(src, dst)


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_scripts_generated(AbstractCachingStateNode[int]):

    _parent_states = staticmethod(
        lambda: [
            TargetState.target_proto_bootstrap_completed.value.name,
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: CustomEnvState.state_scripts_generated.name)

    def _eval_state_once(
        self,
    ) -> ValueType:

        self.eval_parent_state(TargetState.target_proto_bootstrap_completed.value.name)

        argrelay_dir: str = self.eval_parent_state(
            EnvState.state_ref_root_dir_abs_path_inited.name
        )
        venv_abs_path: str = self.eval_parent_state(
            EnvState.state_local_venv_dir_abs_path_inited.name
        )

        import argrelay

        argrelay_module_dir = os.path.dirname(argrelay.__file__)

        # Update exe/check_env.bash from argrelay module:
        _update_check_env_bash(argrelay_dir, argrelay_module_dir)

        # Install exe/argrelay_common_lib.bash as symlink (always override):
        _install_file(
            src=os.path.join(
                argrelay_module_dir, "custom_integ_res/argrelay_common_lib.bash"
            ),
            dst=os.path.join(argrelay_dir, "exe/argrelay_common_lib.bash"),
            mode="symlink_method",
            override=True,
            venv_abs_path=venv_abs_path,
        )

        # Install config files (detect_method, no override):
        config_files_conf = os.path.join(argrelay_dir, "exe/config_files.conf.bash")
        config_tuples = read_bash_array(config_files_conf, "module_path_file_tuples")
        _install_file_tuples(
            config_tuples, argrelay_dir, venv_abs_path, "detect_method", override=False
        )

        # Install resource files (symlink_method, override):
        resource_files_conf = os.path.join(argrelay_dir, "exe/resource_files.conf.bash")
        resource_tuples = read_bash_array(
            resource_files_conf, "module_path_file_tuples"
        )
        _install_file_tuples(
            resource_tuples,
            argrelay_dir,
            venv_abs_path,
            "symlink_method",
            override=True,
        )

        # Generate exe/run_argrelay_server and exe/run_argrelay_client:
        python_path = sys.executable
        _generate_runner_script(
            path=os.path.join(argrelay_dir, "exe/run_argrelay_server"),
            python_path=python_path,
            script_rel="exe/run_argrelay_server",
            main_import="from argrelay_app_server.relay_server.__main__ import main",
        )
        _generate_runner_script(
            path=os.path.join(argrelay_dir, "exe/run_argrelay_client"),
            python_path=python_path,
            script_rel="exe/run_argrelay_client",
            main_import="from argrelay_app_client.relay_client.__main__ import main",
        )
        _generate_runner_script(
            path=os.path.join(argrelay_dir, "exe/argrelay_mcp_proxy"),
            python_path=python_path,
            script_rel="exe/argrelay_mcp_proxy",
            main_import="from argrelay_app_mcp_proxy.mcp_proxy.__main__ import main",
        )

        # Create bin/ symlinks from shell_env.conf.bash:
        shell_env_conf = os.path.join(argrelay_dir, "conf/shell_env.conf.bash")
        command_names = read_bash_array(
            shell_env_conf, "argrelay_bind_command_basenames"
        )
        _install_command_symlinks(argrelay_dir, command_names)

        # Remove stale server index to pick a random available server next time:
        server_index_path = os.path.join(
            argrelay_dir, "var/argrelay_client.server_index"
        )
        if os.path.exists(server_index_path):
            os.remove(server_index_path)

        return 0


class CustomEnvState(enum.Enum):

    state_scripts_generated = Bootstrapper_state_scripts_generated


def custom_main():
    env_ctx = customize_env_context()
    run_process(env_ctx)


def customize_env_context():

    env_ctx = EnvContext()
    env_ctx.graph_coordinates.entry_func = EntryFunc.func_boot_env

    env_ctx.state_graph.register_factory(
        CustomEnvState.state_scripts_generated.name,
        Bootstrapper_state_scripts_generated(env_ctx),
    )

    env_ctx.final_state = CustomEnvState.state_scripts_generated.name

    return env_ctx


if __name__ == "__main__":
    custom_main()
