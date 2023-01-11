repocutter
==========
.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License
.. image:: https://img.shields.io/pypi/v/repocutter
    :target: https://pypi.org/project/repocutter/
    :alt: PyPI
.. image:: https://github.com/jshwi/repocutter/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/jshwi/repocutter/actions/workflows/ci.yml
    :alt: CI
.. image:: https://results.pre-commit.ci/badge/github/jshwi/repocutter/master.svg
   :target: https://results.pre-commit.ci/latest/github/jshwi/repocutter/master
   :alt: pre-commit.ci status
.. image:: https://github.com/jshwi/repocutter/actions/workflows/codeql-analysis.yml/badge.svg
    :target: https://github.com/jshwi/repocutter/actions/workflows/codeql-analysis.yml
    :alt: CodeQL
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
.. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
    :target: https://github.com/PyCQA/pylint
    :alt: pylint
.. image:: https://snyk.io/test/github/jshwi/repocutter/badge.svg
    :target: https://snyk.io/test/github/jshwi/repocutter/badge.svg
    :alt: Known Vulnerabilities

Checkout repos to current cookiecutter config
---------------------------------------------

Checkout one or more repos to current ``cookiecutter`` config

This will make changes to local repositories, hopefully preserving their history

Ideally only the working tree will change

Ignored files should be backed up

Use with caution

Usage
-----

.. code-block:: console

    usage: repocutter [-h] [-v] [-a] PATH [REPOS [REPOS ...]]

    Checkout repos to current cookiecutter config

    positional arguments:
      PATH                pat,h to cookiecutter template dir
      REPOS               repos to run cookiecutter over

    optional arguments:
      -h, --help          show this help message and exit
      -v, --version       show program's version number and exit
      -a, --accept-hooks  accept pre/post hooks
