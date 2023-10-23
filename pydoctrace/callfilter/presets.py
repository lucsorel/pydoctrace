from sys import builtin_module_names, version_info
from warnings import warn

from pydoctrace.callfilter import Preset

# excludes calls to functions that are in the built-in modules
FILTER_OUT_BUILTINS = Preset(
    exclude_call=lambda module_parts, *args: len(module_parts) > 0 and module_parts[0] in builtin_module_names
)

# excludes calls to functions that are in the standard library modules (builtins and more, like datetime)
# note: it is based on sys.stdlib_module_names, which appeared in Python 3.10
if version_info.major >= 3 and version_info.minor >= 10:
    from sys import stdlib_module_names
    FILTER_OUT_STDLIB = Preset(
        exclude_call=lambda module_parts, *args: len(module_parts) > 0 and module_parts[0] in stdlib_module_names
    )
else:
    fall_back_message = ''.join(
        [
            'Cannot filter out calls happening in the standard library, ',
            'the feature is available only since Python 3.10.\n',
            'FILTER_OUT_STDLIB preset will fall back to FILTER_OUT_BUILTINS ',
            '(filters out calls done in the built-in functions).',
        ]
    )
    warn(fall_back_message, stacklevel=1)
    FILTER_OUT_STDLIB = FILTER_OUT_BUILTINS

FILTER_OUT_TESTS = Preset(
    exclude_call=lambda module_parts, *args: len(module_parts) > 0 and module_parts[0] in
    ('tests', 'pytest', 'unittest', 'doctest')
)
