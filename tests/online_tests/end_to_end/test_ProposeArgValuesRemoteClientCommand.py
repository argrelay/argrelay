import os

from argrelay.client_spec.ShellContext import (
    COMP_LINE_env_var,
    COMP_POINT_env_var,
    COMP_TYPE_env_var,
    COMP_KEY_env_var,
    UNKNOWN_COMP_KEY,
)
from argrelay.enum_desc.CompType import CompType
from argrelay.test_helper import change_to_known_repo_path, parse_line_and_cpos
from online_tests.end_to_end.End2EndTest import (
    End2EndTest,
    client_command_env_var_name_,
    run_client_with_env_vars,
)


class ThisTestCase(End2EndTest):

    def test_ProposeArgValuesRemoteClientCommand_sends_valid_JSON_for_commands_with_quotes(self):
        """
        Invokes client via generated `@/bin/run_argrelay_client` sending `ServerAction.ProposeArgValues`.
        """
        test_line = f"{os.environ.get(client_command_env_var_name_)} desc host dev \"some_unrecognized_token\" upstream a|"
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
