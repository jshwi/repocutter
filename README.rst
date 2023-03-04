repocutter
==========
.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License
.. image:: https://img.shields.io/pypi/v/repocutter
    :target: https://pypi.org/project/repocutter/
    :alt: PyPI
.. image:: https://github.com/jshwi/repocutter/actions/workflows/build.yaml/badge.svg
    :target: https://github.com/jshwi/repocutter/actions/workflows/build.yaml
    :alt: Build
.. image:: https://github.com/jshwi/repocutter/actions/workflows/codeql-analysis.yml/badge.svg
    :target: https://github.com/jshwi/repocutter/actions/workflows/codeql-analysis.yml
    :alt: CodeQL
.. image:: https://results.pre-commit.ci/badge/github/jshwi/repocutter/master.svg
   :target: https://results.pre-commit.ci/latest/github/jshwi/repocutter/master
   :alt: pre-commit.ci status
.. image:: https://codecov.io/gh/jshwi/repocutter/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jshwi/repocutter
    :alt: codecov.io
.. image:: https://readthedocs.org/projects/repocutter/badge/?version=latest
    :target: https://repocutter.readthedocs.io/en/latest/?badge=latest
    :alt: readthedocs.org
.. image:: https://img.shields.io/badge/python-3.8-blue.svg
    :target: https://www.python.org/downloads/release/python-380
    :alt: python3.8
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Black
.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
    :target: https://pycqa.github.io/isort/
    :alt: isort
.. image:: https://img.shields.io/badge/%20formatter-docformatter-fedcba.svg
    :target: https://github.com/PyCQA/docformatter
    :alt: docformatter
.. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
    :target: https://github.com/PyCQA/pylint
    :alt: pylint
.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
    :alt: Security Status
.. image:: https://snyk.io/test/github/jshwi/repocutter/badge.svg
    :target: https://snyk.io/test/github/jshwi/repocutter/badge.svg
    :alt: Known Vulnerabilities
.. image:: https://snyk.io/advisor/python/repocutter/badge.svg
  :target: https://snyk.io/advisor/python/repocutter
  :alt: repocutter

Checkout repos to current cookiecutter config
---------------------------------------------

Checkout one or more repos to current `cookiecutter <https://github.com/cookiecutter/cookiecutter>`_ config

This will make changes to local repositories, hopefully preserving their history

Ideally only the working tree will change

Ignored files should be backed up

Use with caution

Usage
-----

.. code-block:: console

    usage: repocutter [-h] [-v] [-a] [-c] [-b REV,NEW] [-i LIST] PATH [REPOS [REPOS ...]]

    Checkout repos to current cookiecutter config

    positional arguments:
      PATH                          path to cookiecutter template dir
      REPOS                         repos to run cookiecutter over

    optional arguments:
      -h, --help                    show this help message and exit
      -v, --version                 show program's version number and exit
      -a, --accept-hooks            accept pre/post hooks
      -c, --gc                      clean up backups from previous runs
      -b REV,NEW, --branch REV,NEW  checkout new branch from existing revision
      -i LIST, --ignore LIST        comma separated list of paths to ignore, cookiecutter vars are allowed

Configuration
-------------

Currently only written for a configuration exactly like below

Technically a repo would not need to be a `poetry <https://github.com/python-poetry/poetry>`_ project if the below section exists within its pyproject.toml file

This is the only use case at this time (If there are any other configurations you would like added please leave an `issue <https://github.com/jshwi/repocutter/issues>`_)

Each repository's pyproject.toml file will be parsed for data to recreate its working tree

A ``poetry`` section in the project's pyproject.toml file that looks like the following...

.. code-block:: toml

    [tool.poetry]
    description = "Checkout repos to current cookiecutter config"
    keywords = [
      "config",
      "cookiecutter",
      "jinja2",
      "repo",
      "template"
    ]
    name = "repocutter"
    version = "0.2.0"

...will temporarily write to the ``cookiecutter`` project's cookiecutter.json file until the repo is created

.. code-block:: json

    {
      "project_name": "repocutter",
      "project_version": "0.2.0",
      "project_description": "Checkout repos to current cookiecutter config",
      "project_keywords": "config,cookiecutter,jinja2,repo,template",
    }

The above configuration will reduce the diff, but it will still work if your config is not exactly the same

Why?
----
As time goes on, and you use ``cookiecutter`` for new projects, you will make more and more changes to your ``cookiecutter`` repo

You will find these new project layouts are preferable to your older, more outdated, projects

If you have a project layout configured with ``cookiecutter`` then it's likely you will want this layout for all your projects

Configuring your existing projects manually is even more tedious than configuring a new project manually, especially if you have a lot of them

By checking out your projects to your configured ``cookiecutter`` layout, you can use whatever diff tool you use to rollback any undesired changes
