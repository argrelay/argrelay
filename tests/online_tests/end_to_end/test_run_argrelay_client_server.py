import os
import subprocess

from argrelay.client_spec.ShellContext import (
    COMP_LINE_env_var,
    COMP_POINT_env_var,
    COMP_TYPE_env_var,
    COMP_KEY_env_var,
    UNKNOWN_COMP_KEY,
)
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.TermColor import TermColor
from argrelay.handler_response.DescribeLineArgsClientResponseHandler import indent_size
from argrelay.misc_helper import eprint
from argrelay.test_helper import change_to_known_repo_path, parse_line_and_cpos
from online_tests.end_to_end.End2EndTest import (
    End2EndTest,
    run_client_with_env_vars,
)

client_command_env_var_name_ = "ARGRELAY_CLIENT_COMMAND"


# noinspection PyMethodMayBeStatic
class ThisTestCase(End2EndTest):

    def test_DescribeLineArgs(self):
        """
        Invokes client via generated `@/bin/run_argrelay_client` sending `ServerAction.DescribeArgs`.
        """
        test_line = f"{os.environ.get(client_command_env_var_name_)} goto h|"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        env_vars = os.environ.copy()
        env_vars[COMP_LINE_env_var] = command_line
        env_vars[COMP_POINT_env_var] = str(cursor_cpos)
        env_vars[COMP_TYPE_env_var] = str(CompType.DescribeArgs.value)
        env_vars[COMP_KEY_env_var] = UNKNOWN_COMP_KEY

        with change_to_known_repo_path("."):

            client_proc = run_client_with_env_vars(env_vars)
            described_args = client_proc.stderr.decode("utf-8")
            eprint(f"described_args: {described_args}")

            self.assertEqual(
                f"""
{TermColor.consumed_token.value}{os.environ.get(client_command_env_var_name_)}{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}h{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: 2
{" " * indent_size}{TermColor.other_assigned_arg_value.value}FunctionCategory: external {TermColor.other_assigned_arg_value.value}[{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}ActionType: goto {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*ObjectSelector: ?{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}h{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}ost{TermColor.reset_style.value} service 
""",
                described_args
            )

    def test_ProposeArgValues(self):
        """
        Invokes client via generated `@/bin/run_argrelay_client` sending `ServerAction.ProposeArgValues`.
        """
        test_line = f"{os.environ.get(client_command_env_var_name_)} desc host dev upstream a|"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        env_vars = os.environ.copy()
        env_vars[COMP_LINE_env_var] = command_line
        env_vars[COMP_POINT_env_var] = str(cursor_cpos)
        env_vars[COMP_TYPE_env_var] = str(CompType.PrefixShown.value)
        env_vars[COMP_KEY_env_var] = UNKNOWN_COMP_KEY

        with change_to_known_repo_path("."):

            client_proc = run_client_with_env_vars(env_vars)
            proposed_args = client_proc.stdout.decode("utf-8").strip().splitlines()

            self.assertEqual(
                [
                    "apac",
                    "amer",
                ],
                proposed_args
            )

    def test_RelayLineArgs(self):
        """
        Invokes client via generated `@/bin/run_argrelay_client` sending `ServerAction.RelayLineArgs`.
        """

        with change_to_known_repo_path("."):
            # Function "desc_host" ("desc host") uses `NoopDelegator`, so the test should always pass:
            client_proc = subprocess.run(
                args = f"{os.environ.get(client_command_env_var_name_)} desc host dev upstream amer".split(" "),
            )
            ret_code = client_proc.returncode
            if ret_code != 0:
                raise RuntimeError
