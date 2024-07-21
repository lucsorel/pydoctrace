from inspect import getmembers, isclass
from re import Pattern
from re import compile as re_compile
from types import FrameType
from typing import Iterator, Tuple

REMOVE_LOCALS_PATTERN: Pattern = re_compile(r'<locals>\.')


class FrameScrapperPrePy311:
    """
    Uses frame and associated code objects to scrap the full domain and name of
    a called block of code.
    """

    def _not_yet_parsed_entries_iter(self, namespace: dict, *, parsed_types: set) -> Iterator[Tuple[str, object]]:
        for entry_name, entry in namespace.items():
            if entry is not None:
                parsed_entry_key = self._parsed_entry_key(entry)

                if parsed_entry_key not in parsed_types:
                    parsed_types.add(parsed_entry_key)
                    yield entry_name, entry

    def _parsed_entry_key(self, entry: object):
        entry_class = entry if isclass(entry) else entry.__class__
        return entry_class, id(entry)

    def _get_owner_class_metadata(self, owner) -> Tuple[str, str]:
        if owner is None:
            return None, None
        else:
            owner_class = owner if isclass(owner) else owner.__class__
            return owner_class.__module__, owner_class.__qualname__

    def _dataclass_fq_method(self, method_module: str, delocalized_method_qualname: str, owner: object) -> str:
        # the method name is the text part after the last '.'
        method_name = delocalized_method_qualname.rsplit('.', maxsplit=1)[1]

        owner_module, owner_qname = self._get_owner_class_metadata(owner)
        if method_module == owner_module:
            return f'{owner_module}.{owner_qname}.{method_name}'
        else:
            return f'{owner_module}.{method_name}'

    def _is_a_named_tuple(self, owner: object):
        if owner is None:
            return False

        owner_class = owner if isclass(owner) else owner.__class__
        return issubclass(owner_class, tuple) and hasattr(owner_class, '_asdict') and hasattr(owner_class, '_fields')

    def _namedtuple_fq_method(self, method_module: str, delocalized_method_qualname: str):
        member_name = delocalized_method_qualname.rsplit('.', maxsplit=1)[1]
        if member_name in {'_asdict', '_make', '_replace', '__repr__', '__getnewargs__'}:
            return f'collections.namedtuple.{member_name}'
        else:
            return f'{method_module}.{delocalized_method_qualname}'

    def _iter_over_type_namespaces(
        self, owner: object, owner_members: dict, function_code, *, parsed_types: set, in_locals: bool = True
    ) -> Iterator[str]:
        """
        Looks for the function of the method corresponding to the given code in the classes of the globals.
        - owner_members is either the globals of a module or the members of a class
        """
        for _, member in self._not_yet_parsed_entries_iter(owner_members, parsed_types=parsed_types):
            if getattr(member, '__code__', None) == function_code:
                # owner_module, owner_qname = self._get_owner_class_metadata(owner)
                # scope = 'locals' if in_locals else 'globals'
                # print(_, member.__module__, member.__qualname__, owner_module, owner_qname, scope, sep=';')
                # # print(f'{_=}', f'{member.__module__=}', f'{member.__qualname__=}', f'{owner_class=}', f'{owner_module=}', f'{owner_qname=}', f'{scope=}')
                delocalized_method_qualname = REMOVE_LOCALS_PATTERN.sub('', member.__qualname__)
                if delocalized_method_qualname.startswith('__create_fn__.'):
                    yield self._dataclass_fq_method(member.__module__, delocalized_method_qualname, owner)
                elif self._is_a_named_tuple(owner):
                    yield self._namedtuple_fq_method(member.__module__, delocalized_method_qualname)
                else:
                    yield f'{member.__module__}.{delocalized_method_qualname}'

            # avoid infinite loops when the member is not part of a module
            if getattr(member, '__module__', None) is not None:
                yield from self._iter_over_type_namespaces(
                    member,
                    dict(getmembers(member)),
                    function_code,
                    parsed_types=parsed_types,
                    in_locals=in_locals,
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
        calling_frame_locals = calling_frame.f_locals

        frame_locals = {**calling_frame_locals, '__doc__': None}
        callable_domain_and_name = next(
            self._iter_over_type_namespaces(None, frame_locals, callable_code, parsed_types=set()), None
        )
        if callable_domain_and_name is not None:
            return callable_domain_and_name

        # searches the method call in the calling frame's globals otherwise
        frame_globals = {**calling_frame_globals, '__doc__': None, '__builtins__': None}
        callable_domain_and_name = next(
            self._iter_over_type_namespaces(None, frame_globals, callable_code, parsed_types=set(), in_locals=False),
            None,
        )
        if callable_domain_and_name is not None:
            return callable_domain_and_name

        # default
        callable_domain_path: str = called_frame.f_globals.get('__name__', None)
        return f'{callable_domain_path}.{callable_name}'
