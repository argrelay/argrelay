import re
from io import StringIO
from unittest import TestCase

import pandas as pd

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_config_core_server.StaticDataSchema import data_envelopes_
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_class_
from argrelay.test_helper import change_to_known_repo_path, test_data_
from argrelay.test_helper.EnvMockBuilder import EnvMockBuilder


class ThisTestCase(TestCase):
    """
    Verify TD_63_37_05_36 # default
    """

    def test_match_data_with_docs(self):
        """
        Matches data with its description in the table - see:
        TD_63_37_05_36.default_service_data.md

        This data is relatively large - this test ensures it maintains required properties.

        Note: consider generating table view for review instead of consuming one created manually.
        """

        with change_to_known_repo_path():
            # Filter out only table lines from Markdown file:
            table_regex = re.compile("^\|")
            test_data = ""
            with open("../docs/test_data/TD_63_37_05_36.default_service_data.md") as md_file:
                for file_line in md_file:
                    if table_regex.match(file_line):
                        test_data += file_line
        print(test_data)

        # Configure to print all:
        pd.set_option("display.max_rows", 500)
        pd.set_option("display.max_columns", 500)
        pd.set_option("display.width", 1000)

        # Load Markdown table as data:
        # https://stackoverflow.com/questions/60154404/is-there-the-equivalent-of-to-markdown-to-read-data/60156036#60156036
        # Read a markdown file, getting the header from the first row and index from the second column:
        test_data = pd.read_table(
            StringIO(test_data),
            sep = "|",
            header = 0,
            index_col = 0,
            skipinitialspace = True,
            na_filter = False,
        )
        # Drop the header underline row:
        test_data = test_data.iloc[1:]
        # Remove whitespaces from column names:
        test_data.columns = test_data.columns.str.strip()

        print(test_data)

        env_mock_builder = (
            EnvMockBuilder()
            # Not using client:
            .set_mock_client_config_file_read(False)
            .set_client_config_with_local_server(False)
            .set_test_data_ids_to_load([
                "TD_63_37_05_36",  # default
            ])
        )
        with env_mock_builder.build():

            # All we want is started `LocalServer` with data:
            server_config = server_config_desc.from_default_file()
            local_server = LocalServer(server_config)
            local_server.start_local_server()
            mongo_col = local_server.get_mongo_database()[data_envelopes_]

            # For each populated row, verify that such `HostName`/`ServiceName` exists.
            for table_index, table_row in test_data.iterrows():
                is_populated = table_row["is_populated"]

                if str(is_populated).strip() == "Y":

                    code_maturity = table_row[f"`{ServiceArgType.CodeMaturity}`"].strip().strip("`")
                    geo_region = table_row[f"`{ServiceArgType.GeoRegion}`"].strip().strip("`")
                    flow_stage = table_row[f"`{ServiceArgType.FlowStage}`"].strip().strip("`")

                    cluster_name = table_row[f"`{ServiceArgType.ClusterName}`"].strip().strip("`")

                    self.assertEqual(cluster_name, f"{code_maturity}-{geo_region}-{flow_stage}")

                    host_name = table_row[f"`{ServiceArgType.HostName}`"].strip().strip("`")
                    service_name = table_row[f"`{ServiceArgType.ServiceName}`"].strip().strip("`")

                    # Whether `ServiceName` specified:
                    is_cluster = host_name == ""
                    # Whether `ServiceName` specified:
                    is_host = service_name == ""

                    query_dict = {
                        test_data_: "TD_63_37_05_36",  # default
                        ServiceArgType.CodeMaturity.name: code_maturity,
                        ServiceArgType.GeoRegion.name: geo_region,
                        ServiceArgType.FlowStage.name: flow_stage,
                        ServiceArgType.ClusterName.name: cluster_name,
                    }
                    if is_cluster:
                        query_dict.update({
                            envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                        })
                        self.find_single_data_envelope(mongo_col, query_dict)
                    else:
                        # TODO: FS_82_35_57_62: current data is indexed by `ClusterName` only,
                        #       fix it to include all other arg types,
                        #       remove keys for now:
                        del query_dict[ServiceArgType.CodeMaturity.name]
                        del query_dict[ServiceArgType.GeoRegion.name]
                        del query_dict[ServiceArgType.FlowStage.name]

                        query_dict.update({
                            ServiceArgType.HostName.name: host_name,
                        })
                        if is_host:
                            query_dict.update({
                                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                            })
                            # Ensure `HostName` contains abbreviation of (`CodeMaturity`, `FlowStage`) as its suffix:
                            data_envelope = self.find_single_data_envelope(mongo_col, query_dict)
                            self.assertTrue(
                                code_maturity[0]
                                +
                                flow_stage[0]
                                in
                                data_envelope[ServiceArgType.HostName.name]
                            )
                        else:
                            query_dict.update({
                                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                                ServiceArgType.ServiceName.name: service_name,
                            })
                            self.find_single_data_envelope(mongo_col, query_dict)

    def find_single_data_envelope(self, mongo_col, query_dict) -> dict:
        query_res = mongo_col.find(query_dict)
        found_count = 0

        for data_envelope in iter(query_res):
            found_count += 1

        self.assertEqual(1, found_count, query_dict)
        return data_envelope
