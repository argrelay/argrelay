########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is a custom build script *sourced* by `@/exe/bootstrap_dev_env.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, the build scripts like this for integration project should build it and test it.

# Not running `tox` as it expects all Python versions present
# within the environment while CI environments may have only one of
# the Python versions per runner (each runner runs with its own
# Python version, not all) and we are not selecting them
# for `tox` conditionally.
# Instead, run some selected tests which do not need extra dependencies
# (e.g. do not run `gui_tests`):
# TODO: Re-group tests to exculde trully online (going to Interne, but do not exclude end to end, for example):
for test_group in \
offline_tests \
release_tests \
slow_tests \

do
    ./exe/dev_shell.bash ./exe/run_max_tests.bash ./tests/"${test_group}"
done

########################################################################################################################
