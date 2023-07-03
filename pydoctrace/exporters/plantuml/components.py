'''
Module dedicated to the export of package diagrams in the PlanUML syntax.

Bibliography:
- FIXME https://plantuml.com/fr/sequence-diagram: syntax of package diagrams
- https://plantuml.com/en/guide, https://plantuml.com/fr/guide: the PlanUML syntax books. Pages or sections of interest:
  - 24.6 Colors: color names
- https://plantuml-documentation.readthedocs.io/en/latest/formatting/all-skin-params.html: "All skin parameters available in PlantUML in alphabetical order."
'''

from dataclasses import dataclass, field
from io import TextIOBase
from typing import Any, List, Tuple

from pydoctrace.exporters import Exporter
from pydoctrace.exporters.plantuml import PlantUMLEscapeFormatter

HEADER_TPL = r'''@startuml {diagram_name}
skinparam BoxPadding 10
skinparam NoteBackgroundColor Cornsilk
skinparam NoteBorderColor Sienna
'''

FOOTER_TPL = r'''
footer Generated by //pydoctrace//
@enduml
'''


@dataclass
class Function:
    name: str
    module_path: Tuple[str]


@dataclass
class Module:
    sub_modules: List['Module'] = field(default_factory=list)
    functions: List[Function] = field(default_factory=list)


@dataclass
class Call:
    caller: Function
    callee: Function


@dataclass
class Error:
    ...


class PlantUMLComponentsExporter(Exporter):
    '''
    Exports the components diagram in the PlantUML format.
    '''

    fmt: PlantUMLEscapeFormatter = PlantUMLEscapeFormatter()

    def __init__(self, io_sink: TextIOBase):
        super().__init__(io_sink)

    def on_header(self, start_module: str, start_func_name: str):
        diagram_name = f'{start_module}.{start_func_name}-package'
        self.io_sink.write(self.fmt.format(HEADER_TPL, diagram_name=diagram_name))

    def on_tracing_start(self, called: Call):
        ...
        # self.io_sink.write(self.fmt.format(TRACING_START_TPL, called=called))

    def on_start_call(self, caller: Call, called: Call):
        ...
        # self.io_sink.write(self.fmt.format(CALL_START_TPL, caller=caller, called=called))

    def format_arg_value(self, arg: Any) -> str:
        if arg is None:
            return ''
        return arg

    def on_error_propagation(self, error_called: Call, error_caller: Call, error: Error):
        ...
        # self.io_sink.write(
        #     self.fmt.format(ERROR_PROPAGATION_TPL, error_called=error_called, error_caller=error_caller, error=error)
        # )

    def on_return(self, called: Call, arg: Any, **kwargs):
        ...
        # self.io_sink.write(self.fmt.format(CALL_END_TPL, called=called, arg=self.format_arg_value(arg)))

    def on_tracing_end(self, called: Call, arg: Any):
        ...
        # self.io_sink.write(self.fmt.format(TRACING_END_TPL, called=called, arg=self.format_arg_value(arg)))

    def on_unhandled_error_end(self, called: Call, error: Error):
        ...
        # self.io_sink.write(self.fmt.format(UNHANDLED_ERROR_END_TPL, called=called, error=error))

    def on_footer(self):
        self.io_sink.write(FOOTER_TPL)