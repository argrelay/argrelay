from __future__ import annotations

from unittest import mock


class OpenFileMock:
    """
    Mock file data for specific paths:
    https://stackoverflow.com/a/69681105/441652

    Access to file paths not configured within `OpenFileMock` instance is passed through
    to original built-in open func.
    """
    builtin_open = open

    def __init__(self, path_to_data: dict[str, any]):
        self.path_to_data: dict[str, any] = path_to_data
        self.path_to_mock: dict = {}

    def add_path_data(
        self,
        file_path: str,
        file_data: any,
    ) -> None:
        self.path_to_data[file_path] = file_data

    def open(self, *args, **kwargs):
        file_path = args[0]
        if file_path in self.path_to_data:
            new_mock = mock.mock_open(read_data = self.path_to_data[file_path])
            self.path_to_mock[file_path] = new_mock
            return new_mock(*args, **kwargs)
        return self.builtin_open(*args, **kwargs)
