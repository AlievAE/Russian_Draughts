from itertools import product

import pygame
from pygame import Surface

from src.ai import AI
from src.boardstate import BoardState

import sys
import timeit
import time


def draw_board(screen: Surface, pos_x: int, pos_y: int, elem_size: int, board: BoardState):
    dark = (0, 0, 0)
    white = (200, 200, 200)

    for y, x in product(range(8), range(8)):
        color = white if (x + y) % 2 == 0 else dark
        position = pos_x + x * elem_size, pos_y + y * elem_size, elem_size, elem_size
        pygame.draw.rect(screen, color, position)

        figure = board.board[y, x]

        if figure == 0:
            continue

        if figure > 0:
            figure_color = 255, 255, 255
        else:
            figure_color = 100, 100, 100
        r = elem_size // 2 - 10

        pygame.draw.circle(screen, figure_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)
        if abs(figure) == 2:
            r = 5
            negative_color = [255 - e for e in figure_color]
            pygame.draw.circle(screen, negative_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)


def game_loop(screen: Surface, board: BoardState, ai: AI):
    grid_size = screen.get_size()[0] // 8
    pos = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click_position = event.pos

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                new_x, new_y = [p // grid_size for p in event.pos]
                old_x, old_y = [p // grid_size for p in mouse_click_position]
                sys.stdout.flush()
                new_board = board.do_move(old_x, old_y, new_x, new_y)
                if new_board is not None:
                    board = new_board

            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                x, y = [p // grid_size for p in event.pos]
                board.board[y, x] = (board.board[y, x] + 1 + 2) % 5 - 2
                if board.board[y, x] == 1:
                    board.pieces += 1
                elif board.board[y, x] == 0:
                    board.pieces -= 1

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = timeit.default_timer()
                    to_play = board.current_player
                    while (board.current_player == to_play):
                        new_board = ai.next_move(board, -1000000, 1000000, 4)
                        if new_board[0] is not None:
                            board = new_board[0]
                        else:
                            break
                        sys.stdout.flush()
                        draw_board(screen, 0, 0, grid_size, board)
                        pygame.display.flip()
                        time.sleep(0.3)
                    stop = timeit.default_timer()
                    execution_time = stop - start
                if event.key == pygame.K_s and event.mod and pygame.KMOD_CTRL:
                    with open(OUTPUT, "w+") as fout:
                        board.output(fout)
                if event.key == pygame.K_d and event.mod and pygame.KMOD_CTRL:
                    with open(INPUT, "r+") as fout:
                        new_board = board.input(fout)
                    board = new_board
                if event.key == pygame.K_r and event.mod and pygame.KMOD_CTRL:
                    for i in range(8):
                        for j in range(8):
                            board.board[i, j] = 0
                            board.captured[i][j] = 0

                    board.cap = None
                    board.uncap = []
                    board.current_player = 1
                    board.pieces = 0

                if event.key == pygame.K_x and event.mod and pygame.KMOD_CTRL:
                    board.current_player *= -1

                if event.key == pygame.K_t and event.mod and pygame.KMOD_CTRL:
                    with open(TIMEOUTPUT, "w") as file_time:
                        flag = True
                        while (flag):
                            start = timeit.default_timer()
                            to_play = board.current_player
                            while (board.current_player == to_play):
                                new_board = ai.next_move(board, -1000000, 1000000, 4)
                                if new_board[0] is not None:
                                    board = new_board[0]
                                    print(new_board[2], end=" ", file=file_time)
                                    sys.stdout.flush()
                                else:
                                    flag = False
                                    break
                                time.sleep(0.3)
                                draw_board(screen, 0, 0, grid_size, board)
                                pygame.display.flip()
                            stop = timeit.default_timer()
                            execution_time = stop - start
                            if flag:
                                print(execution_time - 0.3, file=file_time)
                            sys.stdout.flush()

        draw_board(screen, 0, 0, grid_size, board)
        pygame.display.flip()


pygame.init()

INPUT = "output.txt"
OUTPUT = "output.txt"
TIMEOUTPUT = "moveTime.txt"

screen: Surface = pygame.display.set_mode([512, 512])
ai = AI()

game_loop(screen, BoardState.initial_state(), ai)

pygame.quit()
