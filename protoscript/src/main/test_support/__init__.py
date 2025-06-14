from unittest import TestCase


class BaseTestClass(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
