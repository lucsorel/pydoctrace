"""
Module dedicated to the export of sequence diagrams in the PlanUML syntax.

Bibliography:
- https://plantuml.com/en/sequence-diagram: syntax of sequence diagrams
- https://plantuml.com/en/guide, https://plantuml.com/fr/guide: the PlanUML syntax books. Pages or sections of interest:
  - 24.6 Colors: color names
- https://plantuml-documentation.readthedocs.io/en/latest/formatting/all-skin-params.html: "All skin parameters available in PlantUML in alphabetical order."
"""

from string import Formatter
from typing import Any

from pydoctrace.domain.execution import CallEnd, Error
from pydoctrace.exporters import Exporter
from pydoctrace.exporters.formatters import escape_dunder_with_tilde, formatter_factory, replace_arobase_by_unicode
from pydoctrace.exporters.plantuml import FOOTER_TPL

PLANTUML_SEQUENCE_FORMATTER: Formatter = formatter_factory(
    'PlantUMLSequenceFormatter', replace_arobase_by_unicode, escape_dunder_with_tilde
)

HEADER_TPL = r"""@startuml {diagram_name}
skinparam BoxPadding 10
skinparam ParticipantPadding 5
skinparam NoteBackgroundColor Cornsilk
skinparam NoteBorderColor Sienna
hide footbox
"""

TRACING_START_TPL = r"""
[o-> "{called.fq_module_text:dunder}\n{called.function_name:dunder}"
note right: line {called.line_index}
"""

CALL_START_TPL = r"""
"{caller.fq_module_text:dunder}\n{caller.function_name:dunder}" -> "{called.fq_module_text:dunder}\n{called.function_name:dunder}" ++
note left: line {caller.line_index}
note right: line {called.line_index}
"""

CALL_END_TPL = r"""
return {arg:dunder}
note right: line {called.line_index}
|||
"""

ERROR_PROPAGATION_TPL = r"""
"{error_caller.fq_module_text:dunder}\n{error_caller.function_name:dunder}" o<--x "{error_called.fq_module_text:dunder}\n{error_called.function_name:dunder}": ""{error.class_name}""\n{error.message}
deactivate "{error_called.fq_module_text:dunder}\n{error_called.function_name:dunder}"
note right: line {error_called.line_index}
note left: line {error_caller.line_index}
"""

TRACING_END_TPL = r"""
[<-- "{called.fq_module_text:dunder}\n{called.function_name:dunder}": {arg:dunder}
note right: line {called.line_index}
"""

UNHANDLED_ERROR_END_TPL = r"""
[<-->x "{called.fq_module_text:dunder}\n{called.function_name:dunder}": ""{error.class_name}""\n{error.message}
note right: line {called.line_index}
"""


class PlantUMLSequenceExporter(Exporter):
    """
    Exports the sequence diagram in the PlantUML format.

    The nature of the sequence diagram and the corresponding PlantUML syntax
    allows to produce the diagram contents as the execution goes, in a
    streaming fashion.

    For efficiency reasons, instances of the execution domain model are used
    directly without converting them into diagram model instances.
    """

    fmt: Formatter = PLANTUML_SEQUENCE_FORMATTER

    def on_header(self, start_module: str, start_func_name: str):
        diagram_name = f'{start_module}.{start_func_name}-sequence'
        self.io_sink.write(self.fmt.format(HEADER_TPL, diagram_name=diagram_name))

    def on_tracing_start(self, called: CallEnd):
        self.io_sink.write(self.fmt.format(TRACING_START_TPL, called=called))

    def on_start_call(self, caller: CallEnd, called: CallEnd):
        self.io_sink.write(self.fmt.format(CALL_START_TPL, caller=caller, called=called))

    def format_arg_value(self, arg: Any) -> Any:
        if arg is None:
            return ''
        return arg

    def on_error_propagation(self, error_called: CallEnd, error_caller: CallEnd, error: Error):
        self.io_sink.write(
            self.fmt.format(ERROR_PROPAGATION_TPL, error_called=error_called, error_caller=error_caller, error=error)
        )

    def on_return(self, *, called: CallEnd, arg: Any, **kwargs):
        self.io_sink.write(self.fmt.format(CALL_END_TPL, called=called, arg=self.format_arg_value(arg)))

    def on_tracing_end(self, called: CallEnd, arg: Any):
        self.io_sink.write(self.fmt.format(TRACING_END_TPL, called=called, arg=self.format_arg_value(arg)))

    def on_unhandled_error_end(self, called: CallEnd, error: Error):
        self.io_sink.write(self.fmt.format(UNHANDLED_ERROR_END_TPL, called=called, error=error))

    def on_footer(self):
        self.io_sink.write(FOOTER_TPL)
