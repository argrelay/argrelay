import os
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

import yaml
from marshmallow import Schema, ValidationError
from yaml import SafeLoader

from argrelay.misc_helper_common import get_config_path, get_argrelay_dir


def schemaless_dict_from_yaml_file(
    file_path: str,
) -> dict:
    """
    Avoid using this method (directly) as it loads YAML data without `Schema`.

    See `TypeDesc.dict_from_yaml_file` instead.
    """
    with open(file_path) as yaml_file:
        return yaml.safe_load(yaml_file)


def construct_include(
    yaml_loader: SafeLoader,
    yaml_node: yaml.Node,
) -> Any:
    """
    Method which allows `!include`-ing files in YAML.

    See:
    https://stackoverflow.com/a/9577670/441652
    """

    file_name = os.path.abspath(os.path.join(
        # All paths should be relative to `@/` = `argrelay_dir`:
        get_argrelay_dir(),
        yaml_loader.construct_scalar(yaml_node),
    ))

    with open(file_name, "r") as file_stream:
        return yaml.load(file_stream, SafeLoader)


yaml.add_constructor("!include", construct_include, SafeLoader)


@dataclass(frozen = True)
class TypeDesc:
    """
    Type descriptor: schema, example, etc.
    """

    dict_schema: Schema = field()
    ref_name: str = field()
    dict_example: dict = field()
    default_file_path: str = field()

    def get_adjusted_file_path(
        self,
    ) -> str:
        return get_config_path(self.default_file_path)

    def obj_from_default_file(
        self,
    ) -> object:
        return self.obj_from_yaml_file(self.get_adjusted_file_path())

    def dict_from_default_file(
        self,
    ) -> dict:
        return self.dict_from_yaml_file(self.get_adjusted_file_path())

    def obj_from_yaml_file(
        self,
        file_path: str,
    ) -> object:
        return self.obj_from_input_dict(schemaless_dict_from_yaml_file(file_path))

    def dict_from_yaml_file(
        self,
        file_path: str,
    ) -> dict:
        return self.dict_from_input_dict(schemaless_dict_from_yaml_file(file_path))

    def obj_from_yaml_str(
        self,
        yaml_str: str,
    ) -> object:
        return self.obj_from_input_dict(yaml.safe_load(yaml_str))

    def dict_from_yaml_str(
        self,
        yaml_str: str,
    ) -> object:
        return self.dict_from_input_dict(yaml.safe_load(yaml_str))

    def obj_from_input_dict(
        self,
        input_dict: dict,
    ) -> object:
        # Make a `deepcopy` as `marshmallow` reuses instances specified in `load_default`:
        return deepcopy(self.dict_schema.load(input_dict))

    def dict_from_input_dict(
        self,
        input_dict: dict,
    ) -> dict:
        """
        This `dict` to `dict` method is used to make `Schema` populate defaults:
        """
        return self.dict_from_input_obj(
            # Load `obj` first to populate all defaults based on schema definition:
            self.obj_from_input_dict(input_dict)
        )

    def dict_from_input_obj(
        self,
        input_obj: object,
    ) -> dict:
        # Make a `deepcopy` just in case (if `marshmallow` reuses some of the instances):
        return deepcopy(self.dict_schema.dump(input_obj))

    def validate_dict(
        self,
        input_dict: dict,
    ) -> None:
        validation_errors = self.dict_schema.validate(input_dict)
        if validation_errors:
            raise ValidationError(validation_errors)
