from __future__ import annotations

from dataclasses import dataclass, field
from typing import Collection

from argrelay.misc_helper_common import eprint


@dataclass
class ProgressTracker:
    """
    State and stats to track `data_envelope`-s loading progress.
    """
    envelope_per_col_i: int = field(default = 0)
    envelope_per_col_n: int = field(default = 0)
    base_total_envelope_i: int = field(default = 0)
    total_envelope_i: int = field(default = 0)
    total_envelope_n: int = field(default = 0)

    # Number of envelopes loaded per `collection_name`:
    collection_sizes: dict[str, int] = field(default_factory = dict)

    # TODO: Provide a way to exclude some collection_name and envelope_classes from
    #       requirement of being part of `search_control`.
    #       For example, `ReservedEnvelopeClass.class_help` is used internally (may not be used by `search_control`).
    unused_index_props_per_collection: dict[str, set[str]] = field(default_factory = lambda: {})

    dangling_search_props_per_collection: dict[str, set[str]] = field(default_factory = lambda: {})

    def track_unused_index_props_per_collection_unused_by_search_control(
        self,
        collection_name: str,
        index_props: Collection[str],
    ):
        """
        TODO: deduplicate with `track_dangling_search_props_per_collection_undefined_by_index_model`
        """
        assert len(index_props) > 0
        self.unused_index_props_per_collection.setdefault(
            collection_name,
            set(),
        ).update(index_props)

        prop_names = " ".join(index_props)
        eprint(
            f"`index_model` components not used by any `search_control`: "
            f"`collection_name` [{collection_name}] "
            f"`index_props`: {prop_names} "
        )

    def track_dangling_search_props_per_collection_undefined_by_index_model(
        self,
        collection_name: str,
        search_props: Collection[str],
    ):
        """
        TODO: deduplicate with `track_unused_index_props_per_collection_unused_by_search_control`
        """
        assert len(search_props) > 0
        self.dangling_search_props_per_collection.setdefault(
            collection_name,
            set(),
        ).update(search_props)

        prop_names = " ".join(search_props)
        error_message = (
            f"`collection_name` [{collection_name}] "
            f"`search_props`: {prop_names} "
        )
        if self.collection_sizes.get(collection_name, 0) == 0:
            eprint(
                f"`search_control` components not in `index_model` (but ignoring as collection is empty now): " +
                error_message
            )
        else:
            raise ValueError(
                f"`search_control` components not in `index_model`: " +
                error_message
            )

    def report_collection_sizes(
        self,
    ):
        for collection_name, collection_size in self.collection_sizes.items():
            if collection_size != 0:
                eprint(f"`collection_name` [{collection_name}] size: {collection_size}")
        for collection_name, collection_size in self.collection_sizes.items():
            if collection_size == 0:
                eprint(f"`index_model` declares `collection_name` [{collection_name}] but it is empty")

    def _assert_intermediate_progress(
        self,
    ):
        assert self.envelope_per_col_i <= self.envelope_per_col_n
        assert self.envelope_per_col_n <= self.total_envelope_n
        assert self.total_envelope_i <= self.total_envelope_n

    def _assert_collection_final_progress(
        self,
    ):
        self._assert_intermediate_progress()
        assert self.envelope_per_col_i == self.envelope_per_col_n

    def _assert_total_final_progress(
        self,
    ):
        self._assert_collection_final_progress()
        if self.total_envelope_i != self.total_envelope_n:
            raise AssertionError(
                f"`total_envelope_i` [{self.total_envelope_i}] == "
                f"`total_envelope_n` [{self.total_envelope_n}] "
                f"(not true)"
            )

    def track_collection_size_increment(
        self,
        collection_name: str,
        increment_size: int,
    ):
        """
        Track collection size increment by each store step (after each loader plugin).

        NOTE: It is assumed each loader appends only (does not override existing `data_envelope`-s).
        """
        curr_size = self.collection_sizes.setdefault(collection_name, 0)
        self.collection_sizes[collection_name] = curr_size + increment_size

    def track_collection_indexing_start(
        self,
        collection_name: str,
        increment_size: int,
    ):
        self.base_total_envelope_i: int = self.total_envelope_i
        self.envelope_per_col_i = 0
        self.envelope_per_col_n = increment_size
        self.log_collection_indexing_progress(collection_name)

        assert increment_size <= self.collection_sizes[collection_name]

    def track_collection_indexing_stop(
        self,
        collection_name: str,
    ):
        assert self.envelope_per_col_i == self.total_envelope_i - self.base_total_envelope_i
        self.log_collection_indexing_progress(collection_name)

    def track_collection_indexing_increment(
        self,
        collection_name: str,
    ):
        if self.total_envelope_i > 0 and self.total_envelope_i % 1_000 == 0:
            self.log_collection_indexing_progress(collection_name)
        self.total_envelope_i += 1
        self.envelope_per_col_i += 1

    def log_collection_indexing_progress(
        self,
        collection_name: str,
    ):
        try:
            self._assert_intermediate_progress()
        finally:
            eprint(
                f"collection: {collection_name}: indexed envelopes: "
                f"{self.envelope_per_col_i}/{self.envelope_per_col_n} "
                f"{self.total_envelope_i}/{self.total_envelope_n} "
                "..."
            )

    def track_total_validation_start(
        self,
    ):
        self.total_envelope_i = 0

    def track_total_validation_stop(
        self,
    ):
        self._assert_total_final_progress()
        self.report_collection_sizes()

    def track_collection_validation_start(
        self,
        collection_name: str,
    ):
        eprint(f"collection to validate: {collection_name}")
        self.envelope_per_col_n = self.collection_sizes.get(collection_name, 0)
        self.envelope_per_col_i = 0
        self.log_collection_validation_progress(collection_name)

    def track_collection_validation_stop(
        self,
        collection_name: str,
    ):
        self.log_collection_validation_progress(
            collection_name,
        )
        self._assert_collection_final_progress()

    def track_collection_validation_increment(
        self,
        collection_name: str,
    ):
        self.envelope_per_col_i += 1
        self.total_envelope_i += 1

        if self.total_envelope_i > 0 and self.total_envelope_i % 1_000 == 0:
            self.log_collection_validation_progress(
                collection_name,
            )

    def log_collection_validation_progress(
        self,
        mongo_collection: str,
    ):
        try:
            self._assert_intermediate_progress()
        finally:
            eprint(
                f"collection: {mongo_collection}: validated envelopes: "
                f"{self.envelope_per_col_i}/{self.envelope_per_col_n} "
                f"{self.total_envelope_i}/{self.total_envelope_n} "
                f"..."
            )
