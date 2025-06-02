from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoscript.boot_env import EnvContext


# noinspection PyPep8Naming
class ThisTestClass_ensure_allowed_conf_symlink_target(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          unit tests for `ensure_allowed_conf_symlink_target`
    """

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    def test_success_on_valid_relative_dir(self):
        # given:
        self.fs.create_dir("valid_dir")
        self.env_ctx.target_dst_dir_path = "valid_dir"

        # when:
        self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        # no exception happens

    def test_failure_on_absolute_path(self):
        # given:
        self.env_ctx.target_dst_dir_path = "/abs/path"

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        self.assertIn("must not be absolute", str(ctx.exception))

    def test_failure_on_path_with_dot_dot(self):
        # given:
        self.env_ctx.target_dst_dir_path = "conf/../bad"

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        self.assertIn("must not contain `..`", str(ctx.exception))

    def test_failure_on_non_directory_path(self):
        # given:
        self.fs.create_file("not_a_dir")
        self.env_ctx.target_dst_dir_path = "not_a_dir"

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        self.assertIn("must lead to a directory", str(ctx.exception))

    def test_failure_on_non_existent_path(self):
        # given:
        self.env_ctx.target_dst_dir_path = "missing_dir"

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        self.assertIn("must lead to a directory", str(ctx.exception))

    def test_success_on_symlink_leading_to_a_dir(self):
        # given:
        self.fs.create_dir("valid_dir")
        self.fs.create_symlink("symlink_to_dir", "valid_dir")
        self.env_ctx.target_dst_dir_path = "symlink_to_dir"

        # when:
        self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        # no exception happens
