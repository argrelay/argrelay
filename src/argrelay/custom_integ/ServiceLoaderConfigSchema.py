from __future__ import annotations

from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc

test_data_ids_to_load_ = "test_data_ids_to_load"


class ServiceLoaderConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    # List of `test_data` ids which are allowed to load.
    # Those `data_envelopes` which do not have `test_data` id assigned are loaded regardless of any filter.
    test_data_ids_to_load = fields.List(
        fields.String(),
        required = True,
    )


service_loader_config_desc = TypeDesc(
    dict_schema = ServiceLoaderConfigSchema(),
    ref_name = ServiceLoaderConfigSchema.__name__,
    dict_example = {
        test_data_ids_to_load_: [
            "TD_70_69_38_46",  # no data
        ],
    },
    default_file_path = "",
)
