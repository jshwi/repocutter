<!--
This file is auto-generated and any changes made to it will be overwritten
-->
# tests

## tests._test


### Main already cached

Test `repocutter.main` when the same repo is already saved.


### Main avoid pre commit unstaged error

Test `repocutter.main` and checking out with pre-commit config.


### Main checkout branch

Test `repocutter.main` when checking out branches.


### Main checkout branch fail

Test `repocutter.main` when checking out branches.


### Main ctrl c

Test `repocutter.main` with SIGINT.


### Main entry point

Test `repocutter.main` with entry point.


### Main exit status

Test `repocutter.main`.

Test successful exit status.

Test config correctly written.

Test success output.


### Main gc

Test `repocutter.main` with `-c/--gc`.


### Main ignore path

Test `repocutter.main` and `-i/--ignore` argument.


### Main interpolate var

Test `repocutter.main` with vars defined in json.

Confirm that interpolated string is reset between looping, as if
variable is simply overridden, the config will hold the interpolated
var from the previous run.

Position of defaults and the addition of a read only and write only
config solves this problem.


### Main no dir

Test `repocutter.main` skipping of non-existing dir.


### Main no head

Test `repocutter.main` when no HEAD to checkout.


### Main no make repos

Test `repocutter.main` skipping of non-repository.


### Main no pyproject

Test `repocutter.main` skipping of repos without pyproject.


### Main post hook git

Test `repocutter.main` with a post gen hook that inits repo.


### Version

Test `repocutter.__version__`.


