from marshmallow import Schema, RAISE, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc


class ObjectSchema(Schema):
    """
    Base schema for many other schemas which create object via @post_load.
    """

    class Meta:
        unknown = RAISE
        strict = True

    model_class = dict

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        """
        Implements inheritance as described here:
        https://stackoverflow.com/a/65668854/441652
        """
        return type(self).model_class(**input_dict)


object_desc = TypeDesc(
    dict_schema = ObjectSchema(),
    ref_name = ObjectSchema.__name__,
    dict_example = {},
    default_file_path = "",
)
