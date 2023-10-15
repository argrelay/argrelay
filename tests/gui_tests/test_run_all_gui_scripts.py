from gui_tests.CypressTestCase import CypressTestCase


class ThisTestCase(CypressTestCase):
    # same_test_data_per_class = "TD_38_03_48_51"  # large generated data set
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_run_all_scripts(self):
        self.run_cypress_test_scripts_in_paths(
            "cypress/e2e/argrelay_gui/**/*.cy.js",
        )

    def test_basic_checks(self):
        self.run_cypress_test_script(
            "basic_checks.cy.js",
        )

    def test_command_history(self):
        self.run_cypress_test_script(
            "command_history.cy.js",
        )
