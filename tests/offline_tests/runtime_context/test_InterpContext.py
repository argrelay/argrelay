from __future__ import annotations

from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.AbstractArg import ArgCommandValueOffered, ArgCommandValueDictated
from argrelay.runtime_context.DataArg import ArgCommandValueOfferedData, ArgCommandValueDictatedData
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_config_plugin.PluginConfigSchema import plugin_config_desc
from argrelay.test_infra import line_no_from_ctor
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.CustomTestCase import ShellInputTestCase
from argrelay.test_infra.EnvMockBuilder import default_test_parsed_context, ServerOnlyEnvMockBuilder


class ThisTestCase(ShellInputTestCase):

    def __init__(
        self,
        test_line: str,
        comp_type: CompType,
        expected_token_buckets: list[list[int]],
        expected_excluded_tokens: list[int],
        expected_token_ipos_to_token_bucket_map: dict[int, int],
        expected_offered_args_per_bucket: list[list[ArgCommandValueOffered]],
        expected_dictated_args_per_bucket: list[list[ArgCommandValueDictated]],
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
        self.expected_offered_args_per_bucket = expected_offered_args_per_bucket
        self.expected_dictated_args_per_bucket = expected_dictated_args_per_bucket

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
            self.expected_offered_args_per_bucket,
            self.expected_dictated_args_per_bucket,
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
                    "|", CompType.InvokeAction,
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
                    "empty line",
                ),
                ThisTestCase(
                    "a|", CompType.PrefixShown,
                    [
                        [],
                    ],
                    [0],
                    {},
                    [
                        [],
                    ],
                    [
                        [],
                    ],
                    "case A: with tangent token excluded: single arg, no bucket separator",
                ),
                ThisTestCase(
                    "a|", CompType.InvokeAction,
                    [
                        [0],
                    ],
                    [],
                    {
                        0: 0,
                    },
                    [
                        [
                            ArgCommandValueOfferedData(
                                token_ipos_list = [0],
                                arg_value = "a",
                            ),
                        ],
                    ],
                    [
                        [],
                    ],
                    "case B: with tangent token included: single arg, no bucket separator",
                ),
                ThisTestCase(
                    "% a|", CompType.InvokeAction,
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
                            ArgCommandValueOfferedData(
                                token_ipos_list = [1],
                                arg_value = "a",
                            ),
                        ],
                    ],
                    [
                        [],
                        [],
                    ],
                    "single arg + bucket separator before",
                ),
                ThisTestCase(
                    "a %|", CompType.InvokeAction,
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
                            ArgCommandValueOfferedData(
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
                    "single arg + bucket separator after",
                ),
                ThisTestCase(
                    "%a|", CompType.InvokeAction,
                    [
                        [0],
                    ],
                    [],
                    {
                        0: 0,
                    },
                    [
                        [
                            ArgCommandValueOfferedData(
                                token_ipos_list = [0],
                                arg_value = "%a",
                            ),
                        ],
                    ],
                    [
                        [],
                    ],
                    "single arg concatenated with bucket separator before",
                ),
                ThisTestCase(
                    "a%|", CompType.InvokeAction,
                    [
                        [0],
                    ],
                    [],
                    {
                        0: 0,
                    },
                    [
                        [
                            ArgCommandValueOfferedData(
                                token_ipos_list = [0],
                                arg_value = "a%",
                            ),
                        ],
                    ],
                    [
                        [],
                    ],
                    "single arg concatenated with bucket separator after",
                ),
                ThisTestCase(
                    "% qwer % asdf % zxcv %    |", CompType.InvokeAction,
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
                            ArgCommandValueOfferedData(
                                token_ipos_list = [1],
                                arg_value = "qwer",
                            ),
                        ],
                        [
                            ArgCommandValueOfferedData(
                                token_ipos_list = [3],
                                arg_value = "asdf",
                            ),
                        ],
                        [
                            ArgCommandValueOfferedData(
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
                    "multiple `token_bucket`-s with single `command_token` only",
                ),
                ThisTestCase(
                    "% qwer asdf zxcv % qwer asdf % zxcv %    |", CompType.InvokeAction,
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
                            ArgCommandValueOfferedData(
                                token_ipos_list = [1],
                                arg_value = "qwer",
                            ),
                            ArgCommandValueOfferedData(
                                token_ipos_list = [2],
                                arg_value = "asdf",
                            ),
                            ArgCommandValueOfferedData(
                                token_ipos_list = [3],
                                arg_value = "zxcv",
                            ),
                        ],
                        [
                            ArgCommandValueOfferedData(
                                token_ipos_list = [5],
                                arg_value = "qwer",
                            ),
                            ArgCommandValueOfferedData(
                                token_ipos_list = [6],
                                arg_value = "asdf",
                            ),
                        ],
                        [
                            ArgCommandValueOfferedData(
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
                    "multiple `arg_bucket`-s with multiple `command_token`-s",
                ),
                ThisTestCase(
                    "-dictated_arg_name1 dictated_arg_value1 offered_arg_value1 |", CompType.InvokeAction,
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
                            ArgCommandValueOfferedData(
                                token_ipos_list = [2],
                                arg_value = "offered_arg_value1",
                            ),
                        ],
                    ],
                    [
                        [
                            ArgCommandValueDictatedData(
                                token_ipos_list = [0, 1],
                                arg_value = "dictated_arg_value1",
                                arg_name = "-dictated_arg_name1",
                            ),
                        ],
                    ],
                    "parse well-formed `dictated_arg` and "
                    "well-formed `offered_arg_value`",
                ),
                ThisTestCase(
                    "-dictated_arg_name1 dictated_arg_value1 -dictated_arg_name2 |", CompType.InvokeAction,
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
                            ArgCommandValueDictatedData(
                                token_ipos_list = [0, 1],
                                arg_value = "dictated_arg_value1",
                                arg_name = "-dictated_arg_name1",
                            ),
                        ],
                    ],
                    "parse first well-formed `dictated_arg` and "
                    "second ill-formed `dictated_arg` (missing value)",
                ),
                ThisTestCase(
                    "-dictated_arg_name1 -dictated_arg_value1 offered_arg_value2 |", CompType.InvokeAction,
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
                            ArgCommandValueOfferedData(
                                token_ipos_list = [2],
                                arg_value = "offered_arg_value2",
                            ),
                        ],
                    ],
                    [
                        [
                            ArgCommandValueDictatedData(
                                token_ipos_list = [0, 1],
                                arg_value = "-dictated_arg_value1",
                                arg_name = "-dictated_arg_name1",
                            ),
                        ],
                    ],
                    "parse first well-formed `dictated_arg` "
                    "(with value which only looks like start of another `dictated_arg`) and "
                    "second well-formed `offered_arg_value`",
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
                        expected_offered_args_per_bucket,
                        expected_dictated_args_per_bucket,
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
                        interp_ctx.offered_args_per_bucket,
                        expected_offered_args_per_bucket,
                    )
                    self.assertEqual(
                        interp_ctx.dictated_args_per_bucket,
                        expected_dictated_args_per_bucket,
                    )
