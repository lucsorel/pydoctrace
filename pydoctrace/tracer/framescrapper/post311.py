from types import FrameType


class FrameScrapperPostPy311:
    """
    Uses frame and associated code objects to scrap the full domain and name of
    a called block of code.
    """

    def scrap_callable_domain_and_name(self, called_frame: FrameType) -> str:
        callable_code = called_frame.f_code
        callable_name = callable_code.co_qualname

        # special case for named tuple instantiation
        if (
            called_frame.f_globals.get('_tuple_new') is not None
            and (namedtuple_class := called_frame.f_locals.get('_cls')) is not None
        ):
            return f'{namedtuple_class.__module__}.{callable_name}'

        fq_module_text: str = called_frame.f_globals.get('__name__', None)
        return f'{fq_module_text}.{callable_name}'
