from pydoctrace.doctrace import trace_to_component_puml

from tests.integrations.classes import Person, main


def test_doctrace_classes_component():
    traceable_main = trace_to_component_puml(filter_presets=())(main)

    assert traceable_main() == Person('Suzie', 'Q')
