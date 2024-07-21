from typing import List

from tests.modules.classes.collector import Collector


class Game:
    class Board:
        def __init__(self, width: int, length: int):
            self.x_max = width
            self.y_max = length
            self.matrix = [[None for _ in range(length)] for _ in range(width)]

        class Piece:
            def __init__(self, name: str, x: int, y: int):
                self.name = name
                self.x = x
                self.y = y

            def __eq__(self, other):
                return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

            def __str__(self) -> str:
                return self.name

            def __repr__(self) -> str:
                return f'{self.x}:{self.y} {self.name}'

    class Player:
        def __init__(self, name: str, pieces: List['Game.Board.Piece']):
            self.name = name
            self.pieces = pieces

    def __init__(self, board: Board, players: List['Game.Player']):
        self.board = board
        self.players = players

    def start(self):
        print('starting')


class TicTacToe(Game):
    class SquareBoard(Game.Board):
        def __init__(self, length: int):
            super().__init__(length, length)

        def __repr__(self) -> str:
            if getattr(self, 'matrix', None) is None:
                return '|'
            else:
                return '\n'.join('|'.join(' ' if cell is None else str(cell) for cell in line) for line in self.matrix)

    def __init__(self, white: Game.Player, black: Game.Player, board_size: int):
        super().__init__(TicTacToe.SquareBoard(board_size), [white, black])

    def place_piece(self, player_name: str, piece_name: str, x: int, y: int):
        player = next(player for player in self.players if player.name == player_name)
        target_cell = self.board.matrix[x][y]
        if target_cell is None:
            piece = Game.Board.Piece(piece_name, x, y)
            player.pieces.append(piece)
            self.board.matrix[x][y] = piece
        else:
            raise ValueError(f'cannot add {piece_name} in {x}:{y}: it is already occupied by {target_cell}')

    @staticmethod
    def start_game(board_size: int) -> 'TicTacToe':
        white = Game.Player('white', [])
        black = Game.Player('black', [])
        return TicTacToe(white, black, board_size)


def main_start_game() -> TicTacToe:
    tic_tac_toe = TicTacToe.start_game(3)
    # print(f'{tic_tac_toe.board}')
    tic_tac_toe.place_piece('white', 'x', 1, 2)
    tic_tac_toe.place_piece('black', 'o', 0, 0)
    # print(f'{tic_tac_toe.board}')
    # print(f'{tic_tac_toe.board.matrix=}')

    return tic_tac_toe


class DiffCollector(Collector):
    def _diff(self, aggregation, expected_result):
        return expected_result - aggregation


class ProcessMock:
    """
    Mock the Process class to execute the target function in the current process so that class attributes can be share
    """

    def __init__(self, target, args, daemon):
        self.target = target
        self.args = args
        self.daemon = daemon

    def start(self):
        pass

    def join(self):
        return self.target(*self.args)


def main_process_with_factory():
    process = ProcessMock(target=DiffCollector.collector_factory, args=((3, 4), sum, 5), daemon=True)
    process.start()
    return process.join()
