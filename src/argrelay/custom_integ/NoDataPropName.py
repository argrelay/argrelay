from enum import Enum, auto


class NoDataPropName(Enum):
    """
    These `prop_name`-s are used for (see also):
    *   `ReservedEnvelopeClass.ClassNoData`
    *   `SpecialFunc.func_id_no_data`
    """

    no_data_key_one = auto()
    no_data_key_two = auto()
