"""
repocutter._main
================

Contains package entry point.
"""
from __future__ import annotations

import contextlib as _contextlib
import json as _json
import os as _os
import re as _re
import shutil as _shutil
import typing as _t
from argparse import HelpFormatter as _HelpFormatter
from pathlib import Path as _Path
from subprocess import CalledProcessError as _CalledProcessError
from tempfile import TemporaryDirectory as _TemporaryDirectory
from types import TracebackType as _TracebackType

import appdirs as _appdirs
import checksumdir as _checksumdir
import tomli as _tomli
from arcon import ArgumentParser as _ArgumentParser
from cookiecutter.environment import StrictEnvironment as _StrictEnvironment
from cookiecutter.main import cookiecutter as _cookiecutter
from cookiecutter.prompt import render_variable as _render_variable
from gitspy import Git as _Git
from object_colors import Color as _Color

from ._version import __version__

_NAME = __name__.split(".", maxsplit=1)[0]
_GIT_DIR = ".git"
_INFO = 20
_WARNING = 30
_ERROR = 40
_PRE_COMMIT_CONFIG = ".pre-commit-config.yaml"
_HOOKS = "hooks"

_git = _Git()
_color = _Color()

_color.populate_colors()


class _Parser(_ArgumentParser):
    def __init__(self) -> None:
        super().__init__(
            __version__,
            prog=_color.cyan.get(_NAME),
            description="Checkout repos to current cookiecutter config",
            formatter_class=lambda prog: _HelpFormatter(
                prog, max_help_position=45
            ),
        )
        self._add_arguments()
        self.args = self.parse_args()
        self.args.repos = tuple(_Path(i) for i in self.args.repos)
        self.args.ignore = tuple(_Path(i) for i in self.args.ignore)

    def _add_arguments(self) -> None:
        self.add_argument(
            "path",
            action="store",
            type=_Path,
            metavar="PATH",
            help="path to cookiecutter template dir",
        )
        self.add_argument(
            "repos",
            nargs="*",
            action="store",
            metavar="REPOS",
            help="repos to run cookiecutter over",
        )
        self.add_argument(
            "-a",
            "--accept-hooks",
            action="store_true",
            help="accept pre/post hooks",
        )
        self.add_argument(
            "-c",
            "--gc",
            action="store_true",
            help="clean up backups from previous runs",
        )
        self.add_list_argument(
            "-b",
            "--branch",
            action="store",
            metavar="REV,NEW",
            help="checkout new branch from existing revision",
        )
        self.add_list_argument(
            "-i",
            "--ignore",
            action="store",
            metavar="LIST",
            help=(
                "comma separated list of paths to ignore, cookiecutter vars"
                " are allowed"
            ),
        )


class _MetaData(_t.Dict[str, str]):
    _keys = "name", "version", "description", "keywords"

    @staticmethod
    def _format(key: object) -> str:
        if isinstance(key, list):
            return ",".join(key)

        return str(key)

    def __init__(self, __m: dict[str, dict[str, dict[str, str]]]) -> None:
        super().__init__(
            {
                f"project_{k}": self._format(__m["tool"]["poetry"][k])
                for k in self._keys
            }
        )

    def setentry(self, repo: _Path) -> None:
        """Set the ``include_entry_point`` key.

        :param repo: Path to repository.
        """
        main_file = repo / self["project_name"] / "__main__.py"
        self["include_entry_point"] = "y" if main_file.is_file() else "n"


class _Defaults(_t.Dict[str, _t.Union[str, _t.List[str]]]):
    def __init__(self, __m: dict[str, str | list[str]]) -> None:
        super().__init__(__m)
        self._env = _StrictEnvironment(context=self)

    def render(self, metadata: _MetaData) -> None:
        """Update and render `jinja2` template vars with parsed data.

        :param metadata: Data parsed from config.
        """
        self.update(metadata)
        for key, value in self.items():
            self[key] = _render_variable(self._env, value, self)


class _ChDir:
    def __init__(self, path: _Path) -> None:
        self._cwd = _Path.cwd()
        _os.chdir(path)

    def __enter__(self) -> _ChDir:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: _TracebackType | None,
    ):
        _os.chdir(self._cwd)


@_contextlib.contextmanager
def _temporary_directory() -> _t.Generator[_Path, None, None]:
    with _TemporaryDirectory() as tempdir:
        yield _Path(tempdir)


def _report(level: int, repo: _Path, message: str) -> None:
    ident = (15 - len(str(repo))) * " "
    color = {_INFO: _color.green, _WARNING: _color.yellow, _ERROR: _color.red}
    print(f"[{color[level].get(repo)}{ident}] {message}")


def _garbage_collection(cache_dir: _Path) -> None:
    if cache_dir.is_dir():
        _report(_INFO, cache_dir, "cleaning")
        for path in cache_dir.iterdir():
            _shutil.rmtree(path)


@_contextlib.contextmanager
def _stage_pre_commit(repo: _Path) -> _t.Generator[None, None, None]:
    path = repo / _PRE_COMMIT_CONFIG
    if path.is_file():
        _git.add(path.name)

    yield
    _git.reset(path.name, file=_os.devnull)


@_contextlib.contextmanager
def _disable_hooks(repo: _Path) -> _t.Generator[None, None, None]:
    path = repo / _GIT_DIR / _HOOKS
    with _temporary_directory() as temp:
        temp_hooks = temp / _HOOKS
        if path.is_dir():
            _shutil.move(str(path), temp_hooks)

        yield
        if temp_hooks.is_dir():
            _shutil.move(str(temp_hooks), path)


def _revert_ignored(
    paths: tuple[_Path, ...], repo: _Path, defaults: _Defaults
) -> None:
    with _ChDir(repo):
        with _stage_pre_commit(repo):
            for path in paths:
                rgx = _re.match(r"{{\s?cookiecutter\.(.[^ ]*)\s?}}", str(path))
                if rgx:
                    new_path = defaults.get(rgx.group(1))
                    if not isinstance(new_path, list) and new_path is not None:
                        path = _Path(new_path)

                if path.exists():
                    if path.is_dir():
                        _shutil.rmtree(path)
                    else:
                        _os.remove(path)

                try:
                    _git.checkout("HEAD", "--", str(path), file=_os.devnull)
                except _CalledProcessError:
                    pass


def _checkout_branches(repo: _Path, existing: str, new: str) -> int:
    try:
        _git.checkout(existing, capture=True)
        _git.stderr()  # flush stderr if non-fatal
        _git.checkout("-b", new, capture=True)
    except _CalledProcessError:
        _report(_WARNING, repo, _git.stderr()[0].split(": ")[1])
        return 1

    return 0


def main() -> int:
    """Main function for package.

    :return: Exit status.
    """
    parser = _Parser()
    cache_dir = _Path(_appdirs.user_cache_dir(_NAME))
    if parser.args.gc:
        _garbage_collection(cache_dir)

    readable_config = parser.args.path / "cookiecutter.json"
    with _temporary_directory() as temp:
        template = temp / parser.args.path.name
        _shutil.copytree(parser.args.path, template)
        writeable_config = template / "cookiecutter.json"
        for repo in parser.args.repos:
            defaults = _Defaults(
                _json.loads(readable_config.read_text(encoding="utf-8"))
            )
            pyproject_toml = repo / "pyproject.toml"
            git_dir = repo / _GIT_DIR
            if not repo.is_dir():
                _report(_WARNING, repo, "does not exist")
                continue

            if not git_dir.is_dir():
                _report(_WARNING, repo, "not a repository")
                continue

            if not pyproject_toml.is_file():
                _report(_WARNING, repo, "missing pyproject.toml")
                continue

            temp_repo = temp / repo.name
            _shutil.copytree(repo, temp_repo)
            with _disable_hooks(temp_repo):
                archive_name = f"{repo.name}-{_checksumdir.dirhash(git_dir)}"
                archived_repo = cache_dir / archive_name
                metadata = _MetaData(
                    _tomli.loads(pyproject_toml.read_text(encoding="utf-8"))
                )
                metadata.setentry(repo)
                defaults.render(metadata)
                writeable_config.write_text(
                    _json.dumps(defaults), encoding="utf-8"
                )
                temp_git_dir = temp_repo / _GIT_DIR
                with _ChDir(temp_repo):
                    _git.stash(file=_os.devnull)
                    if parser.args.branch and _checkout_branches(
                        repo, parser.args.branch[0], parser.args.branch[1]
                    ):
                        continue

                if archived_repo.is_dir():
                    _shutil.rmtree(archived_repo)

                _shutil.move(str(temp_repo), archived_repo)
                _cookiecutter(
                    template=str(template),
                    output_dir=str(temp),
                    no_input=True,
                    accept_hooks=parser.args.accept_hooks,
                )
                if temp_git_dir.is_dir():
                    _shutil.rmtree(temp_git_dir)

                _shutil.copytree(archived_repo / _GIT_DIR, temp_git_dir)
                _revert_ignored(parser.args.ignore, temp_repo, defaults)
                _shutil.rmtree(repo)
                _shutil.move(temp_repo, repo)

                _report(_INFO, repo, "success")

    return 0
