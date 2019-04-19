import ur
import random
import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense

class Player():
  
    def __init__(self, name='black', asc='■'):
        self.name = name
        self.ascii = asc
        
    def choose_move(self, game, movement):
        pass
        
    def learn(self, win=True):
        pass
      
    def empty_history(self):
        pass
      
    def set_learning(self, boolean):
        pass
    
class HumanPlayer(Player):
    
    def choose_move(self, game, movement):
        valid_moves = game.valid_movements(movement)
        fstates = [(move, game.get_sim_state(move, movement)) for move in valid_moves]
        print(game.get_state(self), movement)
        print(fstates)
        piece = int(self.sanitize_input(input("Choose a piece:")))
        while piece not in valid_moves:
            print("Valid moves: ", valid_moves)
            piece = int(input("Choose a valid piece:"))
        print("================")
        return piece
    
    def sanitize_input(self, cell):
        if cell == "":
            return 0
        if int(cell) > 15:
            return 15
        return cell
        
        
class RandomPlayer(Player):
  
    def choose_move(self, game, movement):
        valid_moves = game.valid_movements(movement)
        piece = random.choice(valid_moves)
        return piece
      
class SimplePlayer(Player):
  
    def choose_move(self, game, movement):
        valid_moves = game.valid_movements(movement)
        piece = valid_moves[0]
        return piece
      
class MaxPlayer(Player):
  
    def choose_move(self, game, movement):
        valid_moves = game.valid_movements(movement)
        piece = max(valid_moves)
        return piece
      
class AggressiveMaxPlayer(Player):
  
    def choose_move(self, game, movement):
        valid_moves = game.valid_movements(movement)
        occupied = [move for move in valid_moves 
                      if game.is_occupied_by_enemy(move+movement, self) and
                         move not in ur.SAFE]
        if occupied:
            return max(occupied)
        else:
            return max(valid_moves)
          
class RosettaLoverPlayer(Player):
  
    def choose_move(self, game, movement):
        valid_moves = game.valid_movements(movement)
        to_rosettas = [piece for piece in valid_moves
                          if piece+movement in ur.ROSETTA]
        not_in_rosetta = [piece for piece in valid_moves
                          if piece not in ur.CENTRAL_ROSETTA]
        if to_rosettas:
            return max(to_rosettas)
        elif not_in_rosetta:
            return max(not_in_rosetta)
        else:
            return max(valid_moves)

class QPlayer(Player):
  
    def __init__(self, rate, states=None, name='white', asc='q'):
        self.name = name
        self.learning_rate = rate
        if not states:
            self.states = {}
        else:
            self.states = states
        self.last_states = []
        self.learning = False
        self.ascii = asc
        self.enemy_states = []
    
    def choose_move(self, game, movement):
        previous_state = game.get_state(player=self)
        self.enemy_states.append(ur.transpose_state(previous_state))
        
        valid_moves = game.valid_movements(movement)        
        future_states = [game.get_sim_state(move, movement) for move in valid_moves]
        state, piece = self.get_best_piece_for_state(future_states, valid_moves)
        
        self.last_states.append(state)
        return piece
      
    def learn(self, win=True):
        if win:
            for i, state in enumerate(self.last_states):
                coef = i/len(self.last_states)
                self.buff(state, coef)
#             for i, state in enumerate(self.enemy_states):
#                 coef = i/len(self.enemy_states)
#                 self.nerf(state, coef)
        else:
            for i, state in enumerate(self.last_states):
                coef = i/len(self.last_states)
                self.nerf(state, coef)
#             for i, state in enumerate(self.enemy_states):
#                 coef = i/len(self.enemy_states)
#                 self.buff(state, coef)
        self.last_states = []
        self.enemy_states = []
    
    def buff(self, state, coef):
        if state in self.states:
            self.states[state] = self.states[state]*(1+self.learning_rate*coef)
        else:
            self.states[state] = 0.5*(1+self.learning_rate*coef)
    
    def nerf(self, state, coef):
        if state in self.states:
            self.states[state] = self.states[state]/(1+self.learning_rate*coef)
        else:
            self.states[state] = 0.5/(1+self.learning_rate*coef)
            
    def set_learning(self, learning):
        self.learning = learning
        
    def get_best_piece_for_state(self, states, moves):
        indexes = [i for i in range(len(moves))]
        values = [self.states[state] if state in self.states else 0.5
                  for state in states]
        
        if(self.learning):
            try:
                index = random.choices(indexes, weights=values)[0]
            except:
                index = 0
            piece = moves[index]
            best_state = states[index]
        else:
            best_state = states[values.index(max(values))]
            best_value_indexes = [i for i in range(len(values)) if values[i] == max(values)]
            piece = max([moves[i] for i in best_value_indexes])
        return best_state, piece
      
    def set_learning(self, learn):
        self.learning = learn
        
    def empty_history(self):
        self.last_states = []
        self.enemy_states = []
        
class DeepQPlayer(Player):

  
    def __init__(self, rate, name='white', asc='dq'):
        self.name = name
        self.learning_rate = rate
        self.last_states = []
        self.last_moves = []
        self.learning = False
        self.ascii = asc
        self.enemy_states = []
        self.model = Sequential()
        self.model.add(Dense(units=64, activation='relu', input_dim=23))
        self.model.add(Dense(units=6, activation='softmax'))
        self.model.compile(loss=keras.losses.categorical_crossentropy,
                      optimizer=keras.optimizers.SGD(lr=0.01, momentum=0.9, nesterov=True))
    
    def choose_move(self, game, movement):
        previous_state = game.get_state_list(self) + [movement]
        state = np.array([previous_state])

        prediction = self.model.predict(state)[0]
        player_pieces = game.get_pieces_in_order(self)
        prediction_valid = [p for i,p in enumerate(prediction) if game.is_movement_valid(player_pieces[i], movement)]
        if self.learning:
            try:
                ordinal = random.choices([i for i in range(len(prediction)) 
                                            if game.is_movement_valid(player_pieces[i], movement)], 
                                         weights=prediction_valid)[0]
            except:
                ordinal = 0
        else:
            max_pred = 0
            ordinal = -1
            for i, pred in enumerate(prediction):
                if (game.is_movement_valid(player_pieces[i], movement) and pred > max_pred):
                    ordinal = i
                    max_pred = pred
        piece = game.get_pieces_in_order(self)[ordinal]
        self.last_states.append(state)
        self.last_moves.append(ordinal)
        return piece.cell

    def learn(self, win=True):
        if win:
            for i, state in enumerate(self.last_states):
                x = state
                ordinal = self.last_moves[i]
                y = np.array([[1 if i == ordinal else 0 for i in range(6)]])
                self.model.fit(x, y, epochs=1, batch_size=1, verbose=False)
        else:
            for i, state in enumerate(self.last_states):
                pass
        self.last_states = []
        self.enemy_states = []
    
    def buff(self, state, coef):
        if state in self.states:
            self.states[state] = self.states[state]*(1+self.learning_rate*coef)
        else:
            self.states[state] = 0.5*(1+self.learning_rate*coef)
    
    def nerf(self, state, coef):
        if state in self.states:
            self.states[state] = self.states[state]/(1+self.learning_rate*coef)
        else:
            self.states[state] = 0.5/(1+self.learning_rate*coef)
            
    def set_learning(self, learning):
        self.learning = learning
        
    def get_best_piece_for_state(self, states, moves):
        indexes = [i for i in range(len(moves))]
        values = [self.states[state] if state in self.states else 0.5
                  for state in states]
        
        if(self.learning):
            try:
                index = random.choices(indexes, weights=values)[0]
            except:
                index = 0
            piece = moves[index]
            best_state = states[index]
        else:
            best_state = states[values.index(max(values))]
            best_value_indexes = [i for i in range(len(values)) if values[i] == max(values)]
            piece = max([moves[i] for i in best_value_indexes])
        return best_state, piece
      
    def set_learning(self, learn):
        self.learning = learn
        
    def empty_history(self):
        self.last_states = []
        self.enemy_states = []