from marshmallow import Schema, RAISE, fields, post_load

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.schema_config_core_client.ConnectionConfigSchema import connection_config_desc

__comment___ = "__comment__"
connection_config_ = "connection_config"
use_local_requests_ = "use_local_requests"
optimize_completion_request_ = "optimize_completion_request"


class ClientConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    # Allow this field in JSON (otherwise schema validation fails):
    __comment__ = fields.String(
        required = False,
    )

    # Serve requests from local data or send to server
    # (used in test only - see `LocalClient` and FS_66_17_43_42 test infra):
    use_local_requests = fields.Boolean(
        required = False,
    )

    # Use one of these (default = True):
    # *   if True: ProposeArgValuesRemoteOptimizedClientCommand
    # *   if False: ProposeArgValuesRemoteClientCommand
    optimize_completion_request = fields.Boolean(
        required = False,
    )

    connection_config = fields.Nested(connection_config_desc.dict_schema)

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        return ClientConfig(
            use_local_requests = input_dict.get(use_local_requests_, False),
            optimize_completion_request = input_dict.get(optimize_completion_request_, True),
            connection_config = input_dict[connection_config_],
        )


client_config_desc = TypeDesc(
    dict_schema = ClientConfigSchema(),
    ref_name = ClientConfigSchema.__name__,
    dict_example = {
        connection_config_: connection_config_desc.dict_example,
    },
    default_file_path = "argrelay.client.json",
)
