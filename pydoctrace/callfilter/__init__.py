from typing import Any, Callable, Iterable, NamedTuple, Optional, Tuple

# TODO create a type alias for in·exclusion filters


class Preset(NamedTuple):
    '''
    Represents a set of two rules, each one being a function:
    - exclude_call should return True to exclude the call from the tracing process, True to trace it
    - include_call is called only if exclude_call returned True, and is expected to return True
      to force the tracing anyway (it offers some exceptions to the exclusion rule)

    The typical use-case is to exclude the call to all the functions of a given module in exclude_call,
    then to allow the call to some functions in include_call.

    Note: exclude_call must not be None, include_call can be None if the preset offers no exception rule.
    '''
    exclude_call: Callable[[Any], bool]
    include_call: Optional[Callable[[Any], bool]] = None


class CallFilter:
    '''
    Offers the possibility to exclude a call from the tracing process to make the diagrame more concise.

    The method should_trace_call tells whether the call should be traced. The filter internally uses presets
    to help the user define exclusion rules. A preset gives the possibility to express large-grain exclusion rules
    with fine-grain inclusion rules.
    '''
    def __init__(self, presets: Iterable[Preset]):
        self.presets: Tuple[Preset] = tuple(presets)

    def should_trace_call(self, module_parts: Tuple[str], function_name: str, call_depth: int) -> bool:
        '''
        Iterates over the presets until one excludes the call:
        - once a preset excludes the call, the filter stops iterating over the presets
        - if no exclusion preset is found, the call should be traced
        '''
        call_excluded = any(
            (
                # the call is excluded by the exclusion rule
                preset.exclude_call(module_parts, function_name, call_depth) and (
                    # no exception rule is set to include the call
                    preset.include_call is None or
                    # the exception rule does not include the call
                    not preset.include_call(module_parts, function_name, call_depth)
                ) for preset in self.presets
            )
        )

        return not call_excluded


class PassThrough(CallFilter):
    '''
    A light-weigth implementation which filters nothing out.
    '''
    def __init__(self):
        '''
        Initializes the parent class with an emtpy tuple
        '''
        super().__init__(())

    def should_trace_call(self, module_parts: Tuple[str], function_name: str, call_depth: int) -> bool:
        return True


# singleton instance
PASS_THROUGH = PassThrough()


def call_filter_factory(filter_presets: Iterable[Preset]) -> CallFilter:
    if filter_presets is None or len(filter_presets) == 0:
        return PASS_THROUGH
    else:
        return CallFilter(filter_presets)
