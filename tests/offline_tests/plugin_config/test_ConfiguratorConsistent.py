from argrelay_lib_server_plugin_core.plugin_config.ConfiguratorConsistent import (
    ConfiguratorConsistent,
)
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass
from argrelay_test_infra.test_infra.EnvMockBuilder import (
    wrap_instance_method_on_instance,
)


class ThisTestClass(BaseTestClass):

    def test_reply_consistently(self):
        plugin_obj = ConfiguratorConsistent(None, "", {})
        mocked_git_commit_id = "this commit does not exist"
        with wrap_instance_method_on_instance(
            plugin_obj,
            plugin_obj._provide_project_git_commit_id,
        ) as method_wrap_mock:
            method_wrap_mock.return_value = mocked_git_commit_id
            plugin_obj.activate_plugin()
            self.assertEqual(method_wrap_mock.called, True)
        # Even when not mocked, function still return the same value:
        self.assertEqual(
            mocked_git_commit_id,
            plugin_obj.provide_project_git_commit_id(),
        )
