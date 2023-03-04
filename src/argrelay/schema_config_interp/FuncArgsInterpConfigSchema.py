from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_config_interp.InitControlSchema import init_control_desc
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc

function_search_control_ = "function_search_control"

function_init_control_ = "function_init_control"


class FuncArgsInterpConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    function_search_control = fields.Nested(
        search_control_desc.dict_schema,
        required = True,
    )

    function_init_control = fields.Nested(
        init_control_desc.dict_schema,
        required = True,
    )


func_args_interp_config_example = {
    function_search_control_: search_control_desc.dict_example,
    function_init_control_: init_control_desc.dict_example,
}

func_args_interp_config_desc = TypeDesc(
    dict_schema = FuncArgsInterpConfigSchema(),
    ref_name = FuncArgsInterpConfigSchema.__name__,
    dict_example = func_args_interp_config_example,
    default_file_path = "",
)
