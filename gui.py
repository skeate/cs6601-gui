#!/usr/bin/env python

from threading import Thread
import pygame
from Queue import Queue, Empty
from isolation import Board
from pygame.locals import *
from time import time
from random import randint

pygame.init()

light_color = pygame.Color('#c0c0c0')
dark_color  = pygame.Color('#808080')
disabled    = pygame.Color('#101010')
red         = pygame.Color('#bb0000')
blue        = pygame.Color('#0000bb')
green       = pygame.Color('#00bb00')
legal       = pygame.Color('#004400')

q_game = Queue()
q_gui = Queue()

class GuiPlayer():
    def move(self, game, legal_moves, time_left):
        q_gui.put({'name': 'human move start'})
        legal_move = False
        move = (-1, -1)
        while not legal_move:
            move = q_game.get()
            if move == 'die' or move in legal_moves:
                legal_move = True
            q_game.task_done()
        q_gui.put({'name': 'human move stop'})
        # we are trying to quit while watching for a human player's move
        # let's just give a dummy answer, retrigger the kill message, and go
        # back to main game loop
        if move == 'die':
            q_game.put('die')
            move = (-1, -1)
        return move

class RandomPlayer():
    """Player that chooses a move randomly."""
    def move(self, game, legal_moves, time_left):
        if not legal_moves: return (-1,-1)
        return legal_moves[randint(0,len(legal_moves)-1)]

class IsolationGui():
    def __init__(self, width=7, height=7):
        self.width = width
        self.height = height
        self.square_size = 100
        self.mouse_pos = (-1, -1)
        self.game = None
        self.board = None
        self.input_mode = False

    def kill_game(self):
        if self.game:
            q_game.put('die')
            q_game.join()
            self.game = None

    def handle_key(self, key, mod):
        if key == K_ESCAPE or key == K_c and mod & KMOD_CTRL > 0:
            q_game.put('die')
            pygame.event.post(pygame.event.Event(QUIT))
        elif key in (K_1, K_2, K_3, K_4):
            self.kill_game()
            self.game = Thread(target=new_game, args=({K_1:1,K_2:2,K_3:3,K_4:4}[key],))
            self.game.start()

    def handle_click(self, pos, button):
        if not self.input_mode:
            return
        row = int(pos[1] / self.square_size)
        col = int(pos[0] / self.square_size)
        q_game.put((row, col))

    def set_mouse_pos(self, pos):
        self.mouse_pos = (int(pos[1] / self.square_size), int(pos[0] / self.square_size))
        if self.input_mode:
            self.draw_board()

    def draw_board(self):
        if not self.screen:
            raise Exception('Attempted to draw board with no window available')
        if not self.board:
            return
        surface = self.screen
        light_start = False
        legal_moves = self.board.get_legal_moves()
        for row in xrange(self.height):
            light_start = not light_start
            light = light_start
            for col in xrange(self.width):
                p1_last_move = self.board.__last_player_move__[self.board.__player_1__]
                p2_last_move = self.board.__last_player_move__[self.board.__player_2__]
                match = lambda pos: row == pos[0] and col == pos[1]
                if match(p1_last_move):
                    color = red
                elif match(p2_last_move):
                    color = blue
                elif self.board.__board_state__[row][col] == Board.BLANK:
                    square_legal = self.input_mode and (row,col) in legal_moves
                    if square_legal and match(self.mouse_pos):
                        color = green
                    elif square_legal and self.board.move_count > 1:
                        color = legal
                    else:
                        color = light_color if light else dark_color
                else:
                    color = disabled
                rect = pygame.Rect(col * self.square_size, row * self.square_size, self.square_size, self.square_size)
                surface.fill(color, rect)
                light = not light

    def draw_text(self, text, size, color=pygame.Color('#ffffff'), pos=(0,0), center_in=(0,0)):
        font = pygame.font.Font(None, size)
        lines = text.split('\n')
        for line in lines:
            text = font.render(line.strip(), True, color)
            if center_in != (0,0):
                pos = (
                        pos[0] + (center_in[0] - text.get_width()) / 2,
                        pos[1] + (center_in[1] - text.get_height()) / 2
                        )
            self.screen.blit(text, pos)
            pos = (pos[0], int(pos[1] + text.get_height() * 1.1))


    def start(self):
        width = self.width * self.square_size
        height = self.height * self.square_size
        self.screen = pygame.display.set_mode([width, height])
        self.clock = pygame.time.Clock()

        self.draw_text("""
        Press ESC or Ctrl+C to close this window at any time.

        Press 1 to start a new game as player 1 against the AI.
        Press 2 to start a new game as player 2 against the AI.
        Press 3 to start a game with two human players.
        Press 4 to watch the AI play against itself.
        """, 36)

        while True:
            pygame.display.flip()
            self.clock.tick(60)
            try:
                task = q_gui.get(False)
                if task['name'] == 'game over':
                    size = self.square_size
                    last_move = map(
                            lambda x: x * size,
                            self.board.get_last_move_for_player(task['winner'])
                            )
                    self.draw_text('W', 48, pos=tuple(reversed(last_move)), center_in=(size,)*2)
                    self.kill_game()
                elif task['name'] == 'human move start':
                    self.input_mode = True
                    self.draw_board()
                elif task['name'] == 'human move stop':
                    self.input_mode = False
                elif task['name'] == 'draw':
                    self.draw_board()
                    q_game.put('move')
                else:
                    self.board = task['board']
                q_gui.task_done()
            except Empty:
                pass
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    self.handle_key(event.key, event.mod)
                elif event.type == MOUSEBUTTONUP:
                    self.handle_click(event.pos, event.button)
                elif event.type == MOUSEMOTION:
                    self.set_mouse_pos(event.pos)

def new_game(mode):
    AIPlayer = RandomPlayer
    if mode == 1:
        player1 = GuiPlayer()
        player2 = AIPlayer()
    elif mode == 2:
        player1 = AIPlayer()
        player2 = GuiPlayer()
    elif mode == 3:
        player1 = GuiPlayer()
        player2 = GuiPlayer()
    elif mode == 4:
        player1 = AIPlayer()
        player2 = AIPlayer()
    board = Board(player1, player2)
    q_gui.put({'name': 'set board', 'board': board})

    curr_time_millis = lambda : int(round(time() * 1000))
    time_limit = 500

    print('== BEGIN GAME ==')

    loop = True
    while loop:
        q_gui.put({'name': 'draw'})
        legal_moves = board.get_legal_moves()
        if len(legal_moves) == 0:
            q_gui.put({
                'name': 'game over',
                'winner': board.__inactive_player__
            })
        task = q_game.get()
        if task == 'die':
            print('== END GAME ==')
            loop = False
        elif task == 'move' and len(legal_moves) > 0:
            move_start = curr_time_millis()
            time_left = lambda : time_limit - (curr_time_millis() - move_start)
            player = board.get_active_player()
            next_move = player.move(board, legal_moves, time_left)
            if next_move != (-1, -1):
                player_symbol = board.__player_symbols__[player]
                print('player {0}: {1} | took {2} ms'.format(
                    player_symbol,
                    next_move,
                    time_limit - time_left()))
                board.__apply_move__(next_move)
        q_game.task_done()

if __name__ == '__main__':
    gui = IsolationGui()
    gui.start()
