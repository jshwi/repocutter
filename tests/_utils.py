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
FixtureMockCookiecutter = t.Callable[[t.Callable[..., None]], None]
FixtureMockTemporaryDirectory = t.Callable[..., None]
FixtureMakeRepos = t.Callable[..., t.List[Path]]

NAME = "name"

name = VarSeq(NAME)
name_dash = VarSeq(NAME, suffix="-")
description = VarSeq("description")
flags = VarPrefix("--", slug="-")
file = VarSeq("file")
folder = VarSeq("dir")
version = VarSeq("1.0", ".")
keyword = VarSeq("keyword")
tmp = VarSeq("tmp")

cookiecutter_json = {
    "author": "Stephen Whitlock",
    "github_username": "jshwi",
    "email": "stephen@jshwisolutions.com",
    "project_name": "project-name",
    "project_slug": "{{ cookiecutter.project_name|lower|replace('-', '_') }}",
    "project_version": "0.0.0",
    "project_description": (
        "Short description for {{ cookiecutter.project_name }}"
    ),
    "project_keywords": "comma,separated,list",
    "include_entry_point": ["n", "y"],
}


GIT_DIR = ".git"
GIT_TREE = {
    "config": None,
    "objects": {"pack": None, "info": None},
    "HEAD": None,
    "FETCH_LOG": None,
    "refs": {"heads": None, "tags": None},
    "FETCH_HEAD": None,
    "hooks": {
        "commit-msg": None,
        "post-checkout": None,
        "post-commit": None,
        "post-merge": None,
        "post-rewrite": None,
        "pre-commit": None,
        "pre-merge-commit": None,
        "prepare-commit-msg": None,
    },
}
PYPROJECT_TOML = "pyproject.toml"


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


class KeyWords(t.List[str]):
    """Represents a list of keywords.

    :param suffix: Something to make the keywords unique.
    """

    def __init__(self, suffix: int) -> None:
        super().__init__([f"{keyword[suffix]}_{i}" for i in range(5)])


class PyProjectParams(
    t.Dict[str, t.Dict[str, t.Dict[str, t.Union[str, t.List[str], KeyWords]]]]
):
    """Represents contents of a pyproject.toml file.

    :param project_name: Name of project.
    :param project_description: Project description.
    :param project_keywords: Project keywords.
    :param project_version: Project's version.
    """

    authors = ["jshwi <stephen@jshwisolutions.com>"]

    def __init__(
        self,
        project_name: str,
        project_description: str,
        project_keywords: KeyWords,
        project_version: str,
    ) -> None:
        super().__init__(
            {
                "tool": {
                    "poetry": {
                        "authors": self.authors,
                        "description": project_description,
                        "documentation": (
                            f"https://{project_name}.readthedocs.io/en/latest"
                        ),
                        "homepage": (
                            f"https://pypi.org/project/{project_name}/"
                        ),
                        "keywords": project_keywords,
                        "license": "MIT",
                        "maintainers": self.authors,
                        NAME: project_name,
                        "readme": "README.rst",
                        "repository": "https://github.com/jshwi/repo1",
                        "version": project_version,
                    }
                }
            }
        )


class Repo(t.NamedTuple):
    """New repository type."""

    name: str
    contents: t.Dict[str, t.Any]
