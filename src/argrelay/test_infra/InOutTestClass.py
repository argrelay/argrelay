from __future__ import annotations

from typing import Union, Type

from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.misc_helper_common import eprint
from argrelay.plugin_delegator.DelegatorAbstract import DelegatorAbstract
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.server_spec.CallContext import CallContext
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.EnvMockBuilder import EnvMockBuilder


class InOutTestClass(BaseTestClass):
    # TODO: TODO_32_99_70_35: Make generic validator be able to verify payload (not only `interp_ctx` passed from local client) - JSONPath?

    # TODO: Wrap input into Dataclass which in turn can be created via builder (to have ability pre-build defaults for a set of tests).
    def verify_response_data(
        self,
        call_ctx: CallContext,
        actual_suggestions: list[str],
        container_ipos_to_expected_assignments: Union[dict[int, dict[str, AssignedValue]], None],
        container_ipos_to_options_hidden_by_default_value: Union[dict[int, dict[str, list[str]]], None],
        delegator_class: Union[Type[DelegatorAbstract], None],
        envelope_ipos_to_prop_values: Union[dict[int, dict[str, str]], None],
        expected_suggestions: Union[list[str], None],
        envelope_containers: list[EnvelopeContainer],
        expected_container_ipos_to_used_token_bucket: Union[dict[int, Union[int, None]], None],
    ):
        try:

            if expected_suggestions is not None:
                self.assertEqual(expected_suggestions, actual_suggestions)

            if container_ipos_to_expected_assignments is not None:
                self.verify_envelope_containers(
                    envelope_containers,
                    container_ipos_to_expected_assignments,
                )

            if container_ipos_to_options_hidden_by_default_value is not None:
                self.verify_options_hidden_by_default_value(
                    envelope_containers,
                    container_ipos_to_options_hidden_by_default_value,
                )

            if (
                container_ipos_to_expected_assignments is not None
                and
                container_ipos_to_options_hidden_by_default_value is not None
            ):
                self.verify_expected_assignments_with_option_type_hidden_by_default(
                    container_ipos_to_expected_assignments,
                    container_ipos_to_options_hidden_by_default_value
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

            if envelope_ipos_to_prop_values is not None:
                self.verify_data_envelopes(
                    EnvMockBuilder.invocation_input.get_data_envelopes(),
                    envelope_ipos_to_prop_values,
                )

            if expected_container_ipos_to_used_token_bucket is not None:
                # TODO: TODO_32_99_70_35: candidate for generic library of JSONPath verifiers:
                for envelope_container_ipos, envelope_container in enumerate(envelope_containers):
                    expected_used_token_bucket = expected_container_ipos_to_used_token_bucket[envelope_container_ipos]
                    self.assertEqual(
                        expected_used_token_bucket,
                        envelope_container.used_token_bucket,
                    )

        except:

            # Check if there are some obvious test input mistakes:

            if call_ctx.server_action is ServerAction.ProposeArgValues:
                self.assertIsNone(delegator_class)
                self.assertIsNone(envelope_ipos_to_prop_values)
            elif call_ctx.server_action is ServerAction.DescribeLineArgs:
                # TODO: TODO_42_81_01_90: assert data instead of print out: there will be no delegator_class, but a mock to intercept response for enum query:
                self.assertIsNone(delegator_class)
                # TODO: TODO_42_81_01_90: assert data instead of print out: the data should be available:
                self.assertIsNone(envelope_ipos_to_prop_values)
            elif call_ctx.server_action is ServerAction.RelayLineArgs:
                pass
            else:
                raise RuntimeError

            # Rethrow previous error:
            raise

    def verify_envelope_containers(
        self,
        envelope_containers,
        container_ipos_to_expected_assignments: Union[dict[int, dict[str, AssignedValue]], None],
    ):
        for container_ipos, expected_assignments in container_ipos_to_expected_assignments.items():
            try:
                if expected_assignments is None:
                    self.assertFalse(0 <= container_ipos < len(envelope_containers))
                else:
                    self.assertTrue(0 <= container_ipos < len(envelope_containers))
                    for prop_name, assigned_value in expected_assignments.items():
                        try:
                            if assigned_value is None:
                                self.assertTrue(
                                    prop_name not in
                                    envelope_containers
                                    [container_ipos].assigned_prop_name_to_prop_value
                                )
                            elif isinstance(assigned_value, list):
                                # A bit of hack: if `list`, then check if it matches `remaining_prop_name_to_prop_value`:
                                self.assertEqual(
                                    assigned_value,
                                    envelope_containers
                                    [container_ipos].remaining_prop_name_to_prop_value
                                    [prop_name]
                                )
                            else:
                                self.assertEqual(
                                    assigned_value,
                                    envelope_containers
                                    [container_ipos].assigned_prop_name_to_prop_value
                                    [prop_name],
                                )
                        except:
                            eprint(
                                f"container_ipos:{container_ipos} prop_name:{prop_name} assigned_value:{assigned_value}",
                            )
                            raise
            except:
                print(f"envelope_containers:\n{envelope_containers}")
                raise

    def verify_options_hidden_by_default_value(
        self,
        envelope_containers: list[EnvelopeContainer],
        container_ipos_to_options_hidden_by_default_value: Union[dict[int, dict[str, list[str]]], None],
    ):
        """
        Make sure that specified expected `options_hidden_by_default_value` list
        (per `envelope_container` ipos, per `prop_name`) match what is populated into
        `EnvelopeContainer.filled_prop_values_hidden_by_defaults`.
        """
        for container_ipos, options_hidden_by_default_value_per_prop_name in container_ipos_to_options_hidden_by_default_value.items():
            try:
                if options_hidden_by_default_value_per_prop_name is None:
                    self.assertFalse(0 <= container_ipos < len(envelope_containers))
                else:
                    self.assertTrue(0 <= container_ipos < len(envelope_containers))
                    for prop_name, options_hidden_by_default_value in options_hidden_by_default_value_per_prop_name.items():
                        try:
                            if options_hidden_by_default_value is None:
                                self.assertTrue(
                                    prop_name not in
                                    envelope_containers
                                    [container_ipos].filled_prop_values_hidden_by_defaults
                                )
                            else:
                                self.assertEqual(
                                    options_hidden_by_default_value,
                                    envelope_containers
                                    [container_ipos].filled_prop_values_hidden_by_defaults
                                    [prop_name],
                                )
                        except:
                            eprint(
                                f"container_ipos:{container_ipos} prop_name:{prop_name} options_hidden_by_default_value:{options_hidden_by_default_value}",
                            )
                            raise
            except:
                print(f"envelope_containers:\n{envelope_containers}")
                raise

    def verify_expected_assignments_with_option_type_hidden_by_default(
        self,
        container_ipos_to_expected_assignments: dict[int, dict[str, AssignedValue]],
        container_ipos_to_options_hidden_by_default_value: dict[int, dict[str, list[str]]],
    ):
        """
        Make sure that, for given `container_ipos`, if there are both:
        *   options hidden by default
        *   assigned value
        then, the assigned value has `ValueSource.default_value`.
        """
        for container_ipos, expected_assignments in container_ipos_to_expected_assignments.items():
            try:
                if expected_assignments is not None:
                    if container_ipos in container_ipos_to_options_hidden_by_default_value:
                        for prop_name, assigned_value in expected_assignments.items():
                            options_hidden_by_default_value_per_prop_name = (
                                container_ipos_to_options_hidden_by_default_value[
                                    container_ipos
                                ]
                            )
                            if prop_name in options_hidden_by_default_value_per_prop_name:
                                if options_hidden_by_default_value_per_prop_name[prop_name] is None:
                                    self.assertNotEqual(
                                        assigned_value.value_source,
                                        ValueSource.default_value,
                                    )
                                else:
                                    self.assertEqual(
                                        assigned_value.value_source,
                                        ValueSource.default_value,
                                    )
            except:
                print(
                    f"container_ipos_to_expected_assignments:\n{container_ipos_to_expected_assignments}"
                )
                print(
                    f"container_ipos_to_options_hidden_by_default_value:\n{container_ipos_to_options_hidden_by_default_value}"
                )
                raise

    def verify_data_envelopes(
        self,
        data_envelopes,
        envelope_ipos_to_prop_values,
    ):
        for envelope_ipos, prop_values in envelope_ipos_to_prop_values.items():
            try:
                if prop_values is None:
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
                    for prop_name, prop_value in prop_values.items():
                        try:
                            if prop_value is None:
                                self.assertTrue(
                                    prop_name not in
                                    data_envelopes[envelope_ipos]
                                )
                            else:
                                self.assertEqual(
                                    prop_value,
                                    data_envelopes[envelope_ipos][prop_name],
                                )
                        except:
                            eprint(
                                f"envelope_ipos:{envelope_ipos} prop_name:{prop_name} prop_value:{prop_value}",
                            )
                            raise

            except:
                print(f"data_envelopes:\n{data_envelopes}")
                raise
