from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen = True)
class EnvelopeCollection:
    """
    Allows distributing `data_envelope`-s across FS_56_43_05_79 different collections on data load.

    See also `EnvelopeCollectionSchema`.
    """

    collection_name: str = field()

    data_envelopes: list = field()
