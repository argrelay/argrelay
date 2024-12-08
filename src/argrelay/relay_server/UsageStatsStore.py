import json
import os

from argrelay.enum_desc.TopDir import TopDir
from argrelay.misc_helper_common import get_argrelay_dir
from argrelay.relay_server.UsageStatsEntry import UsageStatsEntry
from argrelay.relay_server.UsageStatsEntrySchema import usage_stats_entry_desc


class UsageStatsStore:
    """
    Stored entry for FS_87_02_77_34: usage stats.
    """

    def __init__(
        self,
    ):
        store_dir_path = os.path.join(
            get_argrelay_dir(),
            TopDir.var_dir.value,
        )
        os.makedirs(
            store_dir_path,
            exist_ok = True,
        )
        self.store_file_path: str = str(os.path.join(
            store_dir_path,
            "usage_stats",
        ))

    def store_usage_stats_entry(
        self,
        usage_stats_entry: UsageStatsEntry,
    ):
        with open(self.store_file_path, "a") as json_file:
            json.dump(
                usage_stats_entry_desc.dict_from_input_obj(usage_stats_entry),
                json_file,
            )
            json_file.write("\n")
