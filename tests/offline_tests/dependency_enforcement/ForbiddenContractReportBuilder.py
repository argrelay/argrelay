from __future__ import annotations

from dataclasses import dataclass, field

from importlinter import Contract
from importlinter.application.ports.reporting import Report
from importlinter.application.use_cases import create_report
from importlinter.application.user_options import UserOptions
from importlinter.contracts.forbidden import ForbiddenContract

import argrelay
import argrelay_api_server_cli
from argrelay.test_infra import file_line_l_1

session_options = {
    "root_packages": [
        argrelay.__name__,
        argrelay_api_server_cli.__name__,
    ],
    "include_external_packages": True,
    "exclude_type_checking_imports": True,
}

contract_type_ = "type"
contract_title_ = "name"
source_module_specs_ = "source_modules"
forbidden_module_specs_ = "forbidden_modules"

@dataclass
class ForbiddenContractReportBuilder:

    _contract_class: Contract = ForbiddenContract

    _contract_type: str = "forbidden"

    _contract_title: str | None = None

    _source_module_specs: list[str] = field(default_factory = lambda: [])

    _forbidden_module_specs: list[str] = field(default_factory = lambda: [])

    def set_title(
        self,
        given_contract_title: str,
    ) -> ForbiddenContractReportBuilder:
        self._contract_title = given_contract_title
        return self

    def set_source_module_specs(
        self,
        given_source_module_spec: list[str],
    ):
        self._source_module_specs = given_source_module_spec
        return self

    def add_forbidden_module_spec(
        self,
        given_forbidden_module_spec: str,
    ):
        self._forbidden_module_specs = given_forbidden_module_spec
        return self

    def build(
        self,
    ) -> Report:
        self._contract_title = self._contract_title or file_line_l_1()
        return create_report(
            user_options = UserOptions(
                session_options = session_options,
                contracts_options = [{
                    contract_title_: self._contract_title,
                    contract_type_: self._contract_type,
                    source_module_specs_: self._source_module_specs,
                    forbidden_module_specs_: self._forbidden_module_specs,
                }],
            ),
        )
