import numpy as np
import sys
from typing import Optional, List


class BoardState:
    def __init__(self, board: np.ndarray, current_player: int = 1, pieces: int = -1, captured = None, cap = None, uncap: List[int] = []):
        self.board = board
        self.captured = [[False] * 8 for i in range(8)]
        self.current_player = current_player
        self.pieces = pieces
        self.cap = cap
        self.uncap = []
        if (pieces == -1):
            self.pieces += 1
            for x in range(8):
                for y in range(8):
                    if (board[y, x] != 0):
                        self.pieces += 1
        if captured is not None:
            for i in range(8):
                for j in range(8):
                    self.captured[i][j] = captured[i][j]
        for el in uncap:
            self.uncap.append(el)

    def copy(self) -> 'BoardState':
        return BoardState(self.board.copy(), self.current_player, self.pieces, self.captured, self.cap, self.uncap)

    def on_board(self, x, y) -> 'Bool':
        return (0 <= x <= 7) and (0 <= y <= 7)

    def can_capture_man(self, from_x, from_y) -> 'Bool':
        flag = False
        for dx in [1, -1]:
            for dy in [1, -1]:
                nx = from_x + 2 * dx
                ny = from_y + 2 * dy
                del_x = (from_x + nx) // 2
                del_y = (from_y + ny) // 2
                if not self.on_board(nx, ny):
                    continue
                if self.board[ny, nx] != 0 or self.captured[ny][nx]:
                    continue
                if self.captured[del_y][del_x] or self.board[del_y, del_x] * self.board[from_y, from_x] >= 0:
                    continue
                flag = True
                break      
        return flag
    
    def can_capture_king(self, from_x, from_y):
        flag = False
        for dx in [1, -1]:
            for dy in [1, -1]:
                for mult in range(1, 8):
                    nx = from_x + dx * mult
                    ny = from_y + dy * mult
                    if not self.on_board(nx, ny):
                        break
                    if (self.board[ny, nx] * self.board[from_y, from_x] > 0):
                        break
                    if self.board[ny, nx] * self.board[from_y, from_x] < 0:
                        to_x = nx + dx
                        to_y = ny + dy
                        if not self.on_board(to_x, to_y):
                            break
                        if self.board[to_y, to_x] != 0 or self.captured[to_y][to_x]:
                            break
                        flag = True
                        break    
        return flag
    
    def can_capture(self, from_x, from_y) -> 'Bool':
        flag = False
        if self.board[from_y, from_x] in [1, -1]:
            return self.can_capture_man(from_x, from_y)
        else:
            return self.can_capture_king(from_x, from_y)

    def end_move(self) -> 'BoardState':
        result = self.copy()
        from_x = self.cap[0]
        from_y = self.cap[1]
        if (not self.can_capture(from_x, from_y)):
            result.current_player *= -1
            for el in result.uncap:
                result.captured[el[1]][el[0]] = False
            result.uncap = []
            result.cap = None
            return result
        else:
            return result

    def do_move_man(self, from_x, from_y, to_x, to_y, need_to_cap) -> Optional['BoardState']:
        dx = to_x - from_x
        dy = to_y - from_y        
        if (abs(dx) != abs(dy)):
            return None
        if (abs(dx) == abs(dy) == 1):
            if (dy == self.current_player):
                return None
            if (need_to_cap):
                return None
            result = self.copy()
            result.board[to_y, to_x] = result.board[from_y, from_x]
            result.board[from_y, from_x] = 0
            if (to_y == 0 and self.current_player == 1) or (to_y == 7 and self.current_player == -1):
                result.board[to_y, to_x] *= 2
            result.current_player *= -1
            return result

        elif (abs(dx) == abs(dy) == 2):
            del_y = (to_y + from_y) // 2
            del_x = (to_x + from_x) // 2
            if self.captured[del_y][del_x]:
                return None
            if (self.board[del_y, del_x] * self.board[from_y, from_x] < 0):
                result = self.copy()
                result.board[to_y, to_x] = result.board[from_y, from_x]
                result.board[from_y, from_x] = 0
                result.board[del_y, del_x] = 0
                result.pieces -= 1
                result.captured[del_y][del_x] = True
                result.uncap.append((del_x, del_y))
                if (to_y == 0 and self.current_player == 1) or (to_y == 7 and self.current_player == -1):
                    result.board[to_y, to_x] *= 2
                result.cap = (to_x, to_y)
                return result.end_move()
            else:
                return None
        else:
            return None
        
    def do_move_king(self, from_x, from_y, to_x, to_y, need_to_cap) -> Optional['BoardState']:
        dx = to_x - from_x
        dy = to_y - from_y        
        if (abs(dx) != abs(dy)):
            return None

        del_x = -1
        del_y = -1
        ddx = dx // abs(dx)
        ddy = dy // abs(dy)

        nx = from_x + ddx
        ny = from_y + ddy

        while (nx != to_x or ny != to_y):
            if self.board[ny, nx] * self.board[from_y, from_x] > 0:
                return None
            elif self.board[ny, nx] * self.board[from_y, from_x] < 0:
                if (del_x != -1 or self.captured[del_y][del_x]):
                    return None
                else:
                    del_x = nx
                    del_y = ny
            nx += ddx
            ny += ddy

        result = self.copy()
        result.board[to_y, to_x] = result.board[from_y, from_x]
        result.board[from_y, from_x] = 0
        if (del_x != -1):
            result.board[del_y, del_x] = 0
            result.uncap.append((del_x, del_y))
            result.pieces -= 1
            result.cap = (to_x, to_y)
            return result.end_move()
        if (need_to_cap):
            return None
        result.current_player *= -1
        return result        

    def do_move(self, from_x, from_y, to_x, to_y, need_to_cap: bool = None) -> Optional['BoardState']:
        if (self.cap is not None and (from_x, from_y) != self.cap):
            sys.stdout.flush()
            return None

        if (self.board[from_y, from_x] * self.current_player <= 0):
            return None

        if (to_x + to_y) % 2 == 0:
            return None

        if self.board[to_y, to_x] != 0:
            return None

        if self.board[to_y, to_x] * self.board[from_y, from_x] > 0:
            return None

        if (need_to_cap is None):
            need_to_cap = self.is_capture()

        if self.board[from_y, from_x] in [1, -1]:
            return self.do_move_man(from_x, from_y, to_x, to_y, need_to_cap)

        if self.board[from_y, from_x] in [2, -2]:
            return self.do_move_king(from_x, from_y, to_x, to_y, need_to_cap)            
            

    def get_possible_moves(self) -> List['BoardState']:
        res = []
        A = self.is_capture()
        for y in range(8) if self.current_player == 1 else reversed(range(8)):
            for x in range(8):
                if (self.board[y, x] * self.current_player <= 0):
                    continue
                if (self.board[y, x] in [1, -1]):
                    continue
                if (self.cap is not None and (x, y) != self.cap):
                    continue
                new_board = None
                for dx in [1, -1]:
                    for dy in [1, -1]:
                        for k in range(8):
                            nx = x + dx * k
                            ny = y + dy * k
                            if not self.on_board(nx, ny):
                                continue
                            new_board = self.do_move(x, y, nx, ny, A)
                            if new_board is not None:
                                res.append(new_board)

        for y in range(8) if self.current_player == 1 else reversed(range(8)):
            for x in range(8):
                if (self.board[y, x] * self.current_player <= 0):
                    continue
                if (self.board[y, x] in [2, -2]):
                    continue
                if (self.cap is not None and (x, y) != self.cap):
                    continue
                new_board = None
                for dx in [2, -2]:
                    for dy in [2, -2]:
                        nx = x + dx
                        ny = y + dy
                        if not self.on_board(nx, ny):
                            continue
                        new_board = self.do_move(x, y, nx, ny, A)
                        if new_board is not None:
                            res.append(new_board)
                for dx in [1, -1]:
                    nx = x + dx
                    ny = y + -(self.current_player)
                    if not self.on_board(nx, ny):
                        continue
                    new_board = self.do_move(x, y, nx, ny, A)
                    if new_board is not None:
                        res.append(new_board)
        return res

    def output(self, fout):
        for line in self.board:
            for elem in line:
                print(elem, end=" ", file=fout)
            print(file=fout)
        for line in self.captured:
            for elem in line:   
                print(int(elem), end=" ", file=fout)
            print(file=fout)
        if (self.cap is None):
            print(self.cap, file=fout)
        else:
            print(self.cap[0], self.cap[1], file=fout)
        print(self.current_player, file=fout)
        print(self.pieces, file=fout)
        sys.stdout.flush()

    def input(self, fin) -> 'BoardState':
        result = self.copy()
        s = fin.readlines()
        s = [e.strip() for e in s]
        mat = [0] * 8
        mat = [[int(e) for e in s[i].split()] for i in range(8)]
        for i in range(8):
            for j in range(8):
                result.board[i, j] = mat[i][j]
        for i in range(8):
            result.captured[i] = list(map(int, s[8 + i].split()))
        sys.stdout.flush()
        result.cap = s[16]
        if result.cap[0] != "N":
            print(result.cap)
            sys.stdout.flush()
            result.cap = list(map(int, s[16].split()))
            result.cap = (result.cap[0], result.cap[1])
        else:
            result.cap = None
        result.current_player = int(s[17])
        result.pieces = int(s[18])
        return result

    def is_capture(self) -> 'Bool':
        if self.cap is not None:
            return True
        for y in range(8):
            for x in range(8):
                if ((self.board[y, x] * self.current_player > 0) and self.can_capture(x, y)):
                    return True
        return False

    @staticmethod
    def initial_state() -> 'BoardState':
        board = np.zeros(shape=(8, 8), dtype=np.int8)

        for i in range(5, 8):
            for j in range(8):
                if (i + j) % 2 == 1:
                    board[i, j] = 1
        for i in range(3):
            for j in range(8):
                if (i + j) % 2 == 1:
                    board[i, j] = -1
        return BoardState(board, 1)
