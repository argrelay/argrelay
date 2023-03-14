from __future__ import annotations

from unittest import mock


class OpenFileMock:
    """
    Mock file data for specific paths:
    https://stackoverflow.com/a/69681105/441652
    """
    builtin_open = open
    path_to_data: dict[str, str]
    path_to_mock: dict

    def __init__(self, path_to_data: dict[str, str]):
        self.path_to_data = path_to_data
        self.path_to_mock = {}

    def open(self, *args, **kwargs):
        file_path = args[0]
        if file_path in self.path_to_data:
            self.path_to_mock[file_path] = mock.mock_open(read_data = self.path_to_data[file_path])
            return self.path_to_mock[file_path](*args, **kwargs)
        return self.builtin_open(*args, **kwargs)
