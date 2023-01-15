from typing import NamedTuple, Type

from pydoctrace.exporters import Exporter


class Context(NamedTuple):
    '''
    Stores information about the tracing process.
    It is used to pass information between the trace parser and the diagram exporter.
    '''
    exporter_class: Type[Exporter]
    export_file_path: str
    start_module: str
    start_function_name: str
