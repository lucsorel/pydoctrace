'''
Module dedicated to the export of component diagrams in the PlanUML syntax.

Bibliography:
- https://plantuml.com/en/component-diagram: syntax of component diagrams
The domain modeling involves NamedTuples because they are used as dictionary keys (thus need to be hashable and immutable).
'''

from collections import defaultdict, deque
from io import TextIOBase
from itertools import count
from string import Formatter
from typing import Any, Dict, Iterable, Tuple

from pydoctrace.domain.diagram import Call, Function, Interactions, Module, Raised, Return
from pydoctrace.domain.execution import CallEnd, Error
from pydoctrace.exporters import Exporter
from pydoctrace.exporters.formatters import escape_dunder_with_tilde, formatter_factory
from pydoctrace.exporters.plantuml import FOOTER_TPL

PLANTUML_COMPONENT_FORMATTER: Formatter = formatter_factory('PlantUMLComponentFormatter', escape_dunder_with_tilde)

HEADER_TPL = r'''@startuml {diagram_name}
skinparam BoxPadding 10
skinparam componentStyle rectangle

'''

PACKAGE_OPEN_TPL = r'''{indentation}package {package_name:dunder} {{
'''

STYLED_PACKAGE_OPEN_TPL = r'''{indentation}{package_type} {package_name:dunder}{package_styling} {{
'''

PACKAGE_CLOSE_TPL = r'''{indentation}}}
'''

COMPONENT_TPL = r'''{indentation}[{function.fqn:dunder}] as "{function.name:dunder}"{stereotype}
'''

INTERACTION_CALL_TPL = r'''[{caller_function.fqn:dunder}] {arrow} [{called_function.fqn:dunder}]{arrow_label}
'''

INDENT = '  '


class ModuleStructureVisitor:
    '''
    Recursively produces the PlantUML syntax of the components structure using a visitor pattern on the root module.
    '''

    fmt: Formatter = PLANTUML_COMPONENT_FORMATTER

    def __init__(self, traced_function: Function):
        self.traced_function = traced_function

    def visit_module(self, module: Module, parent_module_path: Tuple[str], indentation_level: int) -> Iterable[str]:
        '''
        Yields the PlantUML code dedicated to package or modules.
        '''
        has_functions = len(module.functions) > 0

        # groups the module name with the parent ones if the module contains no function and only one sub-module
        if not has_functions and len(module.sub_modules) == 1:
            sub_module = list(module.sub_modules.values())[0]

            # skips the wrapping module if it has no name (root module)
            sub_module_parent_path = parent_module_path if module.name is None else parent_module_path + (module.name, )

            yield from self.visit_module(sub_module, sub_module_parent_path, indentation_level)

        # writes the parent packages if any,
        # then revisits the current module (without parents, with an increased indentation level)
        elif len(parent_module_path) > 0:
            indentation = indentation_level * INDENT

            yield self.fmt.format(PACKAGE_OPEN_TPL, indentation=indentation, package_name='.'.join(parent_module_path))

            yield from self.visit_module(module, (), indentation_level + 1)

            yield self.fmt.format(PACKAGE_CLOSE_TPL, indentation=indentation)
        # writes the module with its functions and sub-modules, or the package with sub-modules
        else:
            indentation = indentation_level * INDENT

            # opens the component
            # - special case when the root module contains more than one module: hide its contours (PlantUML rectangle)
            package_styling = ''
            if indentation_level == 0:
                package_type = 'rectangle'
                package_styling = ' #line:transparent'
            # - the component is a module if it has functions -> use a PlantUML frame representation
            elif has_functions:
                package_type = 'frame'
            # - the component is a package if it has no function -> use a PlantUML package representation
            else:
                package_type = 'package'

            yield self.fmt.format(
                STYLED_PACKAGE_OPEN_TPL,
                indentation=indentation,
                package_type=package_type,
                package_name=module.name,
                package_styling=package_styling
            )

            # declares the functions as components
            if has_functions:
                yield from self.visit_functions(module.functions.values(), indentation_level + 1)

            # visits the sub-modules
            if len(module.sub_modules) > 0:
                sub_indentation_level = indentation_level + 1
                for sub_module in module.sub_modules.values():
                    yield from self.visit_module(sub_module, (), sub_indentation_level)

            # closes the component
            yield self.fmt.format(PACKAGE_CLOSE_TPL, indentation=indentation)

    def visit_functions(self, functions: Iterable[Function], indentation_level: int) -> Iterable[str]:
        '''
        Yields the PlantUML code dedicated to the functions of a module.

        All functions are handled in the same visit because:
        - they share the same indentation, being the functions of the same module
        - the recursive visit stops here, being the branch leaves of the module hierarchy
        '''
        indentation = indentation_level * INDENT

        for function in functions:
            yield self.fmt.format(
                COMPONENT_TPL,
                indentation=indentation,
                function=function,
                stereotype=' << @trace_to_component_puml >>' if function == self.traced_function else ''
            )


class PlantUMLComponentExporter(Exporter):
    '''
    Exports the component diagram in the PlantUML format.

    The PlantUML syntax of the component diagram expects the components structure to be declared
    before the arrows of the calls. Therefore, this exporter must store all the traced calls
    before exporting the diagram in order to build the components structure from the traced calls,
    then to export the arrows representing the calls.
    '''

    fmt: Formatter = PLANTUML_COMPONENT_FORMATTER

    def __init__(self, io_sink: TextIOBase):
        super().__init__(io_sink)
        self.interactions_by_call: Dict[Tuple[Function, Function],
                                        Interactions] = defaultdict(lambda: Interactions(deque(), deque()))
        self.interaction_rank_iter = count(1, step=1)
        self.traced_function: Function = None
        self.functions: Dict[Tuple[str], Function] = {}

    def next_interaction_rank(self) -> int:
        return next(self.interaction_rank_iter)

    def function_from_call(self, caller: CallEnd) -> Function:
        '''
        Retrieves the Function from the cache, or creates it from the given Call and caches it.
        '''
        function_key = caller.fq_module_tuple + (caller.function_name, )
        function = self.functions.get(function_key)
        if function is None:
            function = Function(caller.function_name, caller.fq_module_tuple)
            self.functions[function_key] = function

        return function

    def add_call_interaction(self, caller: Function, called: Function):
        (self.interactions_by_call[caller, called]).calls.append(Call(self.next_interaction_rank()))

    def add_return_interaction(self, called: Function, caller: Function):
        (self.interactions_by_call[caller, called]).responses.append(Return(self.next_interaction_rank()))

    def add_raised_interaction(self, called: Function, caller: Function, error_class_name: str):
        (self.interactions_by_call[caller,
                                   called]).responses.append(Raised(self.next_interaction_rank(), error_class_name))

    def on_header(self, start_module: str, start_func_name: str):
        diagram_name = f'{start_module}.{start_func_name}-component'
        self.io_sink.write(self.fmt.format(HEADER_TPL, diagram_name=diagram_name))

    def on_tracing_start(self, called: CallEnd):
        self.traced_function = self.function_from_call(called)

    def on_start_call(self, caller: CallEnd, called: CallEnd):
        self.add_call_interaction(self.function_from_call(caller), self.function_from_call(called))

    def on_error_propagation(self, error_called: CallEnd, error_caller: CallEnd, error: Error):
        self.add_raised_interaction(
            self.function_from_call(error_called), self.function_from_call(error_caller), error.class_name
        )

    def on_return(self, called: CallEnd, caller: CallEnd, **kwargs):
        self.add_return_interaction(self.function_from_call(called), self.function_from_call(caller))

    def on_tracing_end(self, called: CallEnd, arg: Any):
        pass

    def on_unhandled_error_end(self, called: CallEnd, error: Error):
        # TODO add a relationship to a PlantUML label in Red with the name of the error (to indicate that the error exits unhandled the execution)?
        # see https://plantuml.com/en/deployment-diagram#ded8ac71cf351121
        ...

    def on_footer(self):
        '''
        At this stage, the exporter has all the information it needs to produce the contents of the diagram file
        '''
        # builds components structure
        root_module = self.build_components_structure(self.functions.values())

        # writes components structure
        self.write_components_structure(root_module, self.traced_function)

        # writes interactions
        self.write_components_interactions(self.interactions_by_call)

        # writes the file footer
        self.io_sink.write(FOOTER_TPL)

    def build_components_structure(self, functions: Iterable[Function]) -> Module:
        '''
        Creates the modules hierarchy with their functions from the calls
        traced during the execution.
        '''
        root_module = Module(None, {}, {})

        for function in functions:
            # creates or finds the modules hierarchy holding the function
            parent_module = root_module
            for module_name in function.module_path:
                sub_module = parent_module.sub_modules.get(module_name)
                if sub_module is None:
                    sub_module = Module(module_name, {}, {})
                    parent_module.sub_modules[module_name] = sub_module
                parent_module = sub_module

            # adds the function in the module
            sub_module.functions[function.name] = function

        return root_module

    def write_components_structure(self, root_module: Module, traced_function: Function):
        '''
        Writes the 1st part of the PlantUML component diagram describing the structure of
        packages and modules, with the functions in them declared as UML components.
        '''
        for component_line in ModuleStructureVisitor(traced_function).visit_module(root_module, (), 0):
            self.io_sink.write(component_line)

    def write_components_interactions(self, interactions_by_call: Dict[Tuple[Function, Function], Interactions]):
        '''
        Writes the 2nd part of the PlantUML component diagram describing the calls between
        the functions as arrows between the components.
        '''
        for (caller_function, called_function), (calls, responses) in interactions_by_call.items():
            are_in_same_module = caller_function.module_path == called_function.module_path

            # call arrows between functions have a different direction whether they are in the same module or not
            call_arrow = '-->' if are_in_same_module else '->'

            call_label = f" : {', '.join(str(call.rank) for call in calls)}"
            self.io_sink.write(
                self.fmt.format(
                    INTERACTION_CALL_TPL,
                    caller_function=caller_function,
                    arrow=call_arrow,
                    called_function=called_function,
                    arrow_label=call_label
                )
            )

            # draws different line types for return and error exits
            returns = [response for response in responses if isinstance(response, Return)]
            if returns:
                returns_arrow = '<..' if are_in_same_module else '<.'
                returns_label = f" : {', '.join(str(exit_return.rank) for exit_return in returns)}"
                self.io_sink.write(
                    self.fmt.format(
                        INTERACTION_CALL_TPL,
                        caller_function=caller_function,
                        arrow=returns_arrow,
                        called_function=called_function,
                        arrow_label=returns_label
                    )
                )

            raiseds = [response for response in responses if isinstance(response, Raised)]
            if raiseds:
                raiseds_arrow = f"{'<..' if are_in_same_module else '<.'}[thickness=2]"
                raiseds_label = ', '.join(f'{exit_raised.rank}:{exit_raised.error}' for exit_raised in raiseds)
                raiseds_label = f' #line:darkred;text:darkred : {raiseds_label}'
                self.io_sink.write(
                    self.fmt.format(
                        INTERACTION_CALL_TPL,
                        caller_function=caller_function,
                        arrow=raiseds_arrow,
                        called_function=called_function,
                        arrow_label=raiseds_label
                    )
                )
