from pydoctrace.doctrace import trace_to_puml
from pydoctrace.exporters.plantuml import PlantUMLExporter
from pydoctrace.tracer import SequenceTracer

from tests.modules.factorial import factorial_recursive


def test_tracer_sequence():
    def trace_factorial_6():
        tracing_factorial_recursive = trace_to_puml(factorial_recursive)

        return tracing_factorial_recursive(6)

    with open('traced_factorial.puml', 'w', encoding='utf8') as puml_file:
        exporter = PlantUMLExporter(puml_file)
        exporter.write_header(getattr(trace_factorial_6, '__module__'), getattr(trace_factorial_6, '__name__'))

        SequenceTracer(exporter)
        try:
            result = SequenceTracer(exporter).runfunc(trace_factorial_6)
            assert result == 720
        finally:
            exporter.write_footer()
