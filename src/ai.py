from typing import Optional, Tuple

from .boardstate import BoardState

import sys


class AI:
    def __init__(self, INF: int = 1000000):
        self.INF = INF

    def next_move(self, board: BoardState, alpha: int, beta: int, depth: int = 4) -> Optional[Tuple['BoardState', int, int]]:
        moves = board.get_possible_moves()
        if len(moves) == 0:
            return (None, self.INF * -board.current_player, 1)
        best = None
        rating = 0
        cnt = 1
        if (board.current_player == 1):
            if (depth == 1):
                for game in moves:
                    cnt += 1
                    if best is None or rating < self.evaluation(game):
                        best = game
                        rating = self.evaluation(game)
                    if (best is not None):
                        alpha = max(alpha, rating)
                    if (alpha >= beta):
                        return (best, rating, cnt)
                return (best, rating, cnt)
            else:
                for game in moves:
                    cur = self.next_move(game, alpha, beta, depth - 1)
                    cnt += cur[2]
                    if best is None or rating < cur[1]:
                        best = game
                        rating = cur[1]
                    if (best is not None):
                        alpha = max(alpha, rating)
                    if (alpha >= beta):
                        if best is None:
                            return (best, self.INF * -1, cnt)
                        return (best, rating, cnt)
                if best is None:
                    return (best, self.INF * -1, cnt)
                return (best, rating, cnt)
        else:
            if (depth == 1):
                for game in moves:
                    cnt += 1
                    if best is None or rating > self.evaluation(game):
                        best = game
                        rating = self.evaluation(game)
                    if (best is not None):
                        beta = min(beta, rating)
                    if (alpha >= beta):
                        return (best, rating, cnt)
                return (best, rating, cnt)
            else:
                for game in moves:
                    cur = self.next_move(game, alpha, beta, depth - 1)
                    cnt += cur[2]
                    if best is None or rating > cur[1]:
                        best = game
                        rating = cur[1]
                    if (best is not None):
                        beta = max(beta, rating)
                    if (alpha >= beta):
                        if best is None:
                            return (best, self.INF, cnt)
                        return (best, rating, cnt)
                if best is None:
                    return (best, self.INF, cnt)
                return (best, rating, cnt)

    def evaluation(self, board: BoardState) -> int:
        if board.pieces < 7:
            res = board.current_player * len(board.get_possible_moves())
        else:
            res = 5 * board.current_player
        for x in range(8):
            for y in range(8):
                if (board.board[y, x] == 0):
                    continue
                colour = board.board[y, x] // abs(board.board[y, x])
                if (board.board[y, x] in [1, -1]):
                    res += 10 * colour
                elif board.board[y, x] in [2, -2]:
                    res += 30 * colour
                    continue
                if colour == 1:
                    res += (7 - y) * 3
                else:
                    res -= y * 3
        return res
