"""
repocutter._main
================

Contains package entry point.
"""
from __future__ import annotations

import contextlib as _contextlib
import json as _json
import os as _os
import shutil as _shutil
import typing as _t
from pathlib import Path as _Path
from tempfile import TemporaryDirectory as _TemporaryDirectory
from types import TracebackType as _TracebackType

import appdirs as _appdirs
import checksumdir as _checksumdir
import tomli as _tomli
from arcon import ArgumentParser as _ArgumentParser
from cookiecutter.main import cookiecutter as _cookiecutter
from gitspy import Git as _Git
from object_colors import Color as _Color

from ._version import __version__

_NAME = __name__.split(".", maxsplit=1)[0]
_GIT_DIR = ".git"
_INFO = 20
_WARNING = 30
_ERROR = 40

_color = _Color()

_color.populate_colors()


class _Parser(_ArgumentParser):
    def __init__(self) -> None:
        super().__init__(
            __version__,
            prog=_color.cyan.get(_NAME),
            description="Checkout repos to current cookiecutter config",
        )
        self._add_arguments()
        self.args = self.parse_args()
        self.args.repos = tuple(_Path(i) for i in self.args.repos)

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
def temporary_directory() -> _t.Generator[_Path, None, None]:
    """Instantiate a temporary directory as a ``Path`` object.

    :return: Yield a ``Path`` object.
    """
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


def main() -> int:
    """Main function for package.

    :return: Exit status.
    """
    parser = _Parser()
    cache_dir = _Path(_appdirs.user_cache_dir(_NAME))
    git = _Git()
    if parser.args.gc:
        _garbage_collection(cache_dir)

    with temporary_directory() as temp:
        template = temp / parser.args.path.name
        _shutil.copytree(parser.args.path, template)
        config = template / "cookiecutter.json"
        defaults = _json.loads(config.read_text(encoding="utf-8"))
        for repo in parser.args.repos:
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
            archive_name = f"{repo.name}-{_checksumdir.dirhash(git_dir)}"
            archived_repo = cache_dir / archive_name
            metadata = _MetaData(
                _tomli.loads(pyproject_toml.read_text(encoding="utf-8"))
            )
            metadata.setentry(repo)
            defaults.update(metadata)
            config.write_text(_json.dumps(defaults), encoding="utf-8")
            temp_git_dir = temp_repo / _GIT_DIR
            with _ChDir(temp_repo):
                git.stash(file=_os.devnull)

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
            _shutil.rmtree(repo)
            _shutil.move(temp_repo, repo)

            _report(_INFO, repo, "success")

    return 0
