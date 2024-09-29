from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen = True)
class EnvelopeCollection:
    """
    Allows distributing `data_envelope`-s across FS_56_43_05_79 different collections.

    Specifies collection of `data_envelope`-s to load and associated `index_props` to create.

    See also `EnvelopeCollectionSchema`.

    TODO: TODO_00_79_72_55: Remove `static_data` from `server_config`.
          This class should be remove together with `static_data`
          (it seems it is the only place where is "attached" to).
    """

    # TODO: FS_45_08_22_15 data model manipulation: remove to deduplicate with `DataModel`.
    index_props: list[str] = field()
    """
    Lists fields of `data_envelop` which are to be indexed by MongoDB for given collection.
    """

    data_envelopes: list = field()
