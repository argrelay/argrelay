from __future__ import annotations

from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_app_server.runtime_context.AbstractArg import (
    ArgCommandValueDictated,
    ArgCommandValueOffered,
)
from argrelay_app_server.runtime_context.DataArg import (
    ArgCommandDataIncomplete,
    ArgCommandDataValueDictated,
    ArgCommandDataValueOffered,
)
from argrelay_app_server.runtime_context.InterpContext import InterpContext
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.SpecialChar import SpecialChar
from argrelay_schema_config_server.schema_config_server_app.ServerConfigSchema import server_config_desc
from argrelay_schema_config_server.schema_config_server_plugin.PluginConfigSchema import plugin_config_desc
from argrelay_test_infra.test_infra import line_no_from_ctor
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass
from argrelay_test_infra.test_infra.CustomTestCase import ShellInputTestCase
from argrelay_test_infra.test_infra.EnvMockBuilder import (
    default_test_parsed_context,
    ServerOnlyEnvMockBuilder,
)


class ThisTestCase(ShellInputTestCase):

    def __init__(
        self,
        test_line: str,
        comp_type: CompType,
        expected_token_buckets: list[list[int]],
        expected_excluded_tokens: list[int],
        expected_token_ipos_to_token_bucket_map: dict[int, int],
        expected_remaining_offered_args_per_bucket: list[list[ArgCommandValueOffered]],
        expected_remaining_dictated_args_per_bucket: list[list[ArgCommandValueDictated]],
        expected_remaining_incomplete_args_per_bucket: list[list[ArgCommandDataIncomplete]],
        case_comment: str,
    ):
        super().__init__(
            line_no = line_no_from_ctor(),
            case_comment = case_comment,
        )
        self.set_test_line(test_line)
        self.set_comp_type(comp_type)
        self.expected_token_buckets = expected_token_buckets
        self.expected_excluded_tokens = expected_excluded_tokens
        self.expected_token_ipos_to_token_bucket_map = expected_token_ipos_to_token_bucket_map
        self.expected_remaining_offered_args_per_bucket = expected_remaining_offered_args_per_bucket
        self.expected_remaining_dictated_args_per_bucket = expected_remaining_dictated_args_per_bucket
        self.expected_remaining_incomplete_args_per_bucket = expected_remaining_incomplete_args_per_bucket

    def __iter__(self):
        return iter((
            self.line_no,
            self.case_comment,
            self.command_line,
            self.cursor_cpos,
            self.comp_type,
            self.expected_token_buckets,
            self.expected_excluded_tokens,
            self.expected_token_ipos_to_token_bucket_map,
            self.expected_remaining_offered_args_per_bucket,
            self.expected_remaining_dictated_args_per_bucket,
            self.expected_remaining_incomplete_args_per_bucket,
        ))


class ThisTestClass(BaseTestClass):
    """
    Tests parsing of FS_97_64_39_94 `token_bucket`-s.
    """

    def test_parse_input(self):
        # In this test:
        # *   initialize mock once
        # *   start server once
        # *   reuse that for all tests
        env_mock_builder = (
            ServerOnlyEnvMockBuilder()
            .set_test_data_ids_to_load([
                "TD_63_37_05_36",  # demo
            ])
        )
        with env_mock_builder.build():
            # Init `LocalServer` with data:
            dummy_server_config = server_config_desc.obj_from_default_file()
            dummy_plugin_config = plugin_config_desc.obj_from_default_file()
            dummy_local_server = LocalServer(
                dummy_server_config,
                dummy_plugin_config,
            )

            assert "%" == SpecialChar.TokenBucketDelimiter.value, "if not `%`, update test cases"

            test_cases = [
                ThisTestCase(
                    "|",
                    CompType.InvokeAction,
                    [
                        [],
                    ],
                    [],
                    {},
                    [
                        [],
                    ],
                    [
                        [],
                    ],
                    [
                        [],
                    ],
                    "empty line",
                ),
                ThisTestCase(
                    "a|", CompType.PrefixShown,
                    [
                        [],
                    ],
                    [0],
                    {
                        0: 0,
                    },
                    [
                        [],
                    ],
                    [
                        [],
                    ],
                    [
                        [],
                    ],
                    "case A: with `tangent_token` excluded as for `ServerAction.ProposeArgValues`: single arg, no bucket separator",
                ),
                ThisTestCase(
                    "a|",
                    CompType.InvokeAction,
                    [
                        [0],
                    ],
                    [],
                    {
                        0: 0,
                    },
                    [
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [0],
                                arg_value = "a",
                            ),
                        ],
                    ],
                    [
                        [],
                    ],
                    [
                        [],
                    ],
                    "case B: with `tangent_token` included for NOT `ServerAction.ProposeArgValues`: single arg, no bucket separator",
                ),
                ThisTestCase(
                    "% a|",
                    CompType.InvokeAction,
                    [
                        [],
                        # bucket separator is counted as a token - next token is at index = 1 (not 0):
                        [1],
                    ],
                    [0],
                    {
                        1: 1,
                    },
                    [
                        [],
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [1],
                                arg_value = "a",
                            ),
                        ],
                    ],
                    [
                        [],
                        [],
                    ],
                    [
                        [],
                        [],
                    ],
                    "single arg + bucket separator before",
                ),
                ThisTestCase(
                    "a %|",
                    CompType.InvokeAction,
                    [
                        [0],
                        [],
                    ],
                    [1],
                    {
                        0: 0,
                    },
                    [
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [0],
                                arg_value = "a",
                            ),
                        ],
                        [],
                    ],
                    [
                        [],
                        [],
                    ],
                    [
                        [],
                        [],
                    ],
                    "single arg + bucket separator after",
                ),
                ThisTestCase(
                    "%a|",
                    CompType.InvokeAction,
                    [
                        [0],
                    ],
                    [],
                    {
                        0: 0,
                    },
                    [
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [0],
                                arg_value = "%a",
                            ),
                        ],
                    ],
                    [
                        [],
                    ],
                    [
                        [],
                    ],
                    "single arg concatenated with bucket separator before",
                ),
                ThisTestCase(
                    "a%|",
                    CompType.InvokeAction,
                    [
                        [0],
                    ],
                    [],
                    {
                        0: 0,
                    },
                    [
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [0],
                                arg_value = "a%",
                            ),
                        ],
                    ],
                    [
                        [],
                    ],
                    [
                        [],
                    ],
                    "single arg concatenated with bucket separator after",
                ),
                ThisTestCase(
                    "% qwer % asdf % zxcv %    |",
                    CompType.InvokeAction,
                    [
                        [],
                        [1],
                        [3],
                        [5],
                        [],
                    ],
                    [0, 2, 4, 6],
                    {
                        1: 1,
                        3: 2,
                        5: 3,
                    },
                    [
                        [],
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [1],
                                arg_value = "qwer",
                            ),
                        ],
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [3],
                                arg_value = "asdf",
                            ),
                        ],
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [5],
                                arg_value = "zxcv",
                            ),
                        ],
                        [],
                    ],
                    [
                        [],
                        [],
                        [],
                        [],
                        [],
                    ],
                    [
                        [],
                        [],
                        [],
                        [],
                        [],
                    ],
                    "multiple `token_bucket`-s with single `command_token` only",
                ),
                ThisTestCase(
                    "% qwer asdf zxcv % qwer asdf % zxcv %    |",
                    CompType.InvokeAction,
                    [
                        [],
                        [1, 2, 3],
                        [5, 6],
                        [8],
                        [],
                    ],
                    [0, 4, 7, 9],
                    {
                        1: 1,
                        2: 1,
                        3: 1,
                        5: 2,
                        6: 2,
                        8: 3,
                    },
                    [
                        [],
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [1],
                                arg_value = "qwer",
                            ),
                            ArgCommandDataValueOffered(
                                token_ipos_list = [2],
                                arg_value = "asdf",
                            ),
                            ArgCommandDataValueOffered(
                                token_ipos_list = [3],
                                arg_value = "zxcv",
                            ),
                        ],
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [5],
                                arg_value = "qwer",
                            ),
                            ArgCommandDataValueOffered(
                                token_ipos_list = [6],
                                arg_value = "asdf",
                            ),
                        ],
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [8],
                                arg_value = "zxcv",
                            ),
                        ],
                        [],
                    ],
                    [
                        [],
                        [],
                        [],
                        [],
                        [],
                    ],
                    [
                        [],
                        [],
                        [],
                        [],
                        [],
                    ],
                    "multiple `arg_bucket`-s with multiple `command_token`-s",
                ),
                ThisTestCase(
                    "-dictated_arg_name1 dictated_arg_value1 offered_arg_value1 |",
                    CompType.InvokeAction,
                    [
                        [0, 1, 2],
                    ],
                    [],
                    {
                        0: 0,
                        1: 0,
                        2: 0,
                    },
                    [
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [2],
                                arg_value = "offered_arg_value1",
                            ),
                        ],
                    ],
                    [
                        [
                            ArgCommandDataValueDictated(
                                token_ipos_list = [0, 1],
                                arg_value = "dictated_arg_value1",
                                arg_name = "dictated_arg_name1",
                            ),
                        ],
                    ],
                    [
                        [],
                    ],
                    "parse well-formed `dictated_arg` and "
                    "well-formed `offered_arg_value`",
                ),
                ThisTestCase(
                    "-dictated_arg_name1 dictated_arg_value1 -incomplete_arg_name2 |",
                    CompType.InvokeAction,
                    [
                        [0, 1, 2],
                    ],
                    [],
                    {
                        0: 0,
                        1: 0,
                        2: 0,
                    },
                    [
                        [],
                    ],
                    [
                        [
                            ArgCommandDataValueDictated(
                                token_ipos_list = [0, 1],
                                arg_value = "dictated_arg_value1",
                                arg_name = "dictated_arg_name1",
                            ),
                        ],
                    ],
                    [
                        [
                            ArgCommandDataIncomplete(
                                token_ipos_list = [2],
                                arg_name = "incomplete_arg_name2",
                            ),
                        ],
                    ],
                    "parse first well-formed `dictated_arg` and "
                    "second ill-formed `dictated_arg` (missing value) which becomes FS_08_58_30_24 `incomplete_arg`",
                ),
                ThisTestCase(
                    "-dictated_arg_name1 -dictated_arg_value1 offered_arg_value2 |",
                    CompType.InvokeAction,
                    [
                        [0, 1, 2],
                    ],
                    [],
                    {
                        0: 0,
                        1: 0,
                        2: 0,
                    },
                    [
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [2],
                                arg_value = "offered_arg_value2",
                            ),
                        ],
                    ],
                    [
                        [
                            ArgCommandDataValueDictated(
                                token_ipos_list = [0, 1],
                                arg_value = "-dictated_arg_value1",
                                arg_name = "dictated_arg_name1",
                            ),
                        ],
                    ],
                    [
                        [],
                    ],
                    "parse first well-formed `dictated_arg` "
                    "(with value which only looks like start of another `dictated_arg`) and "
                    "second well-formed `offered_arg_value`",
                ),
                ThisTestCase(
                    "-incomplete_arg_name1 |",
                    CompType.InvokeAction,
                    [
                        [0],
                    ],
                    [],
                    {
                        0: 0,
                    },
                    [
                        [],
                    ],
                    [
                        [],
                    ],
                    [
                        [
                            ArgCommandDataIncomplete(
                                token_ipos_list = [0],
                                arg_name = "incomplete_arg_name1",
                            ),
                        ],
                    ],
                    "Parse single `incomplete_arg`.",
                ),
                ThisTestCase(
                    "-incomplete_arg_name1 % -incomplete_arg_name2 |",
                    CompType.InvokeAction,
                    [
                        [0],
                        [2],
                    ],
                    [1],
                    {
                        0: 0,
                        2: 1,
                    },
                    [
                        [],
                        [],
                    ],
                    [
                        [],
                        [],
                    ],
                    [
                        [
                            ArgCommandDataIncomplete(
                                token_ipos_list = [0],
                                arg_name = "incomplete_arg_name1",
                            ),
                        ],
                        [
                            ArgCommandDataIncomplete(
                                token_ipos_list = [2],
                                arg_name = "incomplete_arg_name2",
                            ),
                        ],
                    ],
                    "Parse FS_08_58_30_24 `incomplete_arg`-s - one for each `token_bucket`.",
                ),
                ThisTestCase(
                    "offered_arg_value1 -incomplete_arg_name2 % -dictated_arg_name3 dictated_arg_value3 -incomplete_arg_name4 |",
                    CompType.InvokeAction,
                    [
                        [0, 1],
                        [3, 4, 5],
                    ],
                    [2],
                    {
                        0: 0,
                        1: 0,
                        3: 1,
                        4: 1,
                        5: 1,
                    },
                    [
                        [
                            ArgCommandDataValueOffered(
                                token_ipos_list = [0],
                                arg_value = "offered_arg_value1",
                            ),
                        ],
                        [],
                    ],
                    [
                        [],
                        [
                            ArgCommandDataValueDictated(
                                token_ipos_list = [3, 4],
                                arg_value = "dictated_arg_value3",
                                arg_name = "dictated_arg_name3",
                            ),
                        ],
                    ],
                    [
                        [
                            ArgCommandDataIncomplete(
                                token_ipos_list = [1],
                                arg_name = "incomplete_arg_name2",
                            ),
                        ],
                        [
                            ArgCommandDataIncomplete(
                                token_ipos_list = [5],
                                arg_name = "incomplete_arg_name4",
                            ),
                        ],
                    ],
                    "Parse combination of `offered_arg`, `dictated_arg`, `incomplete_arg` "
                    "in different `token_bucket`-s.",
                ),
            ]
            for test_case in test_cases:

                with self.subTest(test_case):
                    (
                        line_number,
                        case_comment,
                        command_line,
                        cursor_cpos,
                        comp_type,
                        expected_token_buckets,
                        expected_excluded_tokens,
                        expected_token_ipos_to_token_bucket_map,
                        expected_remaining_offered_args_per_bucket,
                        expected_remaining_dictated_args_per_bucket,
                        expected_remaining_incomplete_args_per_bucket,
                    ) = test_case

                    parsed_ctx = default_test_parsed_context(
                        command_line,
                        cursor_cpos,
                        comp_type,
                    )
                    interp_ctx: InterpContext = InterpContext(
                        parsed_ctx = parsed_ctx,
                        interp_factories = dummy_local_server.server_config.interp_factories,
                        action_delegators = dummy_local_server.server_config.action_delegators,
                        query_engine = dummy_local_server.get_query_engine(),
                        help_hint_cache = dummy_local_server.help_hint_cache,
                    )
                    self.assertEqual(
                        expected_token_buckets,
                        interp_ctx.included_token_buckets,
                    )
                    self.assertEqual(
                        expected_token_buckets,
                        interp_ctx.remaining_token_buckets,
                    )
                    self.assertEqual(
                        [[] for i in interp_ctx.included_token_buckets],
                        interp_ctx.consumed_token_buckets,
                    )
                    self.assertEqual(
                        expected_excluded_tokens,
                        interp_ctx.excluded_tokens,
                    )
                    self.assertEqual(
                        expected_token_ipos_to_token_bucket_map,
                        interp_ctx.token_ipos_to_token_bucket_map,
                    )
                    self.assertEqual(
                        [],
                        interp_ctx.consumed_token_ipos_list(),
                    )
                    self.assertEqual(
                        list(range(0, len(parsed_ctx.all_tokens))),
                        sorted(
                            interp_ctx.consumed_token_ipos_list()
                            +
                            interp_ctx.remaining_token_ipos_list()
                            +
                            interp_ctx.excluded_tokens
                        ),
                    )
                    self.assertEqual(
                        interp_ctx.remaining_offered_args_per_bucket,
                        expected_remaining_offered_args_per_bucket,
                    )
                    self.assertEqual(
                        interp_ctx.remaining_dictated_args_per_bucket,
                        expected_remaining_dictated_args_per_bucket,
                    )
                    self.assertEqual(
                        interp_ctx.remaining_incomplete_args_per_bucket,
                        expected_remaining_incomplete_args_per_bucket,
                    )
