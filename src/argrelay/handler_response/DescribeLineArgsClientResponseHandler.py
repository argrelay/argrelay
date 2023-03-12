from __future__ import annotations

from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.schema_response.InterpResult import InterpResult
from argrelay.schema_response.InterpResultSchema import interp_result_desc


class DescribeLineArgsClientResponseHandler(AbstractClientResponseHandler):

    def __init__(
        self,
    ):
        super().__init__(
        )

    def handle_response(self, response_dict: dict):
        interp_result: InterpResult = interp_result_desc.dict_schema.load(response_dict)
        ElapsedTime.measure("after_object_creation")
        interp_result.describe_data()
