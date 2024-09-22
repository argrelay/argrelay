from marshmallow import Schema, RAISE

from argrelay.misc_helper_common.TypeDesc import TypeDesc


# TODO: TODO_40_10_18_32: add custom base to all schemas:
class FuncTreeInterpFactoryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True


func_tree_interp_config_example = {
}

func_tree_interp_config_desc = TypeDesc(
    dict_schema = FuncTreeInterpFactoryConfigSchema(),
    ref_name = FuncTreeInterpFactoryConfigSchema.__name__,
    dict_example = func_tree_interp_config_example,
    default_file_path = "",
)
