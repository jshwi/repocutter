"""
tests
=====

Test package for ``repocutter``.
"""
import typing as t
from pathlib import Path

from templatest.utils import VarSeq

FixtureMain = t.Callable[..., int]
FixtureMakeTree = t.Callable[[Path, t.Dict[t.Any, t.Any]], None]
FixtureGitInit = t.Callable[[Path], None]
FixtureWritePyprojectToml = t.Callable[
    [Path, str, str, t.Tuple[str, ...], str], None
]
FixtureMockCookiecutter = t.Callable[[t.Callable[..., None]], None]

name = VarSeq("name")
description = VarSeq("description")

VERSION = "0.1.0"
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
