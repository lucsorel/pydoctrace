from pydoctrace.doctrace import trace_to_sequence_puml

from tests.modules.ecoindex import ecoindex


def test_trace_to_sequence_puml():
    decorated_ecoindex = trace_to_sequence_puml(ecoindex)
    ecoindex_score = decorated_ecoindex(dom_elements_nb=960, requests_nb=70, size_kb=1500)

    assert abs(ecoindex_score - 41.234) < 0.001
