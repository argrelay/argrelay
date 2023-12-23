from __future__ import annotations

import bisect
import copy
import dataclasses
import dis
import importlib
import json
import os
import os.path
import time
import unittest

from argrelay.client_command_remote import ProposeArgValuesRemoteOptimizedClientCommand
from argrelay.client_spec.ShellContext import ShellContext, UNKNOWN_COMP_KEY
from argrelay.enum_desc.CompType import CompType
from argrelay.relay_client import (
    __main__,
)
from argrelay.runtime_context.ParsedContext import ParsedContext
from argrelay.test_infra import change_to_known_repo_path
from argrelay.test_infra.BaseTestClass import BaseTestClass


# TODO: Fix this to run under `tox`:
@unittest.skipIf(
    os.environ.get("TOX_ENV_NAME", False),
    "At the moment, test fails if run under `tox`.",
)
# noinspection PyMethodMayBeStatic
class ThisTestClass(BaseTestClass):
    # Modules imported from `__main__` specified as they use conditional/dynamic import.
    # The imports listed are according to execution path for `Tab`-completion (`ServerAction.ProposeArgValues`).
    # The rest of modules can be found recursively if they do not also use dynamic import.
    # Otherwise, select the imports on the required execution path manually here:
    entry_module_names = [
        __main__.__name__,
        ProposeArgValuesRemoteOptimizedClientCommand.__name__,
    ]

    # To generate `expected_imports`, run `test_print_grouped_imports`.
    expected_imports = {
        "__future__": [],
        "argrelay.client_command_remote.ProposeArgValuesRemoteOptimizedClientCommand": [
            "argrelay.enum_desc.ServerAction",
            "argrelay.misc_helper.ElapsedTime",
            "argrelay.runtime_data.ConnectionConfig",
            "argrelay.server_spec.CallContext",
            "json",
            "socket"
        ],
        "argrelay.client_spec.ShellContext": [
            "__future__",
            "argrelay.enum_desc.CompScope",
            "argrelay.enum_desc.CompType",
            "argrelay.enum_desc.ServerAction",
            "argrelay.enum_desc.TermColor",
            "argrelay.misc_helper",
            "argrelay.server_spec.CallContext",
            "dataclasses",
            "os"
        ],
        "argrelay.enum_desc.CompScope": [
            "__future__",
            "argrelay.enum_desc.CompType",
            "enum"
        ],
        "argrelay.enum_desc.CompType": [
            "enum"
        ],
        "argrelay.enum_desc.ServerAction": [
            "enum"
        ],
        "argrelay.enum_desc.TermColor": [
            "enum"
        ],
        "argrelay.misc_helper": [
            "os",
            "sys"
        ],
        "argrelay.misc_helper.ElapsedTime": [
            "__future__",
            "argrelay.misc_helper",
            "time"
        ],
        "argrelay.relay_client.__main__": [
            "argrelay.client_spec.ShellContext",
            "argrelay.enum_desc.CompType",
            "argrelay.enum_desc.ServerAction",
            "argrelay.misc_helper",
            "argrelay.misc_helper.ElapsedTime",
            "argrelay.runtime_data.ClientConfig",
            "argrelay.runtime_data.ConnectionConfig",
            "sys"
        ],
        "argrelay.runtime_data.ClientConfig": [
            "argrelay.runtime_data.ConnectionConfig",
            "dataclasses"
        ],
        "argrelay.runtime_data.ConnectionConfig": [
            "dataclasses"
        ],
        "argrelay.server_spec.CallContext": [
            "__future__",
            "argrelay.enum_desc.CompScope",
            "argrelay.enum_desc.ServerAction",
            "argrelay.enum_desc.TermColor",
            "argrelay.misc_helper",
            "dataclasses"
        ],
        "dataclasses": [],
        "enum": [],
        "json": [],
        "os": [],
        "socket": [],
        "sys": [],
        "time": []
    }

    def module_size(
        self,
        module_name: str,
    ):
        module_path = self.get_module_path(module_name)
        if module_path is None:
            return 0
        if os.path.exists(module_path):
            return os.path.getsize(module_path)

    def get_module_path(
        self,
        module_name: str,
    ):
        py_module = importlib.import_module(module_name)
        if not hasattr(py_module, "__file__"):
            return None
        return py_module.__file__

    def list_imported_modules(
        self,
        module_name: str,
    ) -> list[str]:
        """
        Loads imported module names for a given source `module_path`:
        https://stackoverflow.com/a/35495585/441652
        """

        module_path = self.get_module_path(module_name)
        if module_path is None:
            return []

        src_base_path = os.path.join(os.getcwd(), "src")
        if not module_path.startswith(src_base_path):
            # Do not recurse into modules outside "src":
            return []

        with open(module_path) as module_file:
            # noinspection PyTypeChecker
            instr_list = dis.get_instructions(module_file.read())

            module_imports = [import_instr for import_instr in instr_list if "IMPORT_NAME" in import_instr.opname]

            listed_imports = []
            for instr in module_imports:
                module_name = instr.argval
                bisect.insort(listed_imports, module_name)

            return listed_imports

    def group_imports_per_module_per_op(
        self,
        module_names: list[str],
    ) -> dict[str, list[str]]:

        module_names = copy.deepcopy(module_names)
        visited_module_names = []
        grouped_imports = {}

        while module_names:
            for module_name in module_names:
                grouped_imports[module_name] = self.list_imported_modules(module_name)
            visited_module_names.extend(module_names)
            module_names.clear()
            for listed_imports in grouped_imports.values():
                for listed_import in listed_imports:
                    if listed_import not in visited_module_names:
                        module_names.append(listed_import)

        return grouped_imports

    def group_imports(self):
        grouped_imports = self.group_imports_per_module_per_op(ThisTestClass.entry_module_names)
        return grouped_imports

    def dump_ordered_json(
        self,
        grouped_imports,
    ):
        return json.dumps(
            grouped_imports,
            indent = 4,
            sort_keys = True,
        )

    def get_module_load_time_ns(self, module_name):
        time_before = time.time_ns()
        import_module = importlib.import_module(module_name)
        # TODO: HACK: Fix `test_module_reload_breaks_dataclass_asdict` below to remove this hack:
        if module_name != "dataclasses":
            importlib.reload(import_module)
        time_after = time.time_ns()
        return time_after - time_before

    def test_print_grouped_imports(self):
        with change_to_known_repo_path("."):
            grouped_imports = self.group_imports()
            print(self.dump_ordered_json(grouped_imports))

    # TODO: Fix this: when module `dataclasses` is reloaded, its function `dataclasses.asdict` does not work anymore raising `TypeError`:
    @unittest.skip  # TODO: Comment out to run this test - if it is uncommented by default, it breaks `dataclasses.asdict` for ALL OTHER TESTS in current Python instance.
    def test_module_reload_breaks_dataclass_asdict(self):
        # given:
        shell_ctx = ShellContext(
            command_line = "whatever",
            cursor_cpos = 0,
            comp_type = CompType.PrefixShown,
            is_debug_enabled = False,
            comp_key = UNKNOWN_COMP_KEY,
        )
        call_ctx = shell_ctx.create_call_context()

        # when: use `dataclasses.asdict`:
        parsed_ctx = ParsedContext(**dataclasses.asdict(call_ctx))
        # then: it worked:
        self.assertEqual(call_ctx.command_line, parsed_ctx.command_line)

        # when: cause reload:
        importlib.reload(importlib.import_module("dataclasses"))
        # then: `dataclasses.asdict` does not work again:
        with self.assertRaises(TypeError) as e_ctx:
            parsed_ctx = ParsedContext(**dataclasses.asdict(call_ctx))
        self.assertTrue("ParsedContext.__init__() missing 5 required positional arguments:" in e_ctx.exception.args[0])
        # and:
        dict_result = dataclasses.asdict(call_ctx)
        self.assertEqual(dict_result, {}, "dict is empty")

    # TODO: Comment out to run this test - if it is uncommented by default, it breaks enum comparison for ALL OTHER TESTS in current Python instance.
    #       Apparently, when any enum class is reloaded, their id() change and their default comparison does not work:
    #       https://stackoverflow.com/a/66575463/441652
    @unittest.skip
    def test_print_imports_sorted_by_time(self):
        with change_to_known_repo_path("."):
            grouped_imports = self.group_imports()

            all_module_names = [module_name for sub_list in grouped_imports.values() for module_name in sub_list]
            unique_module_names = sorted(set(all_module_names))

            module_load_times = []
            for module_name in unique_module_names:
                load_time_ns = self.get_module_load_time_ns(module_name)
                module_size_bytes = self.module_size(module_name)
                module_load_times.append((load_time_ns, module_size_bytes, module_name))

            module_load_times.sort(key = lambda item: item[0])

            def print_row(time_ms, size_bytes, row_name):
                print(f"{time_ms:12.7f} ms: {size_bytes:>7} bytes: {row_name}")

            total_time_ms = 0
            total_size_bytes = 0
            for (load_time_ns, module_size_bytes, module_name) in module_load_times:
                display_time_ms = load_time_ns / 1_000_000
                total_time_ms += display_time_ms
                total_size_bytes += module_size_bytes
                print_row(display_time_ms, module_size_bytes, module_name)
            print("-" * 40)
            print_row(total_time_ms, total_size_bytes, "TOTAL")

    def test_ProposeArgValuesRemoteOptimizedClientCommand_imports_minimum(self):
        """
        Scan imported modules on the way from client entry point to sending data.

        Test failure should bring attention to review of the imports and keep them to the minimum.
        This is an attempt to ensure performance is not degraded because of accidental unwanted extra imports.

        Total round trip time for the client (on `Tab`) should be around ~20 ms to ~30 ms.
        But time measurement is not enforced (not done) by this test.
        Extrapolate the numbers from the commit at which this note was written based on test with debug output.

        See also:
        *  `ProposeArgValuesRemoteOptimizedClientCommand`
        *  `completion_perf_notes.md`
        """
        with change_to_known_repo_path("."):
            grouped_imports = self.group_imports()
            expected_json = self.dump_ordered_json(ThisTestClass.expected_imports)
            actual_json = self.dump_ordered_json(grouped_imports)
            self.assertEqual(
                expected_json,
                actual_json,
            )
