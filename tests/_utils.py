"""
tests._utils
============
"""
# pylint: disable=too-few-public-methods
from __future__ import annotations

import contextlib
import json
import typing as t
from pathlib import Path


class MockJson:
    """Mock ``json`` module."""

    def __init__(self) -> None:
        self._dumped: dict[str, str] = {}

    @property
    def dumped(self) -> dict[str, str]:
        """Return object that has been dumped."""
        return self._dumped

    def dumps(self, obj: dict[str, str]) -> str:
        """Mock ``json.dumps`` to capture what was dumped.

        :param obj: Object to dump.
        :return: str representation of dict as json.
        """
        self._dumped.update(obj)
        return json.dumps(obj)

    @staticmethod
    def loads(string: str) -> dict[str, str]:
        """Mock ``json.loads``.

        :param string: Json str.
        :return: Json str as dict object.
        """
        return json.loads(string)


class Git:
    """Mock ``Git`` object."""

    def stash(self, **_: object) -> None:
        """Disable this method."""


class MockTemporaryDirectory:
    """Mock ``tempfile.TemporaryDirectory``.

    :param temp_dirs: Paths to mock ``tempfile.TemporaryDirectory``
        with.
    """

    def __init__(self, *temp_dirs: Path) -> None:
        self._temp_dirs = list(temp_dirs)

    @contextlib.contextmanager
    def open(self) -> t.Generator[str, None, None]:
        """Mock dir returned from ``TemporaryDirectory`` constructor.

        :return: Generator yielding self.
        """
        temp_dir = self._temp_dirs.pop(0)
        temp_dir.mkdir()
        yield str(temp_dir)
