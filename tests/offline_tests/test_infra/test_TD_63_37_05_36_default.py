import re
from io import StringIO

import pandas as pd

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.QueryEngine import scalar_to_list_values
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.test_infra import change_to_known_repo_path, test_data_
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.EnvMockBuilder import ServerOnlyEnvMockBuilder


class ThisTestClass(BaseTestClass):
    """
    Verify TD_63_37_05_36 # demo
    """

    def test_match_data_with_docs(self):
        """
        Matches data with its description in the table - see:
        TD_63_37_05_36.demo_services_data.md

        This data is relatively large - this test ensures it maintains required properties.

        Note: consider generating table view for review instead of consuming one created manually.
        """

        with change_to_known_repo_path():
            # Filter out only table lines from Markdown file:
            table_regex = re.compile("^\|")
            test_data = ""
            with open("../docs/test_data/TD_63_37_05_36.demo_services_data.md") as md_file:
                for file_line in md_file:
                    if table_regex.match(file_line):
                        test_data += file_line
        print(test_data)

        # Configure to print all:
        pd.set_option("display.max_rows", 500)
        pd.set_option("display.max_columns", 500)
        pd.set_option("display.width", 1000)

        # Load Markdown table as data:
        # https://stackoverflow.com/a/60156036/441652
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
            ServerOnlyEnvMockBuilder()
            .set_test_data_ids_to_load([
                "TD_63_37_05_36",  # demo
            ])
        )
        with env_mock_builder.build():

            # All we want is started `LocalServer` with data:
            server_config = server_config_desc.obj_from_default_file()
            local_server = LocalServer(server_config)
            local_server.start_local_server()

            # For each populated row, verify that such `host_name`/`service_name` exists.
            for table_index, table_row in test_data.iterrows():
                is_populated = table_row["is_populated"]

                if str(is_populated).strip() == "Y":

                    code_maturity = table_row[f"`{ServiceArgType.code_maturity}`"].strip().strip("`")
                    geo_region = table_row[f"`{ServiceArgType.geo_region}`"].strip().strip("`")
                    flow_stage = table_row[f"`{ServiceArgType.flow_stage}`"].strip().strip("`")

                    cluster_name = table_row[f"`{ServiceArgType.cluster_name}`"].strip().strip("`")

                    self.assertEqual(cluster_name, f"{code_maturity}-{geo_region}-{flow_stage}")

                    host_name = table_row[f"`{ServiceArgType.host_name}`"].strip().strip("`")
                    service_name = table_row[f"`{ServiceArgType.service_name}`"].strip().strip("`")

                    ip_address = table_row[f"`{ServiceArgType.ip_address}`"].strip().strip("`")
                    data_center = table_row[f"`{ServiceArgType.data_center}`"].strip().strip("`")

                    group_label: str = table_row[f"`{ServiceArgType.group_label}`"].strip().strip("`")

                    # Whether `service_name` specified:
                    is_cluster = host_name == ""
                    # Whether `service_name` specified:
                    is_host = service_name == ""

                    query_dict = {
                        test_data_: "TD_63_37_05_36",  # demo
                        ServiceArgType.code_maturity.name: code_maturity,
                        ServiceArgType.geo_region.name: geo_region,
                        ServiceArgType.flow_stage.name: flow_stage,
                        ServiceArgType.cluster_name.name: cluster_name,
                    }
                    if is_cluster:
                        query_dict.update({
                            ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                        })
                        mongo_col = local_server.get_mongo_database()[ServiceEnvelopeClass.ClassCluster.name]
                        self.find_single_data_envelope(mongo_col, query_dict)
                    else:

                        # If in `dc.AB`, the first digit `A` is non-zero,
                        # it must be another data center with another IP address:
                        if data_center[3] != "0":
                            self.assertTrue("ip.172.16" in ip_address)
                        else:
                            self.assertTrue("ip.192.168" in ip_address)

                        # TODO: FS_82_35_57_62: when both host and services are separately
                        #                       indexed (without pending cluster),
                        #                       add tests that providing ip to both host and service function lookup
                        #                       immediately selects cluster implicitly.

                        query_dict.update({
                            ServiceArgType.host_name.name: host_name,
                        })
                        if is_host:
                            query_dict.update({
                                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                            })
                            mongo_col = local_server.get_mongo_database()[ServiceEnvelopeClass.ClassHost.name]
                            # Ensure `host_name` contains abbreviation of (`code_maturity`, `flow_stage`) as its suffix:
                            host_data_envelope = self.find_single_data_envelope(mongo_col, query_dict)
                            self.assertTrue(
                                code_maturity[0]
                                +
                                flow_stage[0]
                                in
                                host_data_envelope[ServiceArgType.host_name.name]
                            )
                        else:
                            query_dict.update({
                                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                            })
                            mongo_col = local_server.get_mongo_database()[ServiceEnvelopeClass.ClassHost.name]
                            host_data_envelope = self.find_single_data_envelope(mongo_col, query_dict)

                            query_dict.update({
                                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                                ServiceArgType.service_name.name: service_name,
                            })
                            mongo_col = local_server.get_mongo_database()[ServiceEnvelopeClass.ClassService.name]
                            service_data_envelope = self.find_single_data_envelope(mongo_col, query_dict)

                            # Both host and service should have same host name:
                            self.assertEqual(
                                host_data_envelope[ServiceArgType.host_name.name],
                                service_data_envelope[ServiceArgType.host_name.name],
                            )

                            # IP address should match:
                            self.assertEqual(
                                host_data_envelope[ServiceArgType.ip_address.name],
                                service_data_envelope[ServiceArgType.ip_address.name],
                            )
                            self.assertEqual(
                                ip_address,
                                service_data_envelope[ServiceArgType.ip_address.name],
                            )

                            # Data centers should match:
                            self.assertEqual(
                                host_data_envelope[ServiceArgType.data_center.name],
                                service_data_envelope[ServiceArgType.data_center.name],
                            )
                            self.assertEqual(
                                data_center,
                                service_data_envelope[ServiceArgType.data_center.name],
                            )

                            # group_label is specified in doc as CSV:
                            group_label_values = group_label.split(",")
                            actual_values = service_data_envelope[ServiceArgType.group_label.name]
                            actual_values = scalar_to_list_values(actual_values)
                            self.assertEqual(
                                group_label_values,
                                actual_values,
                            )

    def find_single_data_envelope(
        self,
        mongo_col,
        query_dict,
    ) -> dict:
        query_res = mongo_col.find(query_dict)
        found_count = 0

        data_envelope = None
        for data_envelope in iter(query_res):
            found_count += 1

        self.assertEqual(1, found_count, query_dict)
        return data_envelope
