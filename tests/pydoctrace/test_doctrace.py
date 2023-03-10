from pydoctrace.doctrace import trace_to_puml
from pydoctrace.exporters.plantuml import PlantUMLExporter
from pydoctrace.tracer import SequenceTracer

from tests.modules.factorial import factorial_recursive


def test_tracer_sequence():
    def trace_factorial():
        tracing_factorial_recursive = trace_to_puml(factorial_recursive)

        assert tracing_factorial_recursive(6) == 720

    with open('traced_factorial.puml', 'w', encoding='utf8') as puml_file:
        exporter = PlantUMLExporter(puml_file)
        exporter.write_header(getattr(trace_factorial, '__module__'), getattr(trace_factorial, '__name__'))

        SequenceTracer(exporter)
        try:
            SequenceTracer(exporter).runfunc(trace_factorial)
        finally:
            exporter.write_footer()
