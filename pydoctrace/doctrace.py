from contextlib import contextmanager
from functools import wraps
from string import Template
from typing import Callable, Iterable, Iterator, Type

from pydoctrace.callfilter import Preset
from pydoctrace.callfilter.presets import FILTER_OUT_STDLIB, FILTER_OUT_TESTS
from pydoctrace.exporters import Context, Exporter
from pydoctrace.exporters.plantuml.component import PlantUMLComponentExporter
from pydoctrace.exporters.plantuml.sequence import PlantUMLSequenceExporter
from pydoctrace.tracer import ExecutionTracer

# default filters used to remove calls from the execution tracing
DEFAULT_FILTERS = FILTER_OUT_STDLIB, FILTER_OUT_TESTS


@contextmanager
def tracing_context_factory(context: Context) -> Iterator[ExecutionTracer]:
    with context.exporter_class.export_manager_factory(context.export_file_path) as exporter:
        # initializes the diagram file
        exporter.on_header(context.start_module, context.start_function_name)

        tracer = ExecutionTracer(exporter)
        try:
            yield tracer
        finally:
            # finalizes the sequence diagram file
            exporter.on_footer()


def context_factory(
    function_to_trace: Callable,
    exporter_class: Type[Exporter],
    export_file_path_tpl: str,
    call_filters: Iterable[Preset] = None
) -> Context:
    function_module = getattr(function_to_trace, '__module__', '__root__')
    function_name = getattr(function_to_trace, '__name__', '__main__')
    export_file_path = Template(export_file_path_tpl).safe_substitute(
        function_name=function_name, function_module=function_module
    )
    call_filters = DEFAULT_FILTERS if call_filters is None else call_filters

    return Context(exporter_class, export_file_path, function_module, function_name, call_filters)


def trace_to_sequence_puml(
    function_to_decorate: Callable = None,
    /,
    *,
    export_file_path_tpl: str = '${function_name}-sequence.puml',
    call_filters: Iterable[Preset] = None
):
    '''
    Decorates a function in order to trace its execution as a sequence diagram.
    - call_filters: enable to remove specific calls from the execution tracing. Use provided presets or design yours.
      By defaults (if None), filters out calls to the tests related modules and standard library modules.
      Set to an empty iterable to disable call filtering.

    - export_file_path_tpl: customizes the file path where the output will be written to.
      It can include placeholders like '${function_module}', '${function_name}', ${datetime_millis}'.
    '''
    def sequence_puml_decorator(function_to_trace: Callable):
        @wraps(function_to_trace)
        def traceable_func(*args, **kwargs):
            # initializes the tracing context
            context = context_factory(function_to_trace, PlantUMLSequenceExporter, export_file_path_tpl, call_filters)

            # runs the decorated function in a tracing context
            with tracing_context_factory(context) as execution_tracer:
                return execution_tracer.runfunc(function_to_trace, *args, **kwargs)

        return traceable_func

    if function_to_decorate:
        return sequence_puml_decorator(function_to_decorate)
    else:
        return sequence_puml_decorator


def trace_to_component_puml(
    function_to_decorate: Callable = None,
    /,
    *,
    export_file_path_tpl: str = '${function_name}-component.puml',
    call_filters: Iterable[Preset] = None
):
    '''
    Decorates a function in order to trace its execution as a component diagram.
    - call_filters: enable to remove specific calls from the execution tracing. Use provided presets or design yours.
      By defaults (if None), filters out calls to the tests related modules and standard library modules.
      Set to an empty iterable to disable call filtering.

    - export_file_path_tpl: customizes the file path where the output will be written to.
      It can include placeholders like '${function_module}', '${function_name}', ${datetime_millis}'.
    '''
    def component_puml_decorator(function_to_trace: Callable):
        @wraps(function_to_trace)
        def traceable_func(*args, **kwargs):
            # initializes the tracing context
            context = context_factory(function_to_trace, PlantUMLComponentExporter, export_file_path_tpl, call_filters)

            # runs the decorated function in a tracing context
            with tracing_context_factory(context) as execution_tracer:
                return execution_tracer.runfunc(function_to_trace, *args, **kwargs)

        return traceable_func

    if function_to_decorate:
        return component_puml_decorator(function_to_decorate)
    else:
        return component_puml_decorator
