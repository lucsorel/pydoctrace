from typing import Iterable, Tuple

from pydoctrace.callfilter.presets import EXCLUDE_STDLIB_PRESET, Preset


class CallFilter:
    """
    Offers the possibility to exclude a call from the tracing process to make the diagram more concise.

    The method should_trace_call tells whether the call should be traced. The filter internally uses presets
    to help the user define exclusion rules. A preset gives the possibility to express large-grain exclusion rules
    with fine-grain inclusion rules.
    """

    def __init__(self, presets: Iterable[Preset]):
        self.presets: Tuple[Preset] = tuple(presets)

    def should_trace_call(self, module_parts: Tuple[str], function_name: str, call_depth: int) -> bool:
        """
        Iterates over the presets until one excludes the call:
        - once a preset excludes the call, the filter stops iterating over the presets
        - if no exclusion preset is found, the call should be traced
        """
        call_excluded = any(
            (
                # the call is excluded by the exclusion rule
                preset.exclude_call(module_parts, function_name, call_depth)
                and (
                    # no exception rule is set to include the call
                    preset.include_call is None
                    or
                    # the exception rule does not include the call
                    not preset.include_call(module_parts, function_name, call_depth)
                )
                for preset in self.presets
            )
        )

        return not call_excluded


class TraceAll(CallFilter):
    """
    A light-weight implementation which filters nothing out (traces everything).
    """

    def __init__(self):
        """
        Initializes the parent class with an emtpy tuple of filtering presets
        """
        super().__init__(())

    def should_trace_call(self, module_parts: Tuple[str], function_name: str, call_depth: int) -> bool:
        return True


# singleton instance
TRACE_ALL_FILTER = TraceAll()


class TraceNone(CallFilter):
    """
    A light-weight implementation which filters everything out (traces nothing).
    """

    def __init__(self):
        """
        Initializes the parent class with an emtpy tuple of filtering presets
        """
        super().__init__(())

    def should_trace_call(self, module_parts: Tuple[str], function_name: str, call_depth: int) -> bool:
        return False


# singleton instance
TRACE_NONE_FILTER = TraceNone()


def call_filter_factory(filter_presets: Iterable[Preset]) -> CallFilter:
    """
    Utility function returning an instance of CallFilter ready to be used by the tracer,
    from the given list of presets.
    """
    if filter_presets is None or len(filter_presets) == 0:
        return TRACE_ALL_FILTER
    else:
        return CallFilter(filter_presets)


FILTER_OUT_STDLIB = call_filter_factory((EXCLUDE_STDLIB_PRESET,))
