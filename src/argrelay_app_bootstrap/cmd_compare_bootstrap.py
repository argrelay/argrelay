from __future__ import annotations

"""
Verifies if these produce equivalent results:
*   `exe/bootstrap_env.bash`
*   `exe/bootstrap_env.py`


Context:
TODO_11_66_62_70.python_bootstrap.md tracks the migration:
*   from the old `bash`-based bootstrap
*   into the new `python`-based bootstrap

Invocation:
exe/compare_bootstrap
"""

import argparse
import filecmp
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile


logger = logging.getLogger(__name__)

_exclude_paths: list[re.Pattern] = [
    #
    # Differs due to clone metadata (timestamps, pack files):
    # re.compile(r"^\.git(/|$)"),
    #
    # Differs due to abs paths embedded in symlinks, activation scripts, binary extensions:
    # re.compile(r"^venv(/|$)"),
    #
    # Differs due to abs paths encoded in bytecode:
    # re.compile(r"(^|/)__pycache__(/|$)"),
    #
    # Compiled `python` sources:
    re.compile(r"\.pyc$"),
    #
    # Git working-tree index: modified by bootstrap operations:
    re.compile(r"^\.git/index$"),
    #
    # Reflog timestamps differ between clones done at different times:
    re.compile(r"^\.git/logs(/|$)"),
    #
    # The scripts differ in venv prompt:
    re.compile(r"^venv/pyvenv\.cfg$"),
    #
    # The scripts differ in venv prompt:
    re.compile(r"^venv/bin/activate.*$"),
    #
    # RECORD files list installed file paths (abs paths inside venv):
    re.compile(r"^venv/.*/RECORD$"),
    #
    # NOTE: The diff is normalized out:
    # Editable install .pth embeds abs path to src dir:
    # re.compile(r"^venv/lib/.*/site-packages/__editable__\."),
    #
    # NOTE: The diff is normalized out:
    # direct_url.json embeds abs path as file:// URL:
    # re.compile(r"^venv/lib/.*/site-packages/.*/direct_url\.json$"),
    #
    # Python bootstrap writes log files; bash bootstrap does not:
    re.compile(r"^logs/"),
]


def init_arg_parser() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    arg_parser.add_argument(
        "--comparator_dir",
        default=None,
        metavar="PATH",
        help="Override the output dir (default: tmp/compare_bootstrap/ under argrelay_dir).",
    )
    arg_parser.add_argument(
        "--skip_bootstrap",
        type=lambda v: v.lower() not in ("false", "0"),
        default=True,
        help="Skip bootstrap steps, compare only (default: True).",
    )
    arg_parser.add_argument(
        "--symlink_side",
        choices=["L", "R"],
        default="R",
        help="Which side the `selected_side` symlink points to (default: R).",
    )
    return arg_parser.parse_args()


def custom_main():
    logging.basicConfig(level=logging.INFO)

    parsed_args = init_arg_parser()

    argrelay_dir = os.getcwd()
    comparator_dir = parsed_args.comparator_dir or os.path.join(
        argrelay_dir, "tmp", "compare_bootstrap"
    )

    logger.info("argrelay_dir: %s", argrelay_dir)
    logger.info("comparator_dir: %s", comparator_dir)

    side_l_repo = os.path.join(comparator_dir, "side_L", "repo")
    side_r_repo = os.path.join(comparator_dir, "side_R", "repo")
    selected_side_path = os.path.join(comparator_dir, "selected_side")

    if not parsed_args.skip_bootstrap:
        _clean_leftovers(comparator_dir)

        _clone_repo(argrelay_dir, side_l_repo)
        _clone_repo(argrelay_dir, side_r_repo)

        _create_conf_symlink(side_l_repo)
        _create_conf_symlink(side_r_repo)

        _remove_if_exists(os.path.join(side_l_repo, "conf", "env_packages.txt"))
        _remove_if_exists(os.path.join(side_r_repo, "conf", "env_packages.txt"))

        _run_bootstrap_bash(side_l_repo)
        _run_bootstrap_python(side_r_repo)
    else:
        logger.info(
            "skip_bootstrap=True: skipping clone+bootstrap, using existing dirs"
        )

    symlink_target = side_l_repo if parsed_args.symlink_side == "L" else side_r_repo
    if os.path.islink(selected_side_path):
        os.unlink(selected_side_path)
    os.symlink(symlink_target, selected_side_path)
    logger.info("selected_side -> %s", symlink_target)

    _compare_dirs(side_l_repo, side_r_repo, selected_side_path)


def _remove_if_exists(file_path: str) -> None:
    if os.path.exists(file_path):
        logger.info("removing pinned deps file: %s", file_path)
        os.remove(file_path)


def _clean_leftovers(comparator_dir: str) -> None:
    if os.path.exists(comparator_dir):
        logger.info("removing previous comparator state: %s", comparator_dir)
        shutil.rmtree(comparator_dir)
    os.makedirs(comparator_dir)


def _clone_repo(
    source_repo: str,
    target_repo: str,
) -> None:
    logger.info("cloning %s -> %s", source_repo, target_repo)
    os.makedirs(os.path.dirname(target_repo), exist_ok=True)
    subprocess.run(
        [
            "git",
            "clone",
            source_repo,
            target_repo,
        ],
        check=True,
    )
    logger.info("clone done: %s", target_repo)


def _read_default_env_dir(repo_dir: str) -> str:
    proto_kernel_json_path = os.path.join(
        repo_dir,
        "exe",
        "proto_code",
        "proto_kernel.json",
    )
    with open(proto_kernel_json_path) as file_obj:
        return json.load(file_obj)["default_env_dir_rel_path"]


def _create_conf_symlink(repo_dir: str) -> None:
    default_env_dir = _read_default_env_dir(repo_dir)
    conf_path = os.path.join(repo_dir, "conf")
    logger.info("creating conf symlink: %s -> %s", conf_path, default_env_dir)
    os.symlink(default_env_dir, conf_path)


def _run_bootstrap_bash(repo_dir: str) -> None:
    logger.info("running bash bootstrap in: %s", repo_dir)
    subprocess.run(
        ["exe/bootstrap_env.bash"],
        cwd=repo_dir,
        check=True,
    )
    logger.info("bash bootstrap done: %s", repo_dir)


def _run_bootstrap_python(repo_dir: str) -> None:
    logger.info("running python bootstrap in: %s", repo_dir)
    subprocess.run(
        ["exe/bootstrap_env.py"],
        cwd=repo_dir,
        check=True,
    )
    logger.info("python bootstrap done: %s", repo_dir)


def _should_exclude(rel_path: str) -> bool:
    return any(exclude_pattern.search(rel_path) for exclude_pattern in _exclude_paths)


def _collect_rel_paths(root_dir: str) -> dict[str, str]:
    """
    Return {rel_path: abs_path} for all non-excluded files under root_dir.
    """

    rel_path_map = {}
    for dir_path, dir_names, file_names in os.walk(root_dir):
        dir_names[:] = [
            dir_name
            for dir_name in dir_names
            if not _should_exclude(
                os.path.relpath(os.path.join(dir_path, dir_name), root_dir)
            )
        ]
        for file_name in file_names:
            abs_path = os.path.join(dir_path, file_name)
            rel_path = os.path.relpath(abs_path, root_dir)
            if _should_exclude(rel_path):
                continue
            rel_path_map[rel_path] = abs_path
    return rel_path_map


def _normalize_content(
    file_text: str,
    side_l: str,
    side_r: str,
    selected_side_path: str,
) -> str:
    """
    Replace both repo abs paths with the selected_side symlink path to eliminate path-only diffs.
    """
    file_text = file_text.replace(side_l, selected_side_path)
    file_text = file_text.replace(side_r, selected_side_path)
    return file_text


def _is_text_file(file_path: str) -> bool:
    try:
        with open(file_path, "rb") as file_obj:
            file_chunk = file_obj.read(8192)
        return b"\x00" not in file_chunk
    except OSError:
        return False


def _compare_dirs(
    side_l: str,
    side_r: str,
    selected_side_path: str,
) -> None:
    logger.info("comparing: %s vs %s", side_l, side_r)

    files_l = _collect_rel_paths(side_l)
    files_r = _collect_rel_paths(side_r)

    keys_l = set(files_l)
    keys_r = set(files_r)

    only_l = sorted(keys_l - keys_r)
    only_r = sorted(keys_r - keys_l)
    paths_common = sorted(keys_l & keys_r)

    diff_count = 0

    for rel_path in only_l:
        logger.warning("only in side_L: %s", rel_path)

    for rel_path in only_r:
        logger.warning("only in side_R: %s", rel_path)

    for rel_path in paths_common:
        abs_l = files_l[rel_path]
        abs_r = files_r[rel_path]

        if filecmp.cmp(abs_l, abs_r, shallow=False):
            continue

        if not (_is_text_file(abs_l) and _is_text_file(abs_r)):
            diff_count += 1
            logger.warning("binary files differ: %s", rel_path)
            continue

        with open(abs_l) as file_l:
            text_l = _normalize_content(
                file_l.read(),
                side_l,
                side_r,
                selected_side_path,
            )
        with open(abs_r) as file_r:
            text_r = _normalize_content(
                file_r.read(),
                side_l,
                side_r,
                selected_side_path,
            )

        if text_l == text_r:
            continue

        diff_count += 1
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".L", delete=False
        ) as temp_file_l:
            temp_file_l.write(text_l)
            temp_path_l = temp_file_l.name
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".R", delete=False
        ) as temp_file_r:
            temp_file_r.write(text_r)
            temp_path_r = temp_file_r.name

        try:
            diff_result = subprocess.run(
                [
                    "diff",
                    "-u",
                    "--label",
                    f"side_L/{rel_path}",
                    "--label",
                    f"side_R/{rel_path}",
                    temp_path_l,
                    temp_path_r,
                ],
                capture_output=True,
                text=True,
            )
            logger.warning("content differs: %s\n%s", rel_path, diff_result.stdout)
        finally:
            os.unlink(temp_path_l)
            os.unlink(temp_path_r)

    total_only = len(only_l) + len(only_r)
    if total_only > 0 or diff_count > 0:
        logger.error("Some included files are different.")
        sys.exit(1)
    else:
        logger.info("No included files are different.")


if __name__ == "__main__":
    custom_main()
