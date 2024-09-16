from gui_tests.CypressTestClass import CypressTestClass


class ThisTestClass(CypressTestClass):
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
