from pydoctrace.doctrace import trace_to_component_puml

from tests.integrations.classes.basicclass import main_basic_class
from tests.integrations.classes.complexclasses import Game, TicTacToe, main_start_game
from tests.integrations.classes.dataclass import main_dataclass
from tests.integrations.classes.namedtuple import main_namedtuple
from tests.integrations.classes.namedtuple_disambiguation import main_namedtuple_disambiguation


def test_doctrace_classes_namedtuple_component():
    traceable_main = trace_to_component_puml(filter_presets=())(main_namedtuple)

    assert traceable_main() == 'Suzie Q'


def test_doctrace_classes_basicclass_component():
    traceable_main = trace_to_component_puml(filter_presets=())(main_basic_class)

    assert traceable_main() == 'Suzie Q'


def test_doctrace_classes_dataclass_component():
    traceable_main = trace_to_component_puml(filter_presets=())(main_dataclass)

    assert traceable_main() == 'Suzie Q'


def test_doctrace_classes_namedtuple_disambiguation():
    traceable_main = trace_to_component_puml(filter_presets=())(main_namedtuple_disambiguation)

    person, pet = traceable_main()
    assert person.firstname == 'Suzie'
    assert person.lastname == 'Q'
    assert pet.name == 'Bémol'
    assert pet.age == 2


def test_doctrace_classes_main_start_game():
    traceable_main = trace_to_component_puml(filter_presets=())(main_start_game)

    tic_tac_toe: TicTacToe = traceable_main()

    assert tic_tac_toe.board.matrix == [
        [Game.Board.Piece('o', 0, 0), None, None],
        [None, None, Game.Board.Piece('x', 1, 2)],
        [None, None, None],
    ]
