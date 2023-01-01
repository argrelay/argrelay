from dataclasses import dataclass

import yaml
from marshmallow import Schema


@dataclass(frozen = True)
class TypeDesc:
    """
    Type descriptor: schema, example, etc.
    """

    object_schema: Schema
    ref_name: str
    dict_example: dict
    default_file_path: str

    def from_default_file(self):
        return self.from_yaml_file(self.default_file_path)

    def from_yaml_file(self, file_path: str):
        return self.from_input_dict(yaml.safe_load(open(file_path)))

    def from_yaml_str(self, yaml_str: str):
        return self.from_input_dict(yaml.safe_load(yaml_str))

    def from_input_dict(self, input_dict: dict):
        return self.object_schema.load(input_dict)
