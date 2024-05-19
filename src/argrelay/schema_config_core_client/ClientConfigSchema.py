from marshmallow import RAISE, fields

from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.schema_config_core_client.ConnectionConfigSchema import connection_config_desc

__comment___ = "__comment__"
connection_config_ = "connection_config"
use_local_requests_ = "use_local_requests"
optimize_completion_request_ = "optimize_completion_request"
show_pending_spinner_ = "show_pending_spinner"
spinless_sleep_sec_ = "spinless_sleep_sec"


# NOTE: Client does not use `Schema` to load config in prod code
#       (only in tests due to heavy import caused by `Schema`).
#       Therefore, validation and applying defaults is not done by this class.
#       Duplicate the same requirements (for validation and defaults) in client prod code.
class ClientConfigSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = ClientConfig

    # Allow this field in JSON (otherwise schema validation fails):
    __comment__ = fields.String(
        required = False,
        load_default = "",
    )

    # Serve requests from local data or send to server
    # (used in test only - see `LocalClient` and FS_66_17_43_42 test infra):
    use_local_requests = fields.Boolean(
        required = False,
        load_default = False,
    )

    # Use one of these (default = True):
    # *   if True: ProposeArgValuesRemoteOptimizedClientCommand
    # *   if False: ProposeArgValuesRemoteClientCommand
    optimize_completion_request = fields.Boolean(
        required = False,
        load_default = True,
    )

    connection_config = fields.Nested(connection_config_desc.dict_schema)

    # Enables spinner for FS_14_59_14_06: pending requests.
    show_pending_spinner = fields.Boolean(
        required = False,
        load_default = False,
    )

    spinless_sleep_sec = fields.Number(
        required = False,
        # Noticeable threshold is around 200 ms, but default to spin immediately:
        load_default = 0.0,
    )


client_config_desc = TypeDesc(
    dict_schema = ClientConfigSchema(),
    ref_name = ClientConfigSchema.__name__,
    dict_example = {
        connection_config_: connection_config_desc.dict_example,
    },
    default_file_path = "argrelay_client.json",
)
