from pydoctrace.doctrace import trace_to_component_puml, trace_to_sequence_puml

from tests.modules.ecoindex import ecoindex


def test_trace_to_sequence_puml():
    decorated_ecoindex = trace_to_sequence_puml(
        export_file_path_tpl='${function_module}/${function_name}-${datetime_millis}.puml'
    )(
        ecoindex
    )
    ecoindex_score = decorated_ecoindex(dom_elements_nb=960, requests_nb=70, size_kb=1500)

    assert abs(ecoindex_score - 41.234) < 0.001


def test_trace_to_component_puml():
    decorated_ecoindex = trace_to_component_puml(
        export_file_path_tpl='${function_module}/${function_name}-${datetime_millis}.puml'
    )(
        ecoindex
    )
    ecoindex_score = decorated_ecoindex(dom_elements_nb=960, requests_nb=70, size_kb=1500)

    assert abs(ecoindex_score - 41.234) < 0.001
