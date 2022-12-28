from unittest import TestCase

import yaml
from jsonschema.exceptions import ValidationError
from marshmallow import ValidationError

from argrelay.api_ext.relay_server.StaticDataSchema import static_data_desc
from relay_server.test_relay_server import load_relay_demo_server_config_dict
from test_argrelay import line_no


class ThisTestCase(TestCase):

    def test_from_yaml_str(self):
        """
        Test assumptions of schema validation.
        """

        test_cases = [
            (
                line_no(), "basic sample",
                """
                first_interp_factory_id: FirstArgInterpFactory
                types_to_values:

                    action:
                        -   goto
                        -   desc
                        -   list

                    access:
                        -   ro
                        -   rw
                """,
                {
                    "first_interp_factory_id": "FirstArgInterpFactory",
                    "types_to_values": {
                        "action": [
                            "goto",
                            "desc",
                            "list",
                        ],
                        "access": [
                            "ro",
                            "rw",
                        ],
                    }
                },
                None,
            ),
            (
                line_no(), "default test data: expanded (more realistic) sample",
                yaml.dump(load_relay_demo_server_config_dict()["static_data"]),
                {
                    "first_interp_factory_id": "FirstArgInterpFactory",
                },
                None,
            ),
            (
                line_no(), "without required field (`types_to_values`)",
                """
                first_interp_factory_id: FirstArgInterpFactory
                """,
                {
                    "first_interp_factory_id": "FirstArgInterpFactory",
                },
                ValidationError,
            ),
            (
                line_no(), "with extra key (`whatever_extra_key`) which is not allowed",
                """
                first_interp_factory_id: FirstArgInterpFactory
                types_to_values: {}
                whatever_extra_key: whatever_extra_val
                """,
                {
                    "first_interp_factory_id": "FirstArgInterpFactory",
                    "types_to_values": {
                    },
                },
                ValidationError,
            ),
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (line_number, case_comment, input_yaml_str, expected_object_part, expected_exception) = test_case
                if not expected_exception:
                    static_data = static_data_desc.from_yaml_str(input_yaml_str)

                    # Assert some fields unconditionally (regardless whether they exist in `expected_object_part`):
                    self.assertEqual(
                        expected_object_part["first_interp_factory_id"],
                        static_data.first_interp_factory_id,
                    )

                    # Assert other fields conditionally (only if they were specified in the `expected_object_part`):
                    if "types_to_values" in expected_object_part:
                        self.assertEqual(expected_object_part["types_to_values"], static_data.types_to_values)
                    else:
                        self.assertTrue(static_data.types_to_values)

                else:
                    with self.assertRaises(expected_exception):
                        static_data_desc.from_yaml_str(input_yaml_str)
