from __future__ import annotations

from typing import Union, Type

from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.misc_helper_common import eprint
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.server_spec.CallContext import CallContext
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.EnvMockBuilder import EnvMockBuilder


class InOutTestClass(BaseTestClass):
    # TODO_32_99_70_35: Make generic validator be able to verify payload (not only `interp_ctx` passed from local client) - JSONPath?

    # TODO: Wrap input into Dataclass which in turn can be created via builder (to have ability pre-build defaults for a set of tests).
    def verify_response_data(
        self,
        call_ctx: CallContext,
        actual_suggestions: list[str],
        container_ipos_to_expected_assignments: Union[dict[int, dict[str, str]], None],
        delegator_class: Union[Type[AbstractDelegator], None],
        envelope_ipos_to_field_values: Union[dict[int, dict[str, str]], None],
        expected_suggestions: Union[list[str], None],
        envelope_containers: list[EnvelopeContainer],
    ):
        try:

            if expected_suggestions is not None:
                # If `expected_suggestions`, verify them:
                self.assertEqual(expected_suggestions, actual_suggestions)

            if container_ipos_to_expected_assignments is not None:
                self.verify_envelope_containers(
                    envelope_containers,
                    container_ipos_to_expected_assignments,
                )

            if delegator_class is not None:
                self.assertEqual(
                    EnvMockBuilder.invocation_input.delegator_plugin_entry.plugin_module_name,
                    delegator_class.__module__,
                )
                self.assertEqual(
                    EnvMockBuilder.invocation_input.delegator_plugin_entry.plugin_class_name,
                    delegator_class.__name__,
                )

            if envelope_ipos_to_field_values is not None:
                self.verify_data_envelopes(
                    EnvMockBuilder.invocation_input.get_data_envelopes(),
                    envelope_ipos_to_field_values,
                )

        except:

            # Check if there are some obvious test input mistakes:

            if call_ctx.server_action is ServerAction.ProposeArgValues:
                self.assertIsNone(delegator_class)
                self.assertIsNone(envelope_ipos_to_field_values)
            elif call_ctx.server_action is ServerAction.DescribeLineArgs:
                # TODO: TODO_11_77_28_50 suggestions are already in all responses:
                self.assertIsNone(expected_suggestions)
                # TODO: TODO_42_81_01_90: assert data instead of print out: there will be no delegator_class, but a mock to intercept response for enum query:
                self.assertIsNone(delegator_class)
                # TODO: TODO_42_81_01_90: assert data instead of print out: the data should be available:
                self.assertIsNone(envelope_ipos_to_field_values)
            elif call_ctx.server_action is ServerAction.RelayLineArgs:
                # TODO: TODO_11_77_28_50 suggestions are already in all responses:
                self.assertIsNone(expected_suggestions)
            else:
                raise RuntimeError

            # Rethrow previous error:
            raise

    def verify_envelope_containers(
        self,
        envelope_containers,
        container_ipos_to_expected_assignments,
    ):
        for container_ipos, expected_assignments in container_ipos_to_expected_assignments.items():
            try:
                if expected_assignments is None:
                    self.assertFalse(0 <= container_ipos < len(envelope_containers))
                else:
                    self.assertTrue(0 <= container_ipos < len(envelope_containers))
                    for arg_type, arg_value in expected_assignments.items():
                        try:
                            if arg_value is None:
                                self.assertTrue(
                                    arg_type not in
                                    envelope_containers
                                    [container_ipos].assigned_types_to_values
                                )
                            else:
                                self.assertEqual(
                                    arg_value,
                                    envelope_containers
                                    [container_ipos].assigned_types_to_values
                                    [arg_type],
                                )
                        except:
                            eprint(
                                f"container_ipos:{container_ipos} arg_type:{arg_type} arg_value:{arg_value}",
                            )
                            raise
            except:
                print(f"envelope_containers:\n{envelope_containers}")
                raise

    def verify_data_envelopes(
        self,
        data_envelopes,
        envelope_ipos_to_field_values,
    ):
        for envelope_ipos, field_values in envelope_ipos_to_field_values.items():
            try:
                if field_values is None:
                    self.assertFalse(
                        (0 <= envelope_ipos < len(data_envelopes))
                        and
                        # TODO: Maybe, for clarity, avoid adding such None data envelope?
                        # Containers with non-found `data_envelope`-s still contribute an entry to this list:
                        (data_envelopes[envelope_ipos] is not None)
                    )
                else:
                    self.assertTrue(
                        (0 <= envelope_ipos < len(data_envelopes))
                    )
                    for field_name, field_value in field_values.items():
                        try:
                            if field_value is None:
                                self.assertTrue(
                                    field_name not in
                                    data_envelopes[envelope_ipos]
                                )
                            else:
                                self.assertEqual(
                                    field_value,
                                    data_envelopes[envelope_ipos][field_name],
                                )
                        except:
                            eprint(
                                f"envelope_ipos:{envelope_ipos} field_name:{field_name} field_value:{field_value}",
                            )
                            raise

            except:
                print(f"data_envelopes:\n{data_envelopes}")
                raise
