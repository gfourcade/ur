import random
import itertools
import pandas as pd
import matplotlib.pyplot as plt

ROSETTA = [4,8,14]
SAFE = [0,1,2,3,4,13,14,15]
CENTRAL_ROSETTA = [8]

class Piece():
    def __init__(self, player):
        self.player = player
        self.cell = 0
    
    def reset_cell(self):
        self.cell = 0
        
    def move(self, movement):
        self.cell = self.cell + movement

class Ur():
    def __init__(self, p1, p2, log=False):
        self.board = new_board()
        self.p1 = p1
        self.p2 = p2
        self.pieces = {}
        self.turn = itertools.cycle([self.p1, self.p2])
        self.current_turn = next(self.turn)
        self.moves = []
        self.logging = log
    
    def start_board(self):
        self.board = new_board()
        self.pieces[self.p1] = [Piece(self.p1) for i in range(6)]
        self.pieces[self.p2] = [Piece(self.p2) for i in range(6)]
        self.board[0] = self.pieces[self.p1] + self.pieces[self.p2]
        self.turn = itertools.cycle([self.p1, self.p2])
        self.current_turn = next(self.turn)
        self.moves = []
        
    def is_movement_valid(self, piece, movement):
        new_cell = piece.cell + movement
        if new_cell == 15:
            return True
        elif new_cell > 15:
            return False
        elif new_cell in SAFE:
            return not self.is_occupied_by_ally(new_cell, piece.player)
        else:
            return not self.is_occupied_by_ally(new_cell, piece.player)
        
    def valid_movements(self, movement):
        moves = [piece.cell for piece in self.pieces[self.current_turn]
                if self.is_movement_valid(piece, movement)]
        moves = list(set(moves))
        return moves
        
    def player_move(self):
        movement = roll_dice()
        player = self.current_turn
        if movement == 0:
            self.change_turn()
            return
        valid_moves = self.valid_movements(movement)
        if len(valid_moves) > 0:
            piece_cell = player.choose_move(self, movement)
            if piece_cell not in valid_moves:
                print("Player movement invalid!")
                print(self.get_state(player), piece_cell)
            self.move(piece_cell, movement)
        if(self.logging):
            print(player.ascii, movement)
            self.print_state()
    
    def move(self, piece_cell, movement):
        piece = self.get_piece_in_cell(piece_cell, self.current_turn)
        if movement == 0:
            return
        new_cell = piece.cell + movement
        self.board[piece.cell].remove(piece)        
        piece.move(movement)
        
        if new_cell not in SAFE:
            for piece_to_reset in self.board[new_cell]:
                piece_to_reset.reset_cell()
                self.board[0].append(piece_to_reset)
                if self.logging:
                    print(self.current_turn.ascii, "eats in", new_cell)
            self.board[new_cell] = []
        
        self.board[piece.cell].append(piece)
        if piece.cell not in ROSETTA:
            self.change_turn()
        self.moves.append((piece.player, piece.cell - movement, piece.cell))
        
    def get_piece_in_cell(self, cell, player):
        for piece in self.pieces[player]:
            if piece.cell == cell:
                return piece
        return None

    def get_pieces_in_order(self, player):
        pieces = []
        for cell in self.board:
            if len(self.board[cell]) > 0:
                pieces += [p for p in self.board[cell] if p.player == player]
        pieces.reverse()
        return pieces
    
    def is_occupied(self, cell):
        return len(self.board[cell]) > 0
    
    def is_occupied_by_enemy(self, cell, player):
        for piece in self.board[cell]:
            if piece.player != player:
                return True
        return False
          
    def is_occupied_by_ally(self, cell, player):
        for piece in self.board[cell]:
            if piece.player == player:
                return True
        return False
    
    def change_turn(self):
        self.current_turn = next(self.turn)
            
    def print_state(self):
        print([[piece.player.ascii for piece in self.board[cell]] for cell in range(0,1)])
        print([[piece.player.ascii for piece in self.board[cell]] for cell in range(1,5)])
        print([[piece.player.ascii for piece in self.board[cell]] for cell in range(5,13)])
        print([[piece.player.ascii for piece in self.board[cell]] for cell in range(13,15)])
        print([[piece.player.ascii for piece in self.board[cell]] for cell in range(15,16)])
        print('===============================================')
        
    def other_player(self, player):
        if self.p1 == player:
            return self.p2
        else:
            return self.p1
        
    def get_sim_state(self, cell, movement):
        player = self.current_turn
        pieces_current = [piece.cell for piece
                                 in self.pieces[player]]
        pieces_other = [piece.cell for piece
                               in self.pieces[self.other_player(player)]]
        
        for i, old_cell in enumerate(pieces_current):
            if old_cell == cell:
                pieces_current[i] = old_cell+movement
                break
        for i, old_cell in enumerate(pieces_other):
            if old_cell == cell+movement:
                pieces_other[i] = 0
                break
        pieces_current.sort()
        pieces_other.sort()
        i = 1
        res = 0
        for cell in pieces_other + pieces_current:
          res += cell*i
          i *= 16
        return hex(res)

    def get_state_list(self, player):
        state = []
        for i in self.board:
            cell = self.board[i]
            if i == 0:
                pass
            elif i < 5 or i == 13 or i == 14:
                state.append(1 if len(cell) > 0 and cell[0].player == player else 0)
                state.append(-1 if len(cell) > 0 and cell[0].player != player else 0)
            elif i == 15:
                state.append(sum([1 if piece.player == player else 0 for piece in cell]))
                state.append(sum([-1  if piece.player != player else 0 for piece in cell]))
            else:
                if len(cell) > 0:
                    state.append(1 if cell[0].player == player else -1)
                else:
                    state.append(0)
        return state

    def get_state(self, player):
        pieces_1 = sorted([piece.cell for piece in self.pieces[self.p1]])
        pieces_2 = sorted([piece.cell for piece in self.pieces[self.p2]])
        if player == self.p2:
            pieces = pieces_2 + pieces_1
        else:
            pieces = pieces_1 + pieces_2
        #print(pieces)
        i = 1
        res = 0
        for cell in pieces:
          res += cell*i
          i *= 16
        return hex(res)
        
    def is_ended(self):
        p1 = [1 for piece in self.pieces[self.p1] if piece.cell == 15]
        p2 = [1 for piece in self.pieces[self.p2] if piece.cell == 15]
        return sum(p1) == 6 or sum(p2) == 6
    
    def winner(self):
        p1 = [1 for piece in self.pieces[self.p1] if piece.cell == 15]
        p2 = [1 for piece in self.pieces[self.p2] if piece.cell == 15]
        if sum(p1) == 6:
            return self.p1
        elif sum(p2) == 6:
            return self.p2
        else:
            return None
        
def get_key_of_max_value(d):
    mx = max(d.values())
    keys = [k for k, v in d.items() if v == mx]
    return max(keys)

def new_board():
    board = {
        0 : [],
        1 : [], 2 : [], 3 : [], 4 : [],
        5 : [], 6 : [], 7 : [], 8 : [], 9 : [], 10 : [], 11 : [], 12 : [],
        13 : [], 14 : [],
        15 : []
    }
    return board

def transpose_state(state):
    state = int(state, 16)
    player_two_state = state % 0x1000000
    player_one_state = state  // 0x1000000
    return hex(player_two_state * 0x1000000 + player_one_state)
  
def roll_dice():
    dice = [random.randint(1,6) for i in range(4)]
    marks = [1 for d in dice if d > 3]
    return sum(marks)
  
def train_player(p1, p2, times):
    game = Ur(p1, p2)
    p1.set_learning(True)
    for i in range(times):
        game.start_board()
        while not game.is_ended():
            game.player_move()
        if(game.winner() == p1):
            p1.learn(win=True)
            p2.learn(win=False)
        else:
            p1.learn(win=False)
            p2.learn(win=True)
  
def test_player(p1, p2, times):
    game = Ur(p1, p2)
    p1.set_learning(False)
    
    p1_wins_tot = 0
    p2_wins_tot = 0
    p1_wins = 0
    p2_wins = 0
    for i in range(times):
        game.start_board()
        while not game.is_ended():
            game.player_move()
        if(game.winner() == p1):
            p1_wins += 1
            p1_wins_tot += 1
        else:
            p2_wins += 1
            p2_wins_tot += 1
        p1.empty_history()
        p2.empty_history()

    return p1_wins / (p1_wins+p2_wins)

def train(player, enemies, enemies_res, times=2):
    for enemy_name in enemies:
        enemies[enemy_name].set_learning(False)
    for i in range(times):
        player.set_learning(True)
        for k in range(10):
            for enemy in enemies:
                train_player(player, enemies[enemy], 1)
        if i % (times/20) == 0:
            print("ended learning", i+1, "/", times)

        # player.set_learning(False)
        # for enemy_name in enemies:
        #     print("testing", enemy_name)
        #     enemy_res = enemies_res[enemy_name]
        #     enemy = enemies[enemy_name]
        #     res = test_player(player, enemy, 1000)
        #     enemy_res.append(res)    
        # print("ended testing", i, "/10")
        
def run_parallel(processes, function):
    proc = []
    for i in range(processes):
        p = Process(target=function)
        p.start()
        proc.append(p)
    for p in proc:
        p.join()