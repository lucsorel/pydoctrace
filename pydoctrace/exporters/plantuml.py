from contextlib import contextmanager
from typing import Any, Iterator

from pydoctrace.domain.sequence import Call
from pydoctrace.exporters import Exporter

HEADER_TPL = '''@startuml {diagram_name}
skinparam BoxPadding 10
skinparam ParticipantPadding 5
hide footbox
'''

TRACING_START_TPL = '''
[o-> {called.function_name}
note right: line {called.line_index}
'''

CALL_START_TPL = '''
{caller.function_name} -> {called.function_name} ++
'''

CALL_END_TPL = '''
return {arg}
note right: line {called.line_index}
'''

TRACING_END_TPL = '''
[<- {called.function_name}: {arg}
note right: line {called.line_index}
'''

FOOTER_TPL = '''
@enduml
'''


class PlantUMLExporter(Exporter):
    '''
    Exports the sequence diagram in the PlantUML format.
    '''
    def write_header(self, start_module: str, start_func_name: str):
        diagram_name = f'{start_module}.{start_func_name}'
        self.io_sink.write(HEADER_TPL.format(diagram_name=diagram_name))

    def write_tracing_start(self, called: Call):
        self.io_sink.write(TRACING_START_TPL.format(called=called))

    def write_start_call(self, caller: Call, called: Call):
        self.io_sink.write(CALL_START_TPL.format(caller=caller, called=called))

    def format_arg_value(self, arg: Any) -> str:
        if arg is None:
            return ''
        return arg

    def write_return(self, called: Call, arg: Any, **kwargs):
        self.io_sink.write(CALL_END_TPL.format(called=called, arg=self.format_arg_value(arg)))

    def write_tracing_end(self, called: Call, arg: Any):
        self.io_sink.write(TRACING_END_TPL.format(called=called, arg=self.format_arg_value(arg)))

    def write_footer(self):
        self.io_sink.write(FOOTER_TPL)

    @staticmethod
    @contextmanager
    def export_manager_manager(export_file_path: str) -> Iterator[Exporter]:
        with open(export_file_path, 'w', encoding='utf8') as diagram_file:
            exporter = PlantUMLExporter(diagram_file)
            yield exporter
