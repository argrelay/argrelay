from argrelay.plugin_delegator.DelegatorAbstract import DelegatorAbstract


class DelegatorSingleFuncAbstract(DelegatorAbstract):
    """
    This is a base delegator which implements single func.

    Unlike this (single func) class, its base `DelegatorAbstract` is potentially responsible for
    multiple funcs which is a bad pattern leading to complex logic (to handle each func differently)
    without separation of concerns.

    TODO: TODO_06_54_83_58: extend via func instead of delegator:
          Provide list of common functionality for all 1-to-1 dedicated delegators.
          For example:
          *   Each dedicated delegator should override `get_single_func_id()` which defines func it implements.
              NOTE: Some special funcs (e.g. `intercept`, `help`, ...) define `single_func_id` in their config -
              maybe this should be combined? The question is whether to exposed `single_func_id` via config or
              hide in code (as `get_single_func_id()`). Exposing via config allows matching delegator configs
              against `composite_tree` configs, but adds clutter to the config.
          *   Check common `assert func_id =` and implement it here common for all.
          *   Factor out common parts of `run_invoke_control` for simple funct
              (which only populate `custom_plugin_data`).
          *   Factor out and simplify defining func `data_envelope`.
    """
