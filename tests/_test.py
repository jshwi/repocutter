"""
tests._test
===========
"""
import shutil

# pylint: disable=too-many-arguments
from pathlib import Path

import checksumdir
import pytest

import repocutter

from . import (
    GIT_DIR,
    GIT_TREE,
    KEYWORDS,
    PYPROJECT_TOML,
    VERSION,
    FixtureMain,
    FixtureMakeTree,
    FixtureMockCookiecutter,
    FixtureMockTemporaryDirectory,
    FixtureWritePyprojectToml,
    description,
    name,
)
from ._utils import MockJson


def test_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test ``repocutter.__version__``.

    :param monkeypatch: Mock patch environment and attributes.
    """
    monkeypatch.setattr("repocutter.__version__", VERSION)
    assert repocutter.__version__ == VERSION


def test_main_exit_status(
    capsys: pytest.CaptureFixture,
    main: FixtureMain,
    repo: Path,
    cookiecutter_package: Path,
    write_pyproject_toml: FixtureWritePyprojectToml,
    mock_cookiecutter: FixtureMockCookiecutter,
    mock_json: MockJson,
) -> None:
    """Test ``repocutter.main``.

    Test successful exit status.

    Test config correctly written.

    Test success output.

    :param capsys: Capture sys out and err.
    :param main: Mock ``main`` function.
    :param repo: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param write_pyproject_toml: Write pyproject.toml file with test
        attributes.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param mock_json: Mock ``json`` module.
    """
    checksum = checksumdir.dirhash(cookiecutter_package)
    write_pyproject_toml(
        repo / PYPROJECT_TOML, name[0], description[0], KEYWORDS, VERSION
    )
    mock_cookiecutter(lambda *_, **__: None)
    assert main(cookiecutter_package, repo) == 0
    assert mock_json.dumped["project_name"] == name[0]
    assert mock_json.dumped["project_description"] == description[0]
    assert mock_json.dumped["project_keywords"] == ",".join(KEYWORDS)
    assert mock_json.dumped["project_version"] == VERSION
    assert mock_json.dumped["include_entry_point"] == "n"
    assert checksumdir.dirhash(cookiecutter_package) == checksum
    std = capsys.readouterr()
    assert "success" in std.out


def test_main_post_hook_git(
    tmp_path: Path,
    main: FixtureMain,
    repo: Path,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
    make_tree: FixtureMakeTree,
    write_pyproject_toml: FixtureWritePyprojectToml,
) -> None:
    """Test ``repocutter.main`` with a post gen hook that inits repo.

    :param tmp_path: Create and return temporary directory.
    :param main: Mock ``main`` function.
    :param repo: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param make_tree: Make a directory and it's contents.
    :param write_pyproject_toml: Write pyproject.toml file with test
        attributes.
    """
    write_pyproject_toml(
        repo / PYPROJECT_TOML, name[0], description[0], KEYWORDS, VERSION
    )
    mock_cookiecutter(
        lambda *_, **__: make_tree(tmp_path, {"repo": {GIT_DIR: GIT_TREE}})
    )
    main(cookiecutter_package, repo)


def test_main_already_cached(
    tmp_path: Path,
    main: FixtureMain,
    repo: Path,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
    make_tree: FixtureMakeTree,
    write_pyproject_toml: FixtureWritePyprojectToml,
    mock_temporary_directory: FixtureMockTemporaryDirectory,
) -> None:
    """Test ``repocutter.main`` when the same repo is already saved.

    :param tmp_path: Create and return temporary directory.
    :param main: Mock ``main`` function.
    :param repo: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param make_tree: Make a directory and it's contents.
    :param write_pyproject_toml: Write pyproject.toml file with test
        attributes.
    :param mock_temporary_directory: Mock
        ``tempfile.TemporaryDirectory``.
    """
    temp_dir = tmp_path / "tmp"
    write_pyproject_toml(
        repo / PYPROJECT_TOML, name[0], description[0], KEYWORDS, VERSION
    )
    mock_temporary_directory(temp_dir)
    cached = (
        tmp_path
        / ".cache"
        / repocutter.__name__
        / f"repo-{checksumdir.dirhash(repo / GIT_DIR)}"
    )
    cached.mkdir(parents=True)
    make_tree(cached, {GIT_DIR: GIT_TREE})
    mock_cookiecutter(
        lambda *_, **__: make_tree(temp_dir, {"repo": {GIT_DIR: GIT_TREE}})
    )
    main(cookiecutter_package, repo)


def test_main_entry_point(
    main: FixtureMain,
    repo: Path,
    cookiecutter_package: Path,
    write_pyproject_toml: FixtureWritePyprojectToml,
    mock_cookiecutter: FixtureMockCookiecutter,
    mock_json: MockJson,
) -> None:
    """Test ``repocutter.main`` with entry point.

    :param main: Mock ``main`` function.
    :param repo: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param write_pyproject_toml: Write pyproject.toml file with test
        attributes.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param mock_json: Mock ``json`` module.
    """
    checksum = checksumdir.dirhash(cookiecutter_package)
    write_pyproject_toml(
        repo / PYPROJECT_TOML, name[0], description[0], KEYWORDS, VERSION
    )
    package = repo / name[0]
    package.mkdir()
    entry_point = package / "__main__.py"
    entry_point.touch()
    mock_cookiecutter(lambda *_, **__: None)
    main(cookiecutter_package, repo)
    assert mock_json.dumped["include_entry_point"] == "y"
    assert checksumdir.dirhash(cookiecutter_package) == checksum


def test_main_ctrl_c(
    main: FixtureMain,
    repo: Path,
    cookiecutter_package: Path,
    write_pyproject_toml: FixtureWritePyprojectToml,
    mock_cookiecutter: FixtureMockCookiecutter,
) -> None:
    """Test ``repocutter.main`` with SIGINT.

    :param main: Mock ``main`` function.
    :param repo: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param write_pyproject_toml: Write pyproject.toml file with test
        attributes.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    """

    def _sigint(*_: object, **__: object) -> None:
        raise KeyboardInterrupt

    write_pyproject_toml(
        repo / PYPROJECT_TOML, name[0], description[0], KEYWORDS, VERSION
    )
    template_checksum = checksumdir.dirhash(cookiecutter_package)
    repo_checksum = checksumdir.dirhash(repo)
    mock_cookiecutter(_sigint)
    with pytest.raises(KeyboardInterrupt):
        main(cookiecutter_package, repo)

    assert checksumdir.dirhash(cookiecutter_package) == template_checksum
    assert checksumdir.dirhash(repo) == repo_checksum


def test_main_no_dir(
    capsys: pytest.CaptureFixture,
    main: FixtureMain,
    repo: Path,
    cookiecutter_package: Path,
) -> None:
    """Test ``repocutter.main`` skipping of non-existing dir.

    :param capsys: Capture sys out and err.
    :param main: Mock ``main`` function.
    :param repo: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    """
    shutil.rmtree(repo)
    main(cookiecutter_package, repo)
    std = capsys.readouterr()
    assert "does not exist" in std.out


def test_main_no_repo(
    capsys: pytest.CaptureFixture,
    main: FixtureMain,
    repo: Path,
    cookiecutter_package: Path,
) -> None:
    """Test ``repocutter.main`` skipping of non-repository.

    :param capsys: Capture sys out and err.
    :param main: Mock ``main`` function.
    :param repo: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    """
    shutil.rmtree(repo / ".git")
    main(cookiecutter_package, repo)
    std = capsys.readouterr()
    assert "not a repository" in std.out
