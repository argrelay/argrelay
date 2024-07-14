from typing import Union

from argrelay.handler_response.ClientResponseHandlerAbstract import ClientResponseHandlerAbstract
from argrelay.schema_response.InvocationInput import InvocationInput
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc


class ClientResponseHandlerCheckEnv(ClientResponseHandlerAbstract):
    """
    Implements FS_36_17_84_44 `check_env`.

    Unlike `ClientResponseHandlerRelayLineArgs` for regular command execution,
    this class only returns payload of the response
    (without executing client-side part of its delegator plugin).
    This is to avoid the alternative when, in order to get response data,
    stdout has to be captured from regular command execution in a sub-process.
    """

    def __init__(
        self,
    ):
        super().__init__(
        )
        self.invocation_input: Union[InvocationInput, None] = None

    def handle_response(
        self,
        response_dict: dict,
    ):
        self.invocation_input = invocation_input_desc.dict_schema.load(response_dict)
