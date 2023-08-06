import dataclasses
from unittest import TestCase

from argrelay.enum_desc.CompType import CompType
from argrelay.relay_server.__main__ import create_app
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_request.RequestContextSchema import request_context_desc
from argrelay.server_spec.const_int import (
    RELAY_LINE_ARGS_PATH,
)
from argrelay.test_helper.EnvMockBuilder import ServerOnlyEnvMockBuilder


class ThisTestCase(TestCase):

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
            .set_test_data_ids_to_load([
                "TD_63_37_05_36"  # demo
            ])
        )
        with env_mock_builder.build():
            self.assertTrue(
                open(server_config_desc.default_file_path).read() == env_mock_builder.get_server_config_yaml()
            )

            flask_app = create_app()
            self.ctx = flask_app.app_context()
            self.ctx.push()
            self.client = flask_app.test_client()

            env_mock_builder.assert_server_config_read()

            data_obj = dataclasses.replace(
                request_context_desc.dict_schema.load(request_context_desc.dict_example),
                comp_type = CompType.InvokeAction,
                command_line = "some_command goto service prod wert-pd-1",
            )
            response = self.client.post(
                RELAY_LINE_ARGS_PATH,
                json = request_context_desc.dict_schema.dumps(data_obj),
            )
            self.assertEqual(200, response.status_code)
