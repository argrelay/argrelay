from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen = True)
class EnvelopeCollection:
    """
    Allows distributing `data_envelope`-s across FS_56_43_05_79 different collections.

    Specifies collection of `data_envelope`-s to load and associated `index_fields` to create.

    See also `EnvelopeCollectionSchema`.
    """
    index_fields: list = field()
    """
    Lists fields of `data_envelop` which are to be indexed by MongoDB for given collection.
    """

    data_envelopes: list = field()
