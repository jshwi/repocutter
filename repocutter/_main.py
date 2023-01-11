"""
repocutter._main
================

Contains package entry point.
"""
from __future__ import annotations

import json as _json
import os as _os
import shutil as _shutil
import typing as _t
from pathlib import Path as _Path
from types import TracebackType as _TracebackType

import appdirs as _appdirs
import checksumdir as _checksumdir
import tomli as _tomli
from arcon import ArgumentParser as _ArgumentParser
from cookiecutter.main import cookiecutter as _cookiecutter
from gitspy import Git as _Git
from object_colors import Color as _Color

from ._version import __version__

NAME = __name__.split(".", maxsplit=1)[0]

_color = _Color()

_color.populate_colors()


class _Parser(_ArgumentParser):
    def __init__(self) -> None:
        super().__init__(
            __version__,
            prog=_color.cyan.get(NAME),
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
            help="pat,h to cookiecutter template dir",
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


class _ConfigBuffer:
    def __init__(self, config: _Path) -> None:
        self._config = config
        self._buffer = config.read_text(encoding="utf-8")

    def __enter__(self) -> _ConfigBuffer:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: _TracebackType | None,
    ):
        self._config.write_text(self._buffer, encoding="utf-8")


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


def main() -> int:
    """Main function for package.

    :return: Exit status.
    """
    parser = _Parser()
    cache_dir = _Path(_appdirs.user_cache_dir(NAME))
    config = parser.args.path / "cookiecutter.json"
    defaults = _json.loads(config.read_text(encoding="utf-8"))
    git = _Git()
    with _ConfigBuffer(config):
        for repo in parser.args.repos:
            pyproject_toml = repo / "pyproject.toml"
            git_dir = repo / ".git"
            with _ChDir(repo):
                git.stash(file=_os.devnull)

            archive_name = f"{repo.name}-{_checksumdir.dirhash(git_dir)}"
            archived_repo = cache_dir / archive_name
            metadata = _MetaData(
                _tomli.loads(pyproject_toml.read_text(encoding="utf-8"))
            )
            metadata.setentry(repo)
            defaults.update(metadata)
            config.write_text(_json.dumps(defaults), encoding="utf-8")
            if archived_repo.is_dir():
                _shutil.rmtree(archived_repo)

            _shutil.move(str(repo), archived_repo)
            _cookiecutter(
                template=str(parser.args.path),
                no_input=True,
                accept_hooks=parser.args.accept_hooks,
            )
            if git_dir.is_dir():
                _shutil.rmtree(git_dir)

            _shutil.copytree(archived_repo / ".git", git_dir)

    return 0
