from __future__ import annotations

from argrelay.schema_config_core_server.ServerConfigSchema import serialize_dag_to_list
from argrelay.test_infra import line_no
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):

    def test_plugin_DAG_serialization(self):
        """
        Test serialization of plugin id DAG.
        """

        test_cases = [
            (
                line_no(),
                {},
                None,
                [],
                "all empty",
            ),
            (
                line_no(),
                {
                    "id_1": [
                        "id_2",
                    ],
                },
                f"plugin id in path `['id_1']` -> `id_2` is not defined",
                None,
                "Using unknown id: id_1",
            ),
            (
                line_no(),
                {
                    "id_1": [
                        "id_2",
                    ],
                },
                f"plugin id in path `['id_1']` -> `id_2` is not defined",
                None,
                "Using unknown id: id_2",
            ),
            (
                line_no(),
                {
                    "id_1": [
                        "id_2",
                    ],
                    "id_2": [
                        "id_1",
                    ]
                },
                "cyclic ref to plugin id in path `['id_1', 'id_2']` -> `id_1`",
                None,
                "cyclic dependency.",
            ),
            (
                line_no(),
                {
                    "id_5": [
                        "id_6",
                    ],
                    "id_4": [
                        "id_5",
                    ],
                    "id_3": [
                        "id_4",
                    ],
                    "id_2": [
                        "id_3",
                    ],
                    "id_1": [
                        "id_2",
                    ],
                    "id_6": [
                    ],
                },
                None,
                [
                    "id_6",
                    "id_5",
                    "id_4",
                    "id_3",
                    "id_2",
                    "id_1",
                ],
                "Ids should be re-ordered according to DAG.",
            ),
            (
                line_no(),
                {
                    "id_1": [
                        "id_2",
                    ],
                    "id_2": [
                    ],
                },
                None,
                [
                    "id_2",
                    "id_1",
                ],
                "Unused plugin ids (id_3) should not appear in the output list.",
            ),
            (
                line_no(),
                {
                    "id_5": [
                    ],
                    "id_4": [
                        "id_5",
                        "id_3",
                    ],
                    "id_1": [
                        "id_2",
                    ],
                    "id_3": [
                    ],
                    "id_2": [
                        "id_3",
                        "id_4",
                    ]
                },
                None,
                [
                    "id_5",
                    "id_3",
                    "id_4",
                    "id_2",
                    "id_1",
                ],
                "It should be okay if dependency is used multiple times: "
                "id_1 -> id_2 -> id_3 "
                "id_1 -> id_2 -> id_4 -> id_3 "
                "Output list should contain id_3 before id_4.",
            ),
            (
                line_no(),
                {
                    "id_5": [
                    ],
                    "id_4": [
                        "id_5",
                        "id_3",
                    ],
                    "id_1": [
                        "id_2",
                    ],
                    "id_3": [
                    ],
                },
                "plugin id in path `['id_1']` -> `id_2` is not defined",
                None,
                "Undefined plugin (id_2) cannot be used as dependency.",
            ),
            (
                line_no(),
                {
                    "id_2": [
                    ],
                    "id_1": [
                        "id_2",
                    ],
                    "id_3": [
                    ],
                },
                None,
                [
                    "id_2",
                    "id_1",
                    "id_3",
                ],
                "It is fine to list plugin ids with no dependencies (`id_3`).",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    input_plugin_dag,
                    expected_exception,
                    expected_plugin_id_list,
                    case_comment,
                ) = test_case

                if expected_exception is None:

                    actual_plugin_id_list = serialize_dag_to_list(
                        input_plugin_dag,
                    )
                    self.assertEqual(
                        expected_plugin_id_list,
                        actual_plugin_id_list,
                    )
                else:
                    self.assertIsNone(
                        expected_plugin_id_list,
                        "remove expected result to avoid confusion"
                    )
                    with self.assertRaises(Exception) as exc_context:
                        serialize_dag_to_list(
                            input_plugin_dag,
                        )
                    self.assertEqual(
                        expected_exception,
                        exc_context.exception.args[0],
                    )
