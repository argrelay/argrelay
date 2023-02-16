from unittest import TestCase

from jsonschema.exceptions import ValidationError
from marshmallow import ValidationError

from argrelay.schema_config_core_server.ServerConfigSchema import static_data_
from argrelay.schema_config_core_server.StaticDataSchema import (
    static_data_desc,
    first_interp_factory_id_,
    known_arg_types_,
    data_envelopes_,
)
from argrelay.test_helper import line_no
from argrelay.test_helper.EnvMockBuilder import load_custom_integ_server_config_dict


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
                    known_arg_types_: [
                        "action",
                        "access",
                    ],
                    data_envelopes_: [
                    ],
                },
                {
                    first_interp_factory_id_: "FirstArgInterpFactory",
                    known_arg_types_: [
                        "action",
                        "access",
                    ],
                    data_envelopes_: [
                    ],
                },
                None,
            ),
            (
                line_no(), "default test data: expanded (realistic) sample",
                load_custom_integ_server_config_dict()[static_data_],
                {
                    first_interp_factory_id_: "FirstArgInterpFactory",
                },
                None,
            ),
            (
                line_no(), "without required field (`data_envelope`-s)",
                {
                    first_interp_factory_id_: "FirstArgInterpFactory",
                    known_arg_types_: [
                    ],
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
                    known_arg_types_: [
                    ],
                    data_envelopes_: [
                    ],
                    "whatever_extra_key": "whatever_extra_val",
                },
                {
                    first_interp_factory_id_: "FirstArgInterpFactory",
                    known_arg_types_: [
                    ],
                    data_envelopes_: [
                    ],
                },
                ValidationError,
            ),
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (line_number, case_comment, input_dict, expected_dict_part, expected_exception) = test_case
                if not expected_exception:
                    static_data = static_data_desc.from_input_dict(input_dict)

                    # Assert those files which were specified in the `expected_dict_part`:
                    for key_to_verify in expected_dict_part.keys():
                        self.assertEqual(expected_dict_part[key_to_verify], getattr(static_data, key_to_verify))

                else:
                    with self.assertRaises(expected_exception):
                        static_data_desc.from_input_dict(input_dict)
