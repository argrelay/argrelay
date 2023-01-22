from dataclasses import dataclass

import yaml
from marshmallow import Schema, ValidationError


@dataclass(frozen = True)
class TypeDesc:
    """
    Type descriptor: schema, example, etc.
    """

    dict_schema: Schema
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
        return self.dict_schema.load(input_dict)

    def validate_dict(self, input_dict: dict):
        validation_errors = self.dict_schema.validate(input_dict)
        if validation_errors:
            raise ValidationError(validation_errors)
