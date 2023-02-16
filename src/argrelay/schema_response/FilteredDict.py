from marshmallow import fields


class FilteredDict(fields.Dict):
    """
    Dict field which does not serialize specific fields:
    https://github.com/marshmallow-code/marshmallow/issues/494#issuecomment-390495145
    """

    def __init__(self, filtered_keys, **kwargs):
        super(FilteredDict, self).__init__(**kwargs)
        self.filtered_keys = filtered_keys

    def _serialize(self, value, attr, obj, **kwargs):
        value = super(FilteredDict, self)._serialize(value, attr, obj)
        if value:
            return {key: value[key] for key in value if key not in self.filtered_keys}
        else:
            return value

    def _deserialize(self, value, attr, data, **kwargs):
        value = super(FilteredDict, self)._deserialize(value, attr, data)
        return {key: value[key] for key in value if key not in self.filtered_keys}
