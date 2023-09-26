from pydoctrace.doctrace import trace_to_component_puml, trace_to_sequence_puml
from pydoctrace.exporters.plantuml.component import PlantUMLComponentExporter
from pydoctrace.exporters.plantuml.sequence import PlantUMLSequenceExporter
from pydoctrace.tracer import ExecutionTracer

from tests.modules.factorial import factorial_recursive


def test_tracer_sequence():
    def trace_factorial_6():
        tracing_factorial_recursive = trace_to_sequence_puml(factorial_recursive)

        return tracing_factorial_recursive(6)

    with open('traced_factorial-sequence.puml', 'w', encoding='utf8') as puml_file:
        exporter = PlantUMLSequenceExporter(puml_file)
        exporter.on_header(trace_factorial_6.__module__, trace_factorial_6.__name__)

        try:
            result = ExecutionTracer(exporter).runfunc(trace_factorial_6)
            assert result == 720
        finally:
            exporter.on_footer()


def test_tracer_component():
    def trace_factorial_6():
        tracing_factorial_recursive = trace_to_component_puml(factorial_recursive)

        return tracing_factorial_recursive(6)

    with open('traced_factorial-component.puml', 'w', encoding='utf8') as puml_file:
        exporter = PlantUMLComponentExporter(puml_file)
        exporter.on_header(trace_factorial_6.__module__, trace_factorial_6.__name__)

        try:
            result = ExecutionTracer(exporter).runfunc(trace_factorial_6)
            assert result == 720
        finally:
            exporter.on_footer()
