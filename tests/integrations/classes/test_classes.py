from pickle import loads

from pytest import mark

from pydoctrace.exporters.plantuml.component import PlantUMLComponentExporter

from tests.integrations import TESTS_INTEGRATIONS_FOLDER, _get_file_suffix, diagram_integration_test
from tests.modules.classes.basicclass import main_basic_class
from tests.modules.classes.complexclasses import Game, TicTacToe, main_process_with_factory, main_start_game
from tests.modules.classes.dataclass import main_dataclass
from tests.modules.classes.local_defs import main_local_defs
from tests.modules.classes.namedtuples import main_namedtuple, main_namedtuple_disambiguation


def is_suzie_q(output: str):
    assert output == 'Suzie Q'


def are_namedtuples(output: tuple):
    person, pickled_person, pet_dict, pet_repr = output
    assert person.firstname == 'Suzie'
    assert person.lastname == 'Q'
    assert pet_dict['name'] == 'Bémol'
    assert pet_dict['age'] == 2
    unpickled_person = loads(pickled_person)
    assert unpickled_person == person


def are_dataclasses(output: tuple):
    suzie_fullname, suzie_hash, frankie_repr, comparison = output
    assert suzie_fullname == 'Suzie Q'
    assert isinstance(suzie_hash, int)
    assert frankie_repr == "Person(firstname='Frankie', lastname='Manning')"
    assert not comparison, 'the 2 instances of Person dataclass are not equal'


def has_matrix(tic_tac_toe: TicTacToe):
    assert tic_tac_toe.board.matrix == [
        [Game.Board.Piece('o', 0, 0), None, None],
        [None, None, Game.Board.Piece('x', 1, 2)],
        [None, None, None],
    ]


def is_minus_2(diff: int):
    assert diff == -2


@mark.parametrize(
    'exporter_class',
    [
        PlantUMLComponentExporter,
        # PlantUMLSequenceExporter, # returned value contains memory address, which causes flaky tests
    ],
)
@mark.parametrize(
    ['function_to_trace', 'output_assertion_callable'],
    [
        (
            main_basic_class,
            is_suzie_q,
        ),
        (
            main_namedtuple,
            is_suzie_q,
        ),
        (
            main_namedtuple_disambiguation,
            are_namedtuples,
        ),
        (
            main_dataclass,
            are_dataclasses,
        ),
        (
            main_start_game,
            has_matrix,
        ),
        (
            main_process_with_factory,
            is_minus_2,
        ),
        (
            main_local_defs,
            is_suzie_q,
        ),
    ],
)
def test_doctrace_classes(exporter_class, function_to_trace, output_assertion_callable):
    exporter_suffix = _get_file_suffix(exporter_class)
    output = diagram_integration_test(
        TESTS_INTEGRATIONS_FOLDER
        / 'classes'
        / f'test_{function_to_trace.__name__}-{output_assertion_callable.__name__}-{exporter_suffix}.puml',
        function_to_trace,
        (),
        None,
        exporter_class,
        # overwrite_expected_contents=True,
    )

    output_assertion_callable(output)
