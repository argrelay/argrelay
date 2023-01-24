from __future__ import annotations

from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc

is_test_data_filter_enabled_ = "is_test_data_filter_enabled"
allow_only_test_data_ = "allow_only_test_data"


class ServiceLoaderConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    is_test_data_filter_enabled = fields.Boolean()

    # List of `test_data` ids which are allowed to load.
    # Those `data_envelopes` which do not have `test_data` id assigned are loaded regardless of any filter.
    allow_only_test_data = fields.List(
        fields.String(),
        required = True,
    )


service_loader_config_desc = TypeDesc(
    dict_schema = ServiceLoaderConfigSchema(),
    ref_name = ServiceLoaderConfigSchema.__name__,
    dict_example = {
        is_test_data_filter_enabled_: False,
        allow_only_test_data_: [
            "TD_70_69_38_46",  # no data
        ],
    },
    default_file_path = "",
)
