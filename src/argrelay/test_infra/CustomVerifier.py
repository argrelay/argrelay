from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.schema_request.CallContextSchema import server_action_
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.JsonTestOutputVerifier import JsonTestOutputVerifier


class CustomVerifier(JsonTestOutputVerifier):

    def __init__(
        self,
        test_instance: BaseTestClass,
    ):
        super().__init__(
        )

        self.test_instance: BaseTestClass = test_instance


class CallContextVerifier(CustomVerifier):

    def __init__(
        self,
        test_instance: BaseTestClass,
        server_action: ServerAction,
    ):
        super().__init__(
            test_instance,
        )

        self.server_action: ServerAction = server_action

        self.add_verifier(
            f"$.{server_action_}",
            lambda m: test_instance.assertEqual(1, len(m)),
            lambda m: test_instance.assertEqual(server_action.name, m[0].value),
        )


class ServerActionVerifier(CallContextVerifier):

    def __init__(
        self,
        test_instance: BaseTestClass,
        server_action: ServerAction,
    ):
        super().__init__(
            test_instance,
            server_action,
        )

        self.test_instance = test_instance,
        self.server_action = server_action,


class ProposeArgValuesVerifier(ServerActionVerifier):

    def __init__(
        self,
        test_instance: BaseTestClass,
    ):
        super().__init__(
            test_instance,
            ServerAction.ProposeArgValues,
        )


class DescribeLineArgsVerifier(ServerActionVerifier):

    def __init__(
        self,
        test_instance: BaseTestClass,
    ):
        super().__init__(
            test_instance,
            ServerAction.DescribeLineArgs,
        )


class RelayLineArgsVerifier(ServerActionVerifier):

    def __init__(
        self,
        test_instance: BaseTestClass,
    ):
        super().__init__(
            test_instance,
            ServerAction.RelayLineArgs,
        )
