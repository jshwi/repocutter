"""
tests.conftest
==============
"""

from __future__ import annotations

import json
import typing as t
from pathlib import Path

import pytest

import repocutter

from ._utils import (
    FixtureMain,
    FixtureMakeRepos,
    FixtureMakeTree,
    FixtureMockCookiecutter,
    FixtureMockTemporaryDirectory,
    Git,
    MockJson,
    MockTemporaryDirectory,
    Repo,
    cookiecutter_json,
)


@pytest.fixture(name="make_tree")
def fixture_make_tree() -> FixtureMakeTree:
    """Recursively create directory tree from dict mapping.

    :return: Function for using this fixture.
    """

    def _make_tree(root: Path, obj: t.Dict[t.Any, t.Any]) -> None:
        for key, value in obj.items():
            fullpath = root / key
            if isinstance(value, dict):
                fullpath.mkdir(exist_ok=True)
                _make_tree(fullpath, value)
            else:
                fullpath.write_text(str(value))

    return _make_tree


@pytest.fixture(name="make_repos")
def fixture_make_repo(
    tmp_path: Path, make_tree: FixtureMakeTree
) -> FixtureMakeRepos:
    """Create and return test repo to cut.

    :param tmp_path: Create and return temporary directory.
    :param make_tree: Make a directory and it's contents.
    :return: Function for using this fixture.
    """

    def _fixture_make_repos(*args: Repo) -> t.List[Path]:
        repos = []
        for arg in args:
            make_tree(tmp_path, {arg.name: arg.contents})
            repos.append(tmp_path / arg.name)

        return repos

    return _fixture_make_repos


@pytest.fixture(name="cookiecutter_package")
def fixture_cookiecutter_package(
    tmp_path: Path, make_tree: FixtureMakeTree
) -> Path:
    """Create and return a test ``cookiecutter`` template package.

    :param tmp_path: Create and return temporary directory.
    :param make_tree: Make a directory and it's contents.
    :return: Function for using this fixture.
    """
    cookiecutter_package = tmp_path / "cookiecutter-package"
    cookiecutter_package.mkdir()
    make_tree(
        cookiecutter_package,
        {
            "cookiecutter.json": json.dumps(cookiecutter_json),
            "{{ cookiecutter.project_name }}": {},
        },
    )
    return cookiecutter_package


@pytest.fixture(name="cache_dir", autouse=True)
def fixture_cache_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch cache dir.

    :param tmp_path: Create and return temporary directory.
    :param monkeypatch: Mock patch environment and attributes.
    """
    monkeypatch.setattr(
        "repocutter._main._appdirs.user_cache_dir",
        lambda x: str(tmp_path / ".cache" / x),
    )


@pytest.fixture(name="environment", autouse=True)
def fixture_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Prepare environment for testing.

    :param monkeypatch: Mock patch environment and attributes.
    :param tmp_path: Create and return temporary directory.
    """
    monkeypatch.setattr("repocutter._main._git", Git())
    monkeypatch.chdir(tmp_path)


@pytest.fixture(name="main")
def fixture_main(monkeypatch: pytest.MonkeyPatch) -> FixtureMain:
    """Pass patched commandline arguments to package's main function.

    :param monkeypatch: Mock patch environment and attributes.
    :return: Function for using this fixture.
    """

    def _main(*args: str) -> int:
        """Run main with custom args."""
        monkeypatch.setattr(
            "sys.argv", [repocutter.__name__, *[str(a) for a in args]]
        )
        return repocutter.main()

    return _main


@pytest.fixture(name="mock_json")
def fixture_mock_json(monkeypatch: pytest.MonkeyPatch) -> MockJson:
    """Mock ``json`` module.

    :param monkeypatch: Mock patch environment and attributes.
    :return: Class behaving as module to capture function actions.
    """
    mock_json = MockJson()
    monkeypatch.setattr("repocutter._main._json", mock_json)
    return mock_json


@pytest.fixture(name="mock_cookiecutter")
def fixture_mock_cookiecutter(
    monkeypatch: pytest.MonkeyPatch,
) -> FixtureMockCookiecutter:
    """Mock ``cookiecutter`` module.

    :param monkeypatch: Mock patch environment and attributes.
    :return: Function for using this fixture.
    """

    def _mock_cookiecutter(action: t.Callable[..., None]):
        monkeypatch.setattr("repocutter._main._cookiecutter", action)

    return _mock_cookiecutter


@pytest.fixture(name="mock_temporary_directory")
def fixture_mock_temporary_dir(
    monkeypatch: pytest.MonkeyPatch,
) -> FixtureMockTemporaryDirectory:
    """Patch ``TemporaryDirectory`` to return test /tmp/<unique> dir.

    :param monkeypatch: Mock patch environment and attributes.
    :return: Function for using this fixture.
    """

    def _mock_temporary_dir(*temp_dirs: Path) -> None:
        monkeypatch.setattr(
            "repocutter._main._TemporaryDirectory",
            MockTemporaryDirectory(*temp_dirs).open,
        )

    return _mock_temporary_dir
