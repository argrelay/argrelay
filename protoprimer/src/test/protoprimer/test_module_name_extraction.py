from protoprimer import proto_code
from test_support import BaseTestClass


# noinspection PyMethodMayBeStatic
class ThisTestClass(BaseTestClass):

    def test_module_name_extraction(self):
        self.assertEqual(
            proto_code.__name__,
            "protoprimer.proto_code",
        )
