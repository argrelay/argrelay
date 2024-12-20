from enum import Enum, auto


class NoDataPropName(Enum):
    """
    These `prop_name`-s are used for (see also):
    *   `ReservedEnvelopeClass.class_no_data`
    *   `SpecialFunc.func_id_no_data`
    """

    no_data_prop_name_one = auto()
    no_data_prop_name_two = auto()
