"""
tests._utils
============
"""
# pylint: disable=too-few-public-methods
from __future__ import annotations

import contextlib
import json
import os
import typing as t
from pathlib import Path

from gitspy import Git as _Git
from templatest.utils import VarPrefix, VarSeq

FixtureMain = t.Callable[..., int]
FixtureMakeTree = t.Callable[[Path, t.Dict[t.Any, t.Any]], None]
FixtureGitInit = t.Callable[[Path], None]
FixtureWritePyprojectToml = t.Callable[
    [Path, str, str, t.Tuple[str, ...], str], None
]
FixtureMockCookiecutter = t.Callable[[t.Callable[..., None]], None]
FixtureMockTemporaryDirectory = t.Callable[..., None]

name = VarSeq("name")
description = VarSeq("description")
flags = VarPrefix("--", slug="-")
file = VarSeq("file")
folder = VarSeq("dir")
version = VarSeq("1.0", ".")

KEYWORDS = ("one", "two", "three", "four", "five")
GIT_DIR = ".git"
GIT_TREE = {
    "config": None,
    "objects": {"pack": None, "info": None},
    "HEAD": None,
    "FETCH_LOG": None,
    "refs": {"heads": None, "tags": None},
    "FETCH_HEAD": None,
}
PYPROJECT_TOML = "pyproject.toml"
TMP = "tmp"


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


class Git(_Git):
    """Mock ``Git`` object."""

    def __init__(self) -> None:
        super().__init__()
        self._called: list[str] = []

    def call(self, *args: str, **_: bool | str | os.PathLike) -> int:
        self._called.append(" ".join(str(i) for i in args))
        return 0

    @property
    def called(self) -> list[str]:
        """Get git commands that were called."""
        return self._called


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
