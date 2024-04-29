from inspect import getmembers, isclass, isfunction
from types import FrameType
from typing import Iterator


class FrameScrapperBeforePy311:
    """
    Uses frame and associated code objects to scrap the full domain and name of
    a called block of code.
    """

    def _is_class_or_function(self, entry: object):
        return isclass(entry) or isfunction(entry)

    def _iter_over_type_namespaces(self, namespace: dict, function_code, *, parsed_types: set) -> Iterator[str]:
        """
        Looks for the function of the method corresponding to the given code in the classes of the globals.
        - namespace is either the globals of a module or the members of a class
        """
        for entry in namespace.values():
            if getattr(entry, '__code__', None) == function_code:
                yield f'{entry.__module__}.{entry.__qualname__}'

            # check for methods and nested classes (avoid infinite loop once root type is reached)
            if isclass(entry) and (entry != type) and (entry not in parsed_types):
                # add the class to the set to avoid analyzing the entry again (like parent<->child cycles)
                parsed_types.add(entry)

                yield from self._iter_over_type_namespaces(
                    dict(getmembers(entry, predicate=self._is_class_or_function)),
                    function_code,
                    parsed_types=parsed_types,
                )

    def scrap_callable_domain_and_name(self, called_frame: FrameType) -> str:
        callable_code = called_frame.f_code
        callable_name = callable_code.co_name

        # special case for named tuple instantiation
        if (
            called_frame.f_globals.get('_tuple_new') is not None
            and (namedtuple_class := called_frame.f_locals.get('_cls')) is not None
        ):
            return f'{namedtuple_class.__module__}.{namedtuple_class.__qualname__}.{callable_name}'

        # searches for the function name and code in the globals of the calling frame
        # TODO searches in the builtins for speed sake? Or is it already done here?
        calling_frame = called_frame.f_back
        calling_frame_globals = calling_frame.f_globals
        if (function_candidate := calling_frame_globals.get(callable_name)) is not None and (
            getattr(function_candidate, '__code__', None) == callable_code
        ):
            return f'{function_candidate.__module__}.{function_candidate.__qualname__}'

        # searches the function in the methods of the local variables in the calling frame
        calling_frame_locals = calling_frame.f_locals
        for entry in calling_frame_locals.values():
            # FIXME the entry could already be a class passed as a parameter
            if (method_candidate := getattr(entry.__class__, callable_name, None)) is not None and (
                getattr(method_candidate, '__code__', None) == callable_code
            ):
                # the callable was defined in the module that defined the class where the matching code was found
                if method_candidate.__module__ == entry.__class__.__module__:
                    return f'{method_candidate.__module__}.{method_candidate.__qualname__}'
                # the callable was defined in another module, which happens for NamedTuple classes (my_names_tuple._replace(), for example)
                else:
                    # TODO this works for namedtuple._replace and ._make but maybe not for inherited methods?
                    return f'{method_candidate.__module__}.{callable_name}'

        # searches the method call in the calling frame's globals otherwise
        calling_globals = {**calling_frame_globals, '__doc__': None, '__builtins__': None}
        callable_domain_and_name = next(
            self._iter_over_type_namespaces(calling_globals, callable_code, parsed_types=set()), None
        )
        if callable_domain_and_name is not None:
            return callable_domain_and_name

        # default
        callable_domain_path: str = called_frame.f_globals.get('__name__', None)
        return f'{callable_domain_path}.{callable_name}'
