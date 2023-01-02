from __future__ import annotations

import contextlib
import io
import os
import re
import sys
from unittest import TestCase, mock

import mongomock
import pkg_resources
import yaml

from argrelay.data_schema.ClientConfigSchema import client_config_desc, use_local_requests_
from argrelay.data_schema.MongoConfigSchema import start_server_
from argrelay.data_schema.ServerConfigSchema import mongo_config_, server_config_desc, static_data_
from argrelay.data_schema.StaticDataSchema import static_data_desc
from argrelay.meta_data.ArgSource import ArgSource
from argrelay.meta_data.ArgValue import ArgValue
from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.RunMode import RunMode
from argrelay.meta_data.SpecialChar import SpecialChar
from argrelay.meta_data.TermColor import TermColor
from argrelay.relay_client.__main__ import main
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.runtime_context.InterpContext import assigned_types_to_values_
from misc_helper import line_no, parse_line_and_cpos
from misc_helper.OpenFileMock import OpenFileMock


def load_relay_demo_server_config_dict() -> dict:
    test_server_config_path = get_resource_path("../../demo/argrelay.server.yaml")
    with open(test_server_config_path) as f:
        server_config_dict = yaml.safe_load(f)
    # Override loaded data - do not start mongo server during testing:
    server_config_dict[mongo_config_][start_server_] = False
    return server_config_dict


def load_relay_demo_client_config_dict() -> dict:
    test_client_config_path = get_resource_path("../../demo/argrelay.client.yaml")
    with open(test_client_config_path) as f:
        client_config_dict = yaml.safe_load(f)
    # Patch config to use local server for testing:
    client_config_dict[use_local_requests_] = True
    return client_config_dict


def get_resource_path(rel_path: str):
    # Composing path to resource this way keeps its base directory always at this relative path:
    test_server_config_path = pkg_resources.resource_filename(__name__, rel_path)
    return test_server_config_path


def mock_client_env(run_mode: RunMode, command_line: str, cursor_cpos: int, comp_type: CompType):
    if run_mode == RunMode.CompletionMode:
        return mock.patch.dict(os.environ, {
            "COMP_LINE": command_line,
            "COMP_POINT": str(cursor_cpos),
            "COMP_TYPE": str(comp_type.value),
            "COMP_KEY": str(0),
        })
    if run_mode == RunMode.InvocationMode:
        return mock.patch.object(sys, 'argv', re.compile(SpecialChar.TokenDelimiter.value).split(command_line))


relay_demo_static_data_object = static_data_desc.from_input_dict(load_relay_demo_server_config_dict()[static_data_])


class ThisTestCase(TestCase):

    def test_propose_auto_comp(self):
        # @formatter:off
        test_cases = [
            (line_no(), "some_command |", CompType.PrefixHidden, "goto\ndesc\nlist", "Suggest from the set of values for the first unassigned arg type"),
            (line_no(), "some_command goto host prod amer upstream sdfg|  ", CompType.PrefixShown, "sdfg", "Still as expected with trailing space after cursor"),
            (line_no(), "some_command goto host qa prod|", CompType.SubsequentHelp, "", "Another value from the same dimension with `SubsequentHelp` => no suggestions"),
            (line_no(), "some_command host qa upstream amer qw goto ro service_c green |", CompType.PrefixShown, "", "No more suggestions when all coordinates specified"),
            (line_no(), "some_command host qa goto |", CompType.MenuCompletion, "upstream\ndownstream", "Suggestions for next coordinate show entire space"),
            (line_no(), "some_command upstream goto host |", CompType.PrefixHidden, "dev\nqa\nprod", ""),
            (line_no(), "some_command upstream goto host |",  CompType.SubsequentHelp, "dev\nqa\nprod", ""),
            # TODO: If selected token left part does not fall into next expected space, suggest from all other (yet not determined) matching that substring.
            (line_no(), "some_command host goto upstream q|", CompType.SubsequentHelp, "qa\nqw\nqwe\nqwer", "Suggestions for subsequent Tab are limited by prefix"),
            (line_no(), "some_command upstream qa apac desc |", CompType.SubsequentHelp, "qw\nqwe\nqwer\nwert\nas\nasd\nasdf\nsdfg\nzx\nzxc\nzxcv\nxcvb", ""),
            (line_no(), "some_command service upstream|", CompType.PrefixHidden, "upstream", ""),
            (line_no(), "some_command de|", CompType.PrefixHidden, "desc", "Suggest from the set of values for the first unassigned arg type (with matching prefix)"),
            (line_no(), "some_command host goto q| dev", CompType.PrefixHidden, "qw\nqwe\nqwer", "Suggestion for a value from other spaces which do not have coordinate specified"),
            (line_no(), "some_command q| dev", CompType.PrefixHidden, "", "Do not suggest a value from other spaces until they are available for query for current object to search"),
            (line_no(), "some_command pro| dev", CompType.PrefixHidden, "", "No suggestion for another value from a space which already have coordinate specified"),
            (line_no(), "some_command goto service q| whatever", CompType.PrefixHidden, "qa", "Unrecognized value does not obstruct suggestion"),
        ]
        # @formatter:on
        # TODO: DUPLICATE: hide this end-to-end setup procedure in a function and reuse across tests:

        client_config_dict = load_relay_demo_client_config_dict()
        client_config_yaml = yaml.dump(client_config_dict)

        server_config_dict = load_relay_demo_server_config_dict()
        server_config_yaml = yaml.dump(server_config_dict)

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    case_comment,
                ) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                # mock access to config files:
                file_mock = OpenFileMock({
                    client_config_desc.default_file_path: client_config_yaml,
                    server_config_desc.default_file_path: server_config_yaml,
                })
                with mock.patch("builtins.open", file_mock.open):
                    self.assertTrue(open(server_config_desc.default_file_path).read() == server_config_yaml)
                    self.assertTrue(open(client_config_desc.default_file_path).read() == client_config_yaml)

                    # mock client env:
                    with mock_client_env(RunMode.CompletionMode, command_line, cursor_cpos, comp_type):
                        # mock Mongo DB:
                        with mock.patch(
                            "argrelay.mongo_data.MongoClientWrapper.get_mongo_client",
                        ) as get_mongo_client_mock:
                            get_mongo_client_mock.return_value = mongomock.MongoClient()

                            interp_ctx = main()

                            actual_suggestions = interp_ctx.propose_auto_comp()
                            self.assertEqual(expected_suggestions, actual_suggestions)

                    file_mock.path_to_mock[
                        client_config_desc.default_file_path
                    ].assert_called_with(client_config_desc.default_file_path)

                    file_mock.path_to_mock[
                        server_config_desc.default_file_path
                    ].assert_called_with(server_config_desc.default_file_path)

    def test_describe_args(self):
        # @formatter:off
        test_cases = [
            (line_no(), "some_command goto service prod amer upstream sdfg|  ", CompType.DescribeArgs, "sdfg", "Still as expected with trailing space after cursor"),
        ]
        # @formatter:on

        # TODO: DUPLICATE: hide this end-to-end setup procedure in a function and reuse across tests:

        client_config_dict = load_relay_demo_client_config_dict()
        client_config_yaml = yaml.dump(client_config_dict)

        server_config_dict = load_relay_demo_server_config_dict()
        server_config_yaml = yaml.dump(server_config_dict)

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    case_comment
                ) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                # mock access to config files:
                file_mock = OpenFileMock({
                    client_config_desc.default_file_path: client_config_yaml,
                    server_config_desc.default_file_path: server_config_yaml,
                })
                with mock.patch("builtins.open", file_mock.open):
                    self.assertTrue(open(server_config_desc.default_file_path).read() == server_config_yaml)
                    self.assertTrue(open(client_config_desc.default_file_path).read() == client_config_yaml)

                    # mock client env:
                    with mock_client_env(RunMode.CompletionMode, command_line, cursor_cpos, comp_type):
                        # mock Mongo DB:
                        with mock.patch(
                            "argrelay.mongo_data.MongoClientWrapper.get_mongo_client",
                        ) as get_mongo_client_mock:
                            get_mongo_client_mock.return_value = mongomock.MongoClient()

                            interp_ctx = main()

                            f = io.StringIO()
                            with contextlib.redirect_stderr(f):
                                interp_ctx.invoke_action()
                                self.maxDiff = None
                                # TODO: Fix: currently (after extending data schema)
                                #       what this output shows is entire type list known to static data (it should use limited lists per object)
                                #       and it only compares it to the last `curr_assigned_types_to_values` (while it should print all `assigned_types_to_values_per_object`)
                                self.assertEqual(
                                    f"""
{TermColor.BRIGHT_YELLOW.value}*AccessType: ?{TermColor.RESET.value} ro|rw
{TermColor.BRIGHT_YELLOW.value}ActionType: ?{TermColor.RESET.value} goto|desc|list
{TermColor.DARK_GREEN.value}CodeMaturity: prod [ExplicitArg]{TermColor.RESET.value}
{TermColor.BRIGHT_YELLOW.value}ColorTag: ?{TermColor.RESET.value} red|green
{TermColor.DARK_GREEN.value}FlowStage: upstream [ExplicitArg]{TermColor.RESET.value}
{TermColor.DARK_GREEN.value}GeoRegion: amer [ExplicitArg]{TermColor.RESET.value}
{TermColor.BRIGHT_YELLOW.value}HostName: ?{TermColor.RESET.value} qw|qwe|qwer|wert|as|asd|asdf|sdfg|zx|zxc|zxcv|xcvb
{TermColor.BRIGHT_YELLOW.value}ObjectSelector: ?{TermColor.RESET.value} host|service
{TermColor.BRIGHT_YELLOW.value}ServiceName: ?{TermColor.RESET.value} service_a|service_b|service_c
""",
                                    f.getvalue()
                                )

                    file_mock.path_to_mock[
                        client_config_desc.default_file_path
                    ].assert_called_with(client_config_desc.default_file_path)

                    file_mock.path_to_mock[
                        server_config_desc.default_file_path
                    ].assert_called_with(server_config_desc.default_file_path)

    def test_arg_assignments_for_completion(self):
        # @formatter:off
        test_cases = [
            (line_no(), RunMode.CompletionMode, "some_command goto|", CompType.PrefixShown, 0, {ServiceArgType.ActionType.name: None, ServiceArgType.ObjectSelector.name: None}, "No assignment for incomplete token"),
            (line_no(), RunMode.CompletionMode, "some_command goto |", CompType.PrefixShown, 0, {ServiceArgType.ActionType.name: ArgValue("goto", ArgSource.ExplicitArg), ServiceArgType.ObjectSelector.name: None}, "Explicit assignment for complete token"),
            (line_no(), RunMode.CompletionMode, "some_command goto service |", CompType.PrefixShown, 0, {ServiceArgType.ActionType.name: ArgValue("goto", ArgSource.ExplicitArg), ServiceArgType.ObjectSelector.name: ArgValue("service", ArgSource.ExplicitArg)}, "Explicit assignment for complete token"),

            (line_no(), RunMode.CompletionMode, "some_command goto host prod|", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: None, ServiceArgType.AccessType.name: None}, "No implicit assignment for incomplete token"),
            # TODO: re-implement functionality via data - see `CodeMaturityProcessor`:
            #(line_no(), RunMode.InvocationMode, "some_command goto host prod|", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: ArgValue("prod", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: ArgValue("ro", ArgSource.ImplicitValue)}, "Implicit assignment even for incomplete token (token pointed by cursor)"),

            (line_no(), RunMode.CompletionMode, "some_command goto host prod |", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: ArgValue("prod", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: None}, "No implicit assignment of access type to \"ro\" when code maturity is \"prod\" in completion"),
            # TODO: re-implement functionality via data - see `CodeMaturityProcessor`:
            #(line_no(), RunMode.InvocationMode, "some_command goto host prod |", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: ArgValue("prod", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: ArgValue("ro", ArgSource.ImplicitValue)}, "Implicit assignment of access type to \"ro\" when code maturity is \"prod\" in invocation"),

            (line_no(), RunMode.CompletionMode, "some_command goto host dev |", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: ArgValue("dev", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: None}, "No implicit assignment of access type to \"rw\" when code maturity is \"dev\" in completion"),
            # TODO: re-implement functionality via data - see `CodeMaturityProcessor`:
            #(line_no(), RunMode.InvocationMode, "some_command goto host dev |", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: ArgValue("dev", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: ArgValue("rw", ArgSource.ImplicitValue)}, "Implicit assignment of access type to \"rw\" when code maturity is \"uat\" in invocation"),
        ]
        # @formatter:on

        # TODO: DUPLICATE: hide this end-to-end setup procedure in a function and reuse across tests:

        client_config_dict = load_relay_demo_client_config_dict()
        client_config_yaml = yaml.dump(client_config_dict)

        server_config_dict = load_relay_demo_server_config_dict()
        server_config_yaml = yaml.dump(server_config_dict)

        for test_case in test_cases:

            with self.subTest(test_case):
                (
                    line_number,
                    run_mode,
                    test_line,
                    comp_type,
                    found_object_ipos,
                    expected_assignments,
                    case_comment,
                ) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                # mock access to config files:
                file_mock = OpenFileMock({
                    client_config_desc.default_file_path: client_config_yaml,
                    server_config_desc.default_file_path: server_config_yaml,
                })
                with mock.patch("builtins.open", file_mock.open):
                    self.assertTrue(open(server_config_desc.default_file_path).read() == server_config_yaml)
                    self.assertTrue(open(client_config_desc.default_file_path).read() == client_config_yaml)

                    # mock client env:
                    with mock_client_env(run_mode, command_line, cursor_cpos, comp_type):

                        # mock Mongo DB:
                        with mock.patch(
                            "argrelay.mongo_data.MongoClientWrapper.get_mongo_client",
                        ) as get_mongo_client_mock:
                            get_mongo_client_mock.return_value = mongomock.MongoClient()

                            interp_ctx = main()

                            for arg_type, arg_value in expected_assignments.items():
                                if arg_value is None:
                                    self.assertTrue(
                                        arg_type not in
                                        interp_ctx.assigned_types_to_values_per_object
                                        [found_object_ipos]
                                        [assigned_types_to_values_]
                                    )
                                else:
                                    self.assertEqual(
                                        arg_value,
                                        interp_ctx.assigned_types_to_values_per_object
                                        [found_object_ipos]
                                        [assigned_types_to_values_]
                                        [arg_type]
                                    )

                    file_mock.path_to_mock[
                        client_config_desc.default_file_path
                    ].assert_called_with(client_config_desc.default_file_path)

                    file_mock.path_to_mock[
                        server_config_desc.default_file_path
                    ].assert_called_with(server_config_desc.default_file_path)
