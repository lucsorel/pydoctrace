from collections import deque
from pathlib import Path
from sys import settrace
from typing import List

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
    def __init__(self, exporter: Exporter):
        self.exporter = exporter
        self.callers_stack: List[Call] = deque()

    def runfunc(self, func, *args, **kwargs):
        if func is None:
            raise ValueError('No function was given, nothing to execute not to trace')

        result = None
        # declares the tracing callbacks to handle calls
        settrace(self.globaltrace)
        try:
            result = func(*args, **kwargs)
        finally:
            settrace(None)
        return result

    def should_ignore(self, *args):
        return False

    def globaltrace(self, frame, why: str, arg):
        '''
        Handler for call events.

        Returns:
        - a custom tracing function to trace the execution of the block
        - None if the execution block should be ignored
        '''

        # self.exporter.write_raw_content(f"' g {frame=}\n")

        if why == 'call':
            # constructs the call
            fq_module_text: str = frame.f_globals.get('__name__', None)
            if fq_module_text is None:
                fq_module_text = module_name_from_filepath(frame.f_globals.get('__file__', None))
            line_index = frame.f_lineno
            function_name = frame.f_code.co_name
            call = Call(fq_module_text, tuple(fq_module_text.split('.')), function_name, line_index)

            if len(self.callers_stack) == 0:
                self.exporter.write_tracing_start(call)
            else:
                self.exporter.write_start_call(self.callers_stack[-1]._replace(line_index=frame.f_lineno), call)
            self.callers_stack.append(call)

            return self.localtrace

    def localtrace(self, frame, why, arg):
        if why == 'return':
            # end of the block code: removes the last caller from the stack
            called_end = self.callers_stack.pop()._replace(line_index=frame.f_lineno)
            if len(self.callers_stack) == 0:
                self.exporter.write_tracing_end(called_end, arg)
            else:
                self.exporter.write_return(called_end, arg)

        return self.localtrace
