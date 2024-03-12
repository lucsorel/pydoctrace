from pydoctrace.doctrace import trace_to_component_puml

from tests.integrations.classes.namedtuple import main_named_tuple


def test_doctrace_classes_namedtuple_component():
    traceable_main = trace_to_component_puml(filter_presets=())(main_named_tuple)

    assert traceable_main() == 'Suzie Q'
