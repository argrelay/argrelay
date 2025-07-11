import dataclasses

from argrelay_api_server_cli.schema_request.CallContextSchema import call_context_desc
from argrelay_app_server.relay_server.__main__ import create_app
from argrelay_lib_root.enum_desc.ServerAction import ServerAction
from argrelay_schema_config_server.schema_config_server_app.ServerConfigSchema import (
    server_config_desc,
)
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass
from argrelay_test_infra.test_infra.EnvMockBuilder import ServerOnlyEnvMockBuilder


class ThisTestClass(BaseTestClass):

    def test_data_dump_on_server_with_non_serializable_id(self):
        """
        When `data_envelope`-s are stored into data store without `_id` field,
        the `_id` field is generated as `ObjectId` instance.
        When they are subsequently queried from data store,
        `_id` field cannot be serialized by `Schema.dump`.
        This was fixed by filtering such field -
        for `argrelay`, if unique id is required, `envelope_id_` must be used.
        """

        env_mock_builder = (
            ServerOnlyEnvMockBuilder()
            # Load all data:
            .set_test_data_ids_to_load(["TD_63_37_05_36"])  # demo
        )
        with env_mock_builder.build():
            self.assertTrue(
                open(server_config_desc.get_adjusted_file_path()).read()
                == env_mock_builder.get_server_config_yaml()
            )

            flask_app = create_app()
            self.ctx = flask_app.app_context()
            self.ctx.push()
            self.client = flask_app.test_client()

            env_mock_builder.assert_server_config_read()

            data_obj = dataclasses.replace(
                call_context_desc.dict_schema.load(call_context_desc.dict_example),
                server_action=ServerAction.RelayLineArgs,
                command_line="some_command goto service prod wert-pd-1",
            )
            response = self.client.post(
                ServerAction.RelayLineArgs.value,
                data=call_context_desc.dict_schema.dumps(data_obj),
            )
            self.assertEqual(200, response.status_code)
