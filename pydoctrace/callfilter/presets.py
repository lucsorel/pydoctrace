from sys import builtin_module_names, version_info
from typing import Callable, NamedTuple, Optional, Tuple

# the type alias for an exclusion or an inclusion filter. It is a callable taking the following parameters
# and returning a boolean value:
# - Tuple[str]: represents the module fully-qualified name holding the function
# - str: the function name
# - int: the call depth, incremented when a function calls another function, decremented when a function call returns
Filter = Callable[[Tuple[str], str, int], bool]


class Preset(NamedTuple):
    """
    Represents a set of two rules, each one being a function:
    - exclude_call should return True to exclude the call from the tracing process, False to trace it
    - include_call is optional and called only if exclude_call returned True, and is expected to return
      True to force the tracing anyway; thus offering some inclusion exceptions to the exclusion rule

    The typical use-case is to exclude the call to all the functions of a given module in exclude_call,
    then to allow the call to some functions in include_call.

    Note: exclude_call must not be None, include_call can be None if the preset offers no exception rule.
    """

    exclude_call: Filter
    include_call: Optional[Filter] = None


# excludes calls to functions that are in the built-in modules
EXCLUDE_BUILTINS_PRESET = Preset(
    exclude_call=lambda module_parts, *args: len(module_parts) > 0 and module_parts[0] in builtin_module_names
)

# excludes calls to functions that are in the standard library modules (builtins and more, like datetime)
# note: it is based on sys.stdlib_module_names, which appeared in Python 3.10
if version_info.major >= 3 and version_info.minor >= 10:
    from sys import stdlib_module_names
else:
    # list of module names of the Python 3.10 standard library. Some native modules of the previous versions of the
    # standard library may be missing
    stdlib_module_names = (
        '__future__', '_abc', '_aix_support', '_ast', '_asyncio', '_bisect', '_blake2', '_bootsubprocess', '_bz2',
        '_codecs', '_codecs_cn', '_codecs_hk', '_codecs_iso2022', '_codecs_jp', '_codecs_kr', '_codecs_tw',
        '_collections', '_collections_abc', '_compat_pickle', '_compression', '_contextvars', '_crypt', '_csv',
        '_ctypes', '_curses', '_curses_panel', '_datetime', '_dbm', '_decimal', '_elementtree', '_frozen_importlib',
        '_frozen_importlib_external', '_functools', '_gdbm', '_hashlib', '_heapq', '_imp', '_io', '_json', '_locale',
        '_lsprof', '_lzma', '_markupbase', '_md5', '_msi', '_multibytecodec', '_multiprocessing', '_opcode',
        '_operator', '_osx_support', '_overlapped', '_pickle', '_posixshmem', '_posixsubprocess', '_py_abc',
        '_pydecimal', '_pyio', '_queue', '_random', '_scproxy', '_sha1', '_sha256', '_sha3', '_sha512', '_signal',
        '_sitebuiltins', '_socket', '_sqlite3', '_sre', '_ssl', '_stat', '_statistics', '_string', '_strptime',
        '_struct', '_symtable', '_thread', '_threading_local', '_tkinter', '_tokenize', '_tracemalloc', '_typing',
        '_uuid', '_warnings', '_weakref', '_weakrefset', '_winapi', '_zoneinfo', 'abc', 'aifc', 'antigravity',
        'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore', 'atexit', 'audioop', 'base64', 'bdb', 'binascii',
        'bisect', 'builtins', 'bz2', 'cProfile', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs',
        'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser', 'contextlib', 'contextvars',
        'copy', 'copyreg', 'crypt', 'csv', 'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib',
        'dis', 'distutils', 'doctest', 'email', 'encodings', 'ensurepip', 'enum', 'errno', 'faulthandler', 'fcntl',
        'filecmp', 'fileinput', 'fnmatch', 'fractions', 'ftplib', 'functools', 'gc', 'genericpath', 'getopt', 'getpass',
        'gettext', 'glob', 'graphlib', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'idlelib', 'imaplib',
        'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3',
        'linecache', 'locale', 'logging', 'lzma', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap',
        'modulefinder', 'msilib', 'msvcrt', 'multiprocessing', 'netrc', 'nis', 'nntplib', 'nt', 'ntpath', 'nturl2path',
        'numbers', 'opcode', 'operator', 'optparse', 'os', 'ossaudiodev', 'pathlib', 'pdb', 'pickle', 'pickletools',
        'pipes', 'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats',
        'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'pydoc_data', 'pyexpat', 'queue', 'quopri', 'random', 're',
        'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve',
        'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd', 'sqlite3',
        'sre_compile', 'sre_constants', 'sre_parse', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct',
        'subprocess', 'sunau', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile',
        'termios', 'textwrap', 'this', 'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize', 'tomllib',
        'trace', 'traceback', 'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing', 'unicodedata',
        'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'winreg', 'winsound',
        'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib', 'zoneinfo',
    )  # fmt: skip

EXCLUDE_STDLIB_PRESET = Preset(
    exclude_call=lambda module_parts, *args: len(module_parts) > 0 and module_parts[0] in stdlib_module_names
)

EXCLUDE_TESTS_PRESET = Preset(
    exclude_call=lambda module_parts, *args: len(module_parts) > 0
    and module_parts[0] in ('tests', '_pytest', 'pytest', 'unittest', 'doctest')
)


def _depth_preset_factory(depth_threshold: int) -> Preset:
    """
    Low-level factory function producing a preset that excludes calls from tracing
    when the call depth is equal or above the given threshold of the calls stack.
    """
    if (depth_threshold is None) or not isinstance(depth_threshold, int):
        raise TypeError('depth threshold must be an integer')
    if depth_threshold < 0:
        raise ValueError(f"depth threshold must be a positive integer, got '{depth_threshold}'")

    return Preset(exclude_call=lambda module_parts, function_name, call_depth: call_depth > depth_threshold)


# exposes the low-level preset factory as an upper-case callable, for the sake of homogeneity with other default presets
EXCLUDE_CALL_DEPTH_PRESET_FACTORY = _depth_preset_factory

# excludes calls whose depth in the calls stack is below (greater than) 5
EXCLUDE_DEPTH_BELOW_5_PRESET = EXCLUDE_CALL_DEPTH_PRESET_FACTORY(5)
