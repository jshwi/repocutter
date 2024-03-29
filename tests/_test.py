"""
tests._test
===========
"""

# pylint: disable=too-many-arguments,protected-access,too-many-locals
from __future__ import annotations

import os
from pathlib import Path
from subprocess import CalledProcessError

import checksumdir
import pytest
import tomli_w

import repocutter

from ._utils import (
    GIT_DIR,
    GIT_TREE,
    PYPROJECT_TOML,
    FixtureMain,
    FixtureMakeRepos,
    FixtureMakeTree,
    FixtureMockCookiecutter,
    FixtureMockTemporaryDirectory,
    Git,
    KeyWords,
    MockJson,
    PyProjectParams,
    Repo,
    description,
    file,
    flags,
    folder,
    name,
    name_dash,
    tmp,
    version,
)


def test_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test ``repocutter.__version__``.

    :param monkeypatch: Mock patch environment and attributes.
    """
    monkeypatch.setattr("repocutter.__version__", version[0])
    assert repocutter.__version__ == version[0]


def test_main_exit_status(
    capsys: pytest.CaptureFixture,
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
    mock_json: MockJson,
) -> None:
    """Test ``repocutter.main``.

    Test successful exit status.

    Test config correctly written.

    Test success output.

    :param capsys: Capture sys out and err.
    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param mock_json: Mock ``json`` module.
    """
    checksum = checksumdir.dirhash(cookiecutter_package)
    keywords = KeyWords(0)
    repos = make_repos(
        Repo(
            name[0],
            {
                GIT_DIR: GIT_TREE,
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        name[0], description[0], keywords, version[0]
                    )
                ),
            },
        )
    )
    mock_cookiecutter(lambda *_, **__: None)
    assert main(cookiecutter_package, repos[0]) == 0
    assert mock_json.dumped["project_name"] == name[0]
    assert mock_json.dumped["project_description"] == description[0]
    assert mock_json.dumped["project_keywords"] == ",".join(keywords)
    assert mock_json.dumped["project_version"] == version[0]
    assert mock_json.dumped["include_entry_point"] == "n"
    assert checksumdir.dirhash(cookiecutter_package) == checksum
    std = capsys.readouterr()
    assert "success" in std.out
    assert "stash" in repocutter._main._git.called


def test_main_post_hook_git(
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
    make_tree: FixtureMakeTree,
) -> None:
    """Test ``repocutter.main`` with a post gen hook that inits repo.

    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param make_tree: Make a directory and it's contents.
    """
    repos = make_repos(
        Repo(
            name[0],
            {
                GIT_DIR: GIT_TREE,
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        name[0], description[0], KeyWords(0), version[0]
                    )
                ),
            },
        )
    )
    mock_cookiecutter(
        lambda *_, **__: make_tree(
            repos[0].parent, {repos[0].name: {GIT_DIR: GIT_TREE}}
        )
    )
    main(cookiecutter_package, repos[0])


def test_main_already_cached(
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
    make_tree: FixtureMakeTree,
    mock_temporary_directory: FixtureMockTemporaryDirectory,
) -> None:
    """Test ``repocutter.main`` when the same repo is already saved.

    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param make_tree: Make a directory and it's contents.
    :param mock_temporary_directory: Mock
        ``tempfile.TemporaryDirectory``.
    """
    repos = make_repos(
        Repo(
            name[0],
            {
                GIT_DIR: GIT_TREE,
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        name[0], description[0], KeyWords(0), version[0]
                    )
                ),
            },
        )
    )
    temp_dir_1 = repos[0].parent / tmp[0]
    temp_dir_2 = repos[0].parent / tmp[1]
    mock_temporary_directory(temp_dir_1, temp_dir_2)
    cached = (
        repos[0].parent
        / ".cache"
        / repocutter.__name__
        / f"{name[0]}-{checksumdir.dirhash(repos[0] / GIT_DIR)}"
    )
    cached.mkdir(parents=True)
    make_tree(cached, {GIT_DIR: GIT_TREE})
    mock_cookiecutter(
        lambda *_, **__: make_tree(
            temp_dir_1, {repos[0].name: {GIT_DIR: GIT_TREE}}
        )
    )
    main(cookiecutter_package, repos[0])


def test_main_entry_point(
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
    mock_json: MockJson,
) -> None:
    """Test ``repocutter.main`` with entry point.

    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param mock_json: Mock ``json`` module.
    """
    checksum = checksumdir.dirhash(cookiecutter_package)
    repos = make_repos(
        Repo(
            name[0],
            {
                GIT_DIR: GIT_TREE,
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        name[0], description[0], KeyWords(0), version[0]
                    )
                ),
            },
        )
    )
    package = repos[0] / name[0]
    package.mkdir()
    entry_point = package / "__main__.py"
    entry_point.touch()
    mock_cookiecutter(lambda *_, **__: None)
    main(cookiecutter_package, repos[0])
    assert mock_json.dumped["include_entry_point"] == "y"
    assert checksumdir.dirhash(cookiecutter_package) == checksum


def test_main_ctrl_c(
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
) -> None:
    """Test ``repocutter.main`` with SIGINT.

    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    """
    repos = make_repos(
        Repo(
            name[0],
            {
                GIT_DIR: GIT_TREE,
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        name[0], description[0], KeyWords(0), version[0]
                    )
                ),
            },
        )
    )

    def _sigint(*_: object, **__: object) -> None:
        raise KeyboardInterrupt

    template_checksum = checksumdir.dirhash(cookiecutter_package)
    repo_checksum = checksumdir.dirhash(repos[0])
    mock_cookiecutter(_sigint)
    with pytest.raises(KeyboardInterrupt):
        main(cookiecutter_package, repos[0])

    assert checksumdir.dirhash(cookiecutter_package) == template_checksum
    assert checksumdir.dirhash(repos[0]) == repo_checksum


def test_main_no_dir(
    capsys: pytest.CaptureFixture,
    main: FixtureMain,
    cookiecutter_package: Path,
) -> None:
    """Test ``repocutter.main`` skipping of non-existing dir.

    :param capsys: Capture sys out and err.
    :param main: Mock ``main`` function.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    """
    main(cookiecutter_package, name[0])
    std = capsys.readouterr()
    assert "does not exist" in std.out


def test_main_no_make_repos(
    capsys: pytest.CaptureFixture,
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
) -> None:
    """Test ``repocutter.main`` skipping of non-repository.

    :param capsys: Capture sys out and err.
    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    """
    repos = make_repos(
        Repo(
            name[0],
            {
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        name[0], description[0], KeyWords(0), version[0]
                    )
                )
            },
        )
    )
    main(cookiecutter_package, repos[0])
    std = capsys.readouterr()
    assert "not a repository" in std.out


def test_main_no_pyproject(
    capsys: pytest.CaptureFixture,
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
) -> None:
    """Test ``repocutter.main`` skipping of repos without pyproject.

    :param capsys: Capture sys out and err.
    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    """
    repos = make_repos(Repo(name[0], {GIT_DIR: GIT_TREE}))
    main(cookiecutter_package, repos[0])
    std = capsys.readouterr()
    assert "missing pyproject.toml" in std.out


def test_main_gc(
    capsys: pytest.CaptureFixture,
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
) -> None:
    """Test ``repocutter.main`` with ``-c/--gc``.

    :param capsys: Capture sys out and err.
    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    """
    repos = make_repos(
        Repo(
            name[0],
            {
                GIT_DIR: GIT_TREE,
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        name[0], description[0], KeyWords(0), version[0]
                    )
                ),
            },
        )
    )
    mock_cookiecutter(lambda *_, **__: None)

    # run once to actually create the cache dir
    main(cookiecutter_package, repos[0])

    main(cookiecutter_package, repos[0], flags.gc)
    std = capsys.readouterr()
    assert "cleaning" in std.out


def test_main_avoid_pre_commit_unstaged_error(
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
    make_tree: FixtureMakeTree,
    mock_temporary_directory: FixtureMockTemporaryDirectory,
) -> None:
    """Test ``repocutter.main`` and checking out with pre-commit config.

    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param make_tree: Make a directory and it's contents.
    :param mock_temporary_directory: Mock
        ``tempfile.TemporaryDirectory``.
    """
    repos = make_repos(
        Repo(
            name[0],
            {
                GIT_DIR: GIT_TREE,
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        name[0], description[0], KeyWords(0), version[0]
                    )
                ),
            },
        )
    )
    temp_dir_1 = repos[0].parent / tmp[0]
    temp_dir_2 = repos[0].parent / tmp[1]
    mock_temporary_directory(temp_dir_1, temp_dir_2)
    working_tree = {
        repos[0].name: {".pre-commit-config.yaml": None, file[1]: None}
    }
    make_tree(repos[0].parent, working_tree)
    mock_cookiecutter(lambda *_, **__: make_tree(temp_dir_1, working_tree))
    main(cookiecutter_package, repos[0], flags.ignore, file[1])
    assert "add .pre-commit-config.yaml" in repocutter._main._git.called
    assert "reset .pre-commit-config.yaml" in repocutter._main._git.called


def test_main_no_head(
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
    make_tree: FixtureMakeTree,
    mock_temporary_directory: FixtureMockTemporaryDirectory,
) -> None:
    """Test ``repocutter.main`` when no HEAD to checkout.

    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param make_tree: Make a directory and it's contents.
    :param mock_temporary_directory: Mock
        ``tempfile.TemporaryDirectory``.
    """
    repos = make_repos(
        Repo(
            name[0],
            {
                GIT_DIR: GIT_TREE,
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        name[0], description[0], KeyWords(0), version[0]
                    )
                ),
            },
        )
    )
    called = []

    def _checkout(*args: str, **__: object) -> None:
        called.append(" ".join(str(i) for i in args))
        raise CalledProcessError(1, "checkout")

    # already monkey-patched
    repocutter._main._git.checkout = _checkout

    temp_dir_1 = repos[0].parent / tmp[0]
    temp_dir_2 = repos[0].parent / tmp[1]
    mock_temporary_directory(temp_dir_1, temp_dir_2)
    working_tree = {repos[0].name: {".pre-commit-config.yaml": None}}
    make_tree(repos[0].parent, working_tree)
    mock_cookiecutter(lambda *_, **__: make_tree(temp_dir_1, working_tree))
    main(cookiecutter_package, repos[0], flags.ignore, file[1])
    assert f"HEAD -- {file[1]}" in called


@pytest.mark.parametrize(
    "src_name,path,tree,expected",
    [
        (file[1], file[1], {file[1]: None}, file[1]),
        (
            folder[1],
            folder[1],
            {folder[1]: {file[1]: None, file[2]: None, file[3]: None}},
            folder[1],
        ),
        (
            name[1],
            "{{cookiecutter.project_name}}",
            {name[1]: {file[1]: None}},
            name[1],
        ),
        (
            name[1],
            "{{ cookiecutter.project_name }}",
            {name[1]: {file[1]: None}},
            name[1],
        ),
        (
            "project-slug",
            "{{ cookiecutter.project_slug }}",
            {"project-name": {file[1]: None}},
            "project_slug",
        ),
    ],
    ids=["file", "dir", "interpolate", "interpolate_space", "interpolate_var"],
)
def test_main_ignore_path(
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
    make_tree: FixtureMakeTree,
    mock_temporary_directory: FixtureMockTemporaryDirectory,
    src_name: str,
    path: str,
    tree: dict[str, None | dict[str, dict[str, None]]],
    expected: str,
) -> None:
    """Test ``repocutter.main`` and ``-i/--ignore`` argument.

    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param make_tree: Make a directory and it's contents.
    :param mock_temporary_directory: Mock
        ``tempfile.TemporaryDirectory``.
    :param src_name: Project name.
    :param path: Path to ignore.
    :param tree: Tree to mock.
    :param expected: Expected result.
    """
    repos = make_repos(
        Repo(
            src_name,
            {
                GIT_DIR: GIT_TREE,
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        src_name, description[1], KeyWords(1), version[1]
                    )
                ),
            },
        )
    )
    temp_dir_1 = repos[0].parent / tmp[0]
    temp_dir_2 = repos[0].parent / tmp[1]
    mock_temporary_directory(temp_dir_1, temp_dir_2)
    working_tree = {src_name: tree}
    make_tree(repos[0].parent, working_tree)
    mock_cookiecutter(lambda *_, **__: make_tree(temp_dir_1, working_tree))
    main(cookiecutter_package, repos[0], flags.ignore, path)
    assert f"checkout HEAD -- {expected}" in repocutter._main._git.called


def test_main_checkout_branch(
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
) -> None:
    """Test ``repocutter.main`` when checking out branches.

    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    """
    repos = make_repos(
        Repo(
            name[0],
            {
                GIT_DIR: GIT_TREE,
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        name[0], description[0], KeyWords(0), version[0]
                    )
                ),
            },
        )
    )
    mock_cookiecutter(lambda *_, **__: None)
    main(cookiecutter_package, repos[0], flags.branch, "master,cookiecutter")
    assert "checkout master" in repocutter._main._git.called
    assert "checkout -b cookiecutter" in repocutter._main._git.called


@pytest.mark.parametrize(
    "first,second,expected",
    [
        (0, 1, "checkout -b cookiecutter failed"),
        (1, 0, "checkout master failed"),
        (2, 1, "checkout -b cookiecutter failed"),
    ],
    ids=["new", "rev", "already-rev"],
)
def test_main_checkout_branch_fail(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
    first: int,
    second: int,
    expected: str,
) -> None:
    """Test ``repocutter.main`` when checking out branches.

    :param monkeypatch: Mock patch environment and attributes.
    :param capsys: Capture sys out and err.
    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param first: Result of first call the ``checkout``.
    :param second: Result of second call the ``checkout``.
    :param expected: Expected result.
    """
    repos = make_repos(
        Repo(
            name[0],
            {
                GIT_DIR: GIT_TREE,
                PYPROJECT_TOML: tomli_w.dumps(
                    PyProjectParams(
                        name[0], description[0], KeyWords(0), version[0]
                    )
                ),
            },
        )
    )
    calls = []

    def fail(self: Git, *args: str, **__: object) -> None:
        self._stderr.append(f"error: {' '.join(str(i) for i in args)} failed")
        raise CalledProcessError(1, "checkout")

    def _stderr_but_no_fail(self: Git, *_: str, **__: object) -> None:
        self._stderr.append("Already on 'master'")

    mocker = [lambda *_, **__: None, fail, _stderr_but_no_fail]
    calls.extend([mocker[0], mocker[first], mocker[second]])

    class _Git(Git):
        def call(self, *args: str, **_: bool | str | os.PathLike) -> int:
            calls.pop(0)(self, *args)  # type: ignore
            return 0

    monkeypatch.setattr("repocutter._main._git", _Git())
    mock_cookiecutter(lambda *_, **__: None)
    main(cookiecutter_package, repos[0], flags.branch, "master,cookiecutter")
    std = capsys.readouterr()
    assert expected in std.out


def test_main_interpolate_var(
    main: FixtureMain,
    make_repos: FixtureMakeRepos,
    cookiecutter_package: Path,
    mock_cookiecutter: FixtureMockCookiecutter,
    make_tree: FixtureMakeTree,
    mock_temporary_directory: FixtureMockTemporaryDirectory,
) -> None:
    """Test ``repocutter.main`` with vars defined in json.

    Confirm that interpolated string is reset between looping, as if
    variable is simply overridden, the config will hold the interpolated
    var from the previous run.

    Position of defaults and the addition of a read only and write only
    config solves this problem.

    :param main: Mock ``main`` function.
    :param make_repos: Create and return a test repo to cut.
    :param cookiecutter_package: Create and return a test
        ``cookiecutter`` template package.
    :param mock_cookiecutter: Mock ``cookiecutter`` module.
    :param make_tree: Make a directory and it's contents.
    :param mock_temporary_directory: Mock
        ``tempfile.TemporaryDirectory``.
    """
    tree_1 = {
        GIT_DIR: GIT_TREE,
        PYPROJECT_TOML: tomli_w.dumps(
            PyProjectParams(
                name_dash[0], description[0], KeyWords(0), version[0]
            )
        ),
    }
    tree_2 = {
        GIT_DIR: GIT_TREE,
        PYPROJECT_TOML: tomli_w.dumps(
            PyProjectParams(
                name_dash[1], description[1], KeyWords(1), version[1]
            )
        ),
    }
    tree_3 = {
        GIT_DIR: GIT_TREE,
        PYPROJECT_TOML: tomli_w.dumps(
            PyProjectParams(
                name_dash[2], description[2], KeyWords(2), version[2]
            )
        ),
    }
    repos = make_repos(
        Repo(name_dash[0], tree_1),
        Repo(name_dash[1], tree_2),
        Repo(name_dash[2], tree_3),
    )
    temp_dir_1 = repos[0].parent / tmp[0]
    temp_dir_2 = repos[0].parent / tmp[1]
    temp_dir_3 = repos[0].parent / tmp[2]
    temp_dir_4 = repos[0].parent / tmp[3]
    mock_temporary_directory(temp_dir_1, temp_dir_2, temp_dir_3, temp_dir_4)
    cookiecutter_calls = [
        lambda *_, **__: make_tree(temp_dir_1, {name_dash[0]: tree_1}),
        lambda *_, **__: make_tree(temp_dir_1, {name_dash[1]: tree_2}),
        lambda *_, **__: make_tree(temp_dir_1, {name_dash[2]: tree_3}),
    ]
    mock_cookiecutter(cookiecutter_calls.pop(0))
    main(
        cookiecutter_package,
        repos[0],
        repos[1],
        repos[2],
        flags.ignore,
        "{{ cookiecutter.project_slug }}",
    )
    assert f"checkout HEAD -- {name[0]}" in repocutter._main._git.called
    assert f"checkout HEAD -- {name[1]}" in repocutter._main._git.called
    assert f"checkout HEAD -- {name[2]}" in repocutter._main._git.called
