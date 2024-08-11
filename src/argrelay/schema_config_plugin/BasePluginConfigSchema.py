from __future__ import annotations

from marshmallow import RAISE

from argrelay.misc_helper_common.ObjectSchema import ObjectSchema


class BasePluginConfigSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True


def serialize_dag_to_list(
    entire_dag: dict[str, list[str]],
) -> list[str]:
    output_list: list[str] = list_sub_dag(
        [],
        entire_dag,
        [node_id for node_id in entire_dag],
    )
    return output_list


def list_sub_dag(
    curr_path: list[str],
    entire_dag: dict[str, list[str]],
    id_sub_list: list[str],
) -> list[str]:
    output_list: list[str] = []

    for node_id in id_sub_list:
        if node_id in curr_path:
            raise ValueError(f"cyclic ref to plugin id in path `{curr_path}` -> `{node_id}`")
        if node_id not in entire_dag:
            raise ValueError(f"plugin id in path `{curr_path}` -> `{node_id}` is not defined")
        if node_id in entire_dag:
            # plugin has dependencies:
            sub_list = list_sub_dag(
                curr_path + [node_id],
                entire_dag,
                entire_dag[node_id],
            )
            for sub_node_id in sub_list:
                if sub_node_id not in output_list:
                    output_list.append(sub_node_id)
        else:
            raise ValueError(f"plugin id in path `{curr_path}` -> `{node_id}` is not included for activation")

        if node_id not in output_list:
            output_list.append(node_id)

    return output_list
