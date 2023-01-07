from contextlib import redirect_stdout
from io import StringIO
from trace import Trace

from tests.doctrace.test_ecoindex import ecoindex


def test_doc_tracing():
    output_string_io = StringIO()
    with redirect_stdout(output_string_io):
        tracer = Trace(count=False)
        results = tracer.runfunc(ecoindex, dom_elements_nb=960, requests_nb=70, size_kb=1500)

    print(f'{results=}')
    # print(f'{output_string_io.getvalue()=}')
    output_string_io.seek(0)
    for trace in output_string_io.readlines():
        print(f'{trace=}')
    assert False
