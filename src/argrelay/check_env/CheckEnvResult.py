from typing import Union

from argrelay.enum_desc.ResultCategory import ResultCategory


class CheckEnvResult:
    """
    Result data from plugin Implements FS_36_17_84_44 `check_env`.
    """

    def __init__(
        self,
        result_category: ResultCategory,
        result_key: Union[str, None],
        result_value: Union[str, None],
        result_message: Union[str, None],
    ):
        self.result_category: ResultCategory = result_category
        self.result_key: Union[str, None] = result_key
        self.result_value: Union[str, None] = result_value
        self.result_message: Union[str, None] = result_message
