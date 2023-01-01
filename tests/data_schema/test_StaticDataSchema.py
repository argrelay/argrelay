from unittest import TestCase

from jsonschema.exceptions import ValidationError
from marshmallow import ValidationError

from argrelay.data_schema.ServerConfigSchema import static_data_
from argrelay.data_schema.StaticDataSchema import static_data_desc, types_to_values_, first_interp_factory_id_
from misc_helper import line_no
from relay_demo.test_relay_demo import load_relay_demo_server_config_dict


class ThisTestCase(TestCase):

    def test_from_yaml_str(self):
        """
        Test assumptions of schema validation.
        """

        test_cases = [
            (
                line_no(), "basic sample",
                {
                    first_interp_factory_id_: "FirstArgInterpFactory",
                    types_to_values_: {
                        "action": [
                            "goto",
                            "desc",
                            "list",
                        ],
                        "access": [
                            "ro",
                            "rw",
                        ],
                    },
                    "data_objects": [
                    ],
                },
                {
                    first_interp_factory_id_: "FirstArgInterpFactory",
                    types_to_values_: {
                        "action": [
                            "goto",
                            "desc",
                            "list",
                        ],
                        "access": [
                            "ro",
                            "rw",
                        ],
                    },
                    "data_objects": [
                    ],
                },
                None,
            ),
            (
                line_no(), "default test data: expanded (realistic) sample",
                load_relay_demo_server_config_dict()[static_data_],
                {
                    first_interp_factory_id_: "FirstArgInterpFactory",
                },
                None,
            ),
            (
                line_no(), "without required field (`data_objects`)",
                {
                    first_interp_factory_id_: "FirstArgInterpFactory",
                    types_to_values_: {
                    },
                },
                {
                    first_interp_factory_id_: "FirstArgInterpFactory",
                },
                ValidationError,
            ),
            (
                line_no(), "with extra key (`whatever_extra_key`) which is not allowed",
                {
                    first_interp_factory_id_: "FirstArgInterpFactory",
                    "types_to_values": {
                    },
                    "data_objects": [
                    ],
                    "whatever_extra_key": "whatever_extra_val",
                },
                {
                    first_interp_factory_id_: "FirstArgInterpFactory",
                    types_to_values_: {
                    },
                    "data_objects": [
                    ],
                },
                ValidationError,
            ),
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (line_number, case_comment, input_dict, expected_object_part, expected_exception) = test_case
                if not expected_exception:
                    static_data = static_data_desc.from_input_dict(input_dict)

                    # Assert those files which were specified in the `expected_object_part`:
                    for key_to_verify in expected_object_part.keys():
                        self.assertEqual(expected_object_part[key_to_verify], getattr(static_data, key_to_verify))

                else:
                    with self.assertRaises(expected_exception):
                        static_data_desc.from_input_dict(input_dict)
