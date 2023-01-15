from collections import deque
from pathlib import Path
from sys import settrace
from typing import Any, Callable, List

from pydoctrace.domain.sequence import Call
from pydoctrace.exporters import Exporter

# frame
# - why:
#   - 'call' ->
#     - module (frame.__file__ -> clé de cache, déduire le module à partir de celui de la fonction décorée), function name
#     - fonction (frame.code)
#     - n° de ligne (frame.line)
#     - arg a l'air d'être toujours None
#     -> renvoie la fonction qui va analyser les instructions de l'appel en cours
#   - 'line' ->
#     - module, fonction
#     - arg toujours None
#   - 'return'
#     - module, fonction
#     - arg valué si return explicite; None sinon
#   - 'exception'
#     -> à tester et à gérer

# idée complémentaire : dessiner un diagramme de modules avec des liens entre les fonctions qui s'appellent les unes les autres
# -> https://plantuml.com/fr/activity-diagram-beta § Regroupement ou partition
# -> https://plantuml.com/fr/deployment-diagram avec des components ou packages pour les modules


def module_name_from_filepath(script_filepath: str) -> str:
    '''Return a plausible module name for the script_filepath.'''
    # base = os.path.basename(script_filepath)
    # filename, _ = os.path.splitext(base)
    # return filename
    return None if script_filepath is None else Path(script_filepath).stem


class SequenceTracer:
    '''
    Traces the execution of a callable object and pushes events to the given exporter.
    '''
    def __init__(self, exporter: Exporter):
        self.exporter = exporter
        self.callers_stack: List[Call] = deque()

    def runfunc(self, func: Callable, *args, **kwargs) -> Any:
        '''
        Runs the given function with the given positional and keyword arguments and traces the calls sequence.
        '''

        # ensures that a callable object has been passed
        if func is None or not callable(func):
            raise ValueError('A function or a callable object must be passed to trace its execution')

        # declares the tracing callbacks to trace calls, performs and traces the call, then removes the tracer
        settrace(self.globaltrace)
        try:
            return func(*args, **kwargs)
        finally:
            settrace(None)

    def globaltrace(self, frame, why: str, arg: Any):
        '''
        Handler for call events.

        Returns:
        - a custom tracing function to trace the execution of the block
        - None if the execution block should be ignored
        '''

        if why == 'call':
            # constructs the call
            fq_module_text: str = frame.f_globals.get('__name__', None)
            if fq_module_text is None:
                fq_module_text = module_name_from_filepath(frame.f_globals.get('__file__', None))
            line_index = frame.f_lineno
            function_name = frame.f_code.co_name
            call = Call(fq_module_text, tuple(fq_module_text.split('.')), function_name, line_index)

            # starts the tracing or handle an intermediary call
            if len(self.callers_stack) == 0:
                self.exporter.write_tracing_start(call)
            else:
                self.exporter.write_start_call(self.callers_stack[-1]._replace(line_index=frame.f_lineno), call)

            # adds the call to the calls stack and returns the call tracing function to detect 'return' events
            self.callers_stack.append(call)

            return self.localtrace

    def localtrace(self, frame, why: str, arg: Any):
        '''
        Handler for events happening within a call:
        - 'return' event: ends the current call, removes it from the callers stack
        '''
        if why == 'return':
            # end of the block code: removes the last caller from the stack
            called_end = self.callers_stack.pop()._replace(line_index=frame.f_lineno)
            if len(self.callers_stack) == 0:
                self.exporter.write_tracing_end(called_end, arg)
            else:
                self.exporter.write_return(called_end, arg)

        return self.localtrace
