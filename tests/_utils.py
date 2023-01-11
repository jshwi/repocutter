"""
tests._utils
============
"""
# pylint: disable=too-few-public-methods
from __future__ import annotations

import json


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
