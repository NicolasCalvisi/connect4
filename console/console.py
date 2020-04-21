#!/usr/bin/env python
# coding: utf-8

# In[8]:


import numpy as np
from time import sleep


# In[9]:


NB_ROWS = 6
NB_COLUMNS = 7
EMPTY = -1
YELLOW = 0
RED = 1


# In[10]:


class Board:
    def __init__(self, NB_ROWS = 6, NB_COLUMNS = 7):
        self.NB_ROWS = NB_ROWS
        self.NB_COLUMNS = NB_COLUMNS
        self.EMPTY = -1
        self.YELLOW = 0
        self.RED = 1
        self.WINDOW_LENGTH=4
        self.board = np.ones((NB_ROWS,NB_COLUMNS))*EMPTY
        
    def copy(self):
        new_board = Board(NB_ROWS = self.NB_ROWS, NB_COLUMNS = self.NB_COLUMNS)
        new_board.board = self.board.copy()
        return new_board
    
    def drop_piece(self, row, col, piece):
        assert piece==self.YELLOW or piece == self.RED, "invalide piece"
        self.board[row, col] = piece
        
    def is_valid_location(self, col):
        if (col < 0 or col > self.NB_COLUMNS) : return False
        else : return self.board[self.NB_ROWS-1, col] == self.EMPTY
        
    def get_next_open_row(self, col):
        try : 
            for r in range(self.NB_ROWS):
                if self.board[r, col] == self.EMPTY:
                    return r
            return None
        except : return None
    
    
    def winning_move(self, piece):
        # Check horizontal locations for win
        for c in range(self.NB_COLUMNS-3):
            for r in range(self.NB_ROWS):
                if self.board[r, c] == piece and self.board[r, c+1] == piece and self.board[r, c+2] == piece and self.board[r, c+3] == piece:
                    return True

        # Check vertical locations for win
        for c in range(self.NB_COLUMNS):
            for r in range(self.NB_ROWS-3):
                if self.board[r, c] == piece and self.board[r+1, c] == piece and self.board[r+2, c] == piece and self.board[r+3, c] == piece:
                    return True

        # Check first diaganol
        for c in range(self.NB_COLUMNS-3):
            for r in range(self.NB_ROWS-3):
                if self.board[r, c] == piece and self.board[r+1, c+1] == piece and self.board[r+2, c+2] == piece and self.board[r+3, c+3] == piece:
                    return True

        # Check second diaganol
        for c in range(self.NB_COLUMNS-3):
            for r in range(3, self.NB_ROWS):
                if self.board[r, c] == piece and self.board[r-1, c+1] == piece and self.board[r-2, c+2] == piece and self.board[r-3, c+3] == piece:
                    return True
            
    def get_valid_locations(self):
        valid_locations = []
        for col in range(self.NB_COLUMNS):
            if self.is_valid_location(col):
                valid_locations.append(col)
        return valid_locations 
    
    def draw(self,sleep_time=0.25):
        w,h=np.shape(self.board)
        print('     ',end='')
        for i in range(h):print(i,'   ',end='')
        print('\n\n',end='')
        for i in range(w):
            print(w-i-1,'   ',end='')
            for j in range(h):
                if(self.board[w-i-1,j]==EMPTY) : print('-    ',  end='')
                if(self.board[w-i-1,j]==YELLOW )  : print('O    ', end='')
                if(self.board[w-i-1,j]==RED): print('X    ', end='')
            print('\n\n', end='')
        sleep(sleep_time)
        print('\n\n\n')


# In[17]:


class AI: 
   
    def __init__(self, color=RED, WIN=1e6, four_aligned=100., tree_aligned=5., two_aligned=2.,
                 one_alined=1., LOSE=-1e6,  opp_four_aligned=-100., opp_tree_aligned=-5., opp_two_aligned=-2.,
                 opp_one_alined=-1., level= 3, filename = None, dico = None):


        self.color = color
        if self.color == RED:
            self.opp_color = YELLOW
        else:
            self.opp_color = RED

        self.WIN = WIN
        self.four_aligned = four_aligned
        self.tree_aligned = tree_aligned
        self.two_aligned = two_aligned
        self.one_alined = one_alined
        self.LOSE = LOSE
        self.opp_four_aligned = opp_four_aligned
        self.opp_tree_aligned = opp_tree_aligned
        self.opp_two_aligned = opp_two_aligned
        self.opp_one_alined = opp_one_alined
        self.depth_max = 5

        self.level = level

        if (level == 1):
            self.depth_max = 4
            self.alea = 0.2
            self.forget_hori = .01
            self.forget_verti = .1
            self.forget_diag = .5
        if (level == 2):
            self.depth_max = 4
            self.alea = 0.2
            self.forget_hori = .01
            self.forget_verti = .02
            self.forget_diag = .2
        if (level == 3):
            self.depth_max = 4
            self.alea = 0.1
            self.forget_hori = .01
            self.forget_verti = .02
            self.forget_diag = .1
        if (level == 4):
            self.depth_max = 5
            self.alea = 0.2
            self.forget_hori = .01
            self.forget_verti = .02
            self.forget_diag = .04
        if (level == 5):
            self.depth_max = 6
            self.alea = 0.1
            self.forget_hori = 0
            self.forget_verti = 0
            self.forget_diag = 0

    #has to be update to return a dictionnary containing all the values of
    #the parametres of the current instance.
    def summarize(self, mode = 'dico'):
        pass

    #to change the level of the ai
    def set_level(self, level):
        self.level = level
        if (level == 1):
            self.depth_max = 4
            self.alea = 0.2
            self.forget_hori = .01
            self.forget_verti = .1
            self.forget_diag = .5
        if (level == 2):
            self.depth_max = 4
            self.alea = 0.2
            self.forget_hori = .01
            self.forget_verti = .02
            self.forget_diag = .2
        if (level == 3):
            self.depth_max = 4
            self.alea = 0.1
            self.forget_hori = .01
            self.forget_verti = .02
            self.forget_diag = .1
        if (level == 4):
            self.depth_max = 5
            self.alea = 0.2
            self.forget_hori = .01
            self.forget_verti = .02
            self.forget_diag = .04
        if (level == 5):
            self.depth_max = 6
            self.alea = 0.1

    #evaluate a window (block of 4 consecutive cells)
    def evaluate_window(self, window):

        score = 0

        #positive configarations
        # 4 aligned
        if window.count(self.color) == 4:
            score += self.four_aligned
        # 3 aligned and 1 empty cell (might be filled later in order to win)
        elif window.count(self.color) == 3 and window.count(EMPTY) == 1:
            score += self.tree_aligned
        # 2 aligned and 2 empty cells
        elif window.count(self.color) == 2 and window.count(EMPTY) == 2:
            score += self.two_aligned
        # 1 ai's piece and 3 empty cells
        elif window.count(self.color) == 1 and window.count(EMPTY) == 3:
            score += self.one_alined

        #negaitive configarations
        #=>posive for opponent
        if window.count(self.opp_color) == 4:
            score += self.opp_four_aligned
        if window.count(self.opp_color) == 3 and window.count(EMPTY) == 1:
            score += self.opp_tree_aligned
        elif window.count(self.opp_color) == 2 and window.count(EMPTY) == 2:
            score += self.opp_two_aligned
        elif window.count(self.opp_color) == 1 and window.count(EMPTY) == 3:
            score += self.opp_one_alined

        return score


    #evaluates the whole grid
    def score_position(self, board_object):
        score = 0

        #gives more points to well centered pieces
        center_array = [int(i) for i in list(
            board_object.board[:, board_object.NB_COLUMNS // 2])]
        center_count = center_array.count(self.color)
        score += center_count * 3

        # Score Horizontal : sum of scores of all the horizontal windows
        for r in range(board_object.NB_ROWS):
            row_array = [int(i) for i in list(board_object.board[r, :])]
            for c in range(board_object.NB_COLUMNS - 3):
                if np.random.rand() >= self.forget_hori:
                    window = row_array[c:c + 4]
                    score += self.evaluate_window(window)

        # Score Vertical : idem for vertical windows
        for c in range(board_object.NB_COLUMNS):
            col_array = [int(i) for i in list(board_object.board[:, c])]
            for r in range(board_object.NB_ROWS - 3):
                if np.random.rand() >= self.forget_verti:
                    window = col_array[r:r + 4]
                    score += self.evaluate_window(window)

        # Score on first diagonal : idem for the first type diagonal windows
        for r in range(board_object.NB_ROWS - 3):
            for c in range(board_object.NB_COLUMNS - 3):
                if np.random.rand() >= self.forget_diag:
                    window = [board_object.board[r + i, c + i]
                              for i in range(4)]
                    score += self.evaluate_window(window)

        # Score on first diagonal : idem for the first type diagonal windows
        for r in range(board_object.NB_ROWS - 3):
            for c in range(board_object.NB_COLUMNS - 3):
                if np.random.rand() >= self.forget_diag:
                    window = [board_object.board[r + 3 - i, c + i]
                              for i in range(4)]
                    score += self.evaluate_window(window)

        return score

    

    def score_position(self, board_object):
        score = 0

        ## Score center column
        center_array = [int(i) for i in list(board_object.board[:, board_object.NB_COLUMNS//2])]
        center_count = center_array.count(self.color)
        score += center_count * 3

        ## Score Horizontal
        for r in range(board_object.NB_ROWS):
            row_array = [int(i) for i in list(board_object.board[r,:])]
            for c in range(board_object.NB_COLUMNS-3):
                window = row_array[c:c+board_object.WINDOW_LENGTH]
                score += self.evaluate_window(window)

        ## Score Vertical
        for c in range(board_object.NB_COLUMNS):
            col_array = [int(i) for i in list(board_object.board[:,c])]
            for r in range(board_object.NB_ROWS-3):
                window = col_array[r:r+board_object.WINDOW_LENGTH]
                score += self.evaluate_window(window)

        ## Score positive sloped diagonal
        for r in range(board_object.NB_ROWS-3):
            for c in range(board_object.NB_COLUMNS-3):
                window = [board_object.board[r+i, c+i] for i in range(board_object.WINDOW_LENGTH)]
                score += self.evaluate_window(window)

        for r in range(board_object.NB_ROWS-3):
            for c in range(board_object.NB_COLUMNS-3):
                window = [board_object.board[r+3-i, c+i] for i in range(board_object.WINDOW_LENGTH)]
                score += self.evaluate_window(window)

        return score

    def is_terminal_node(self, board_object):
        return board_object.winning_move(self.color) or board_object.winning_move(self.opp_color) or         board_object.get_valid_locations() == []
    
    def minimax(self, board_object, depth, maximizingPlayer = True, alpha=-np.inf, beta=np.inf):
        valid_locations = board_object.get_valid_locations()
        is_terminal = self.is_terminal_node(board_object)
        if depth == 0 or is_terminal:
            if is_terminal:
                if board_object.winning_move(self.color):
                    return (None, self.WIN)
                elif board_object.winning_move(self.opp_color):
                    return (None, self.LOSE)
                else: # Equality
                    return (None, 0)
            else: # Depth is zero
                return (None, self.score_position(board_object))
            
        if maximizingPlayer:
            value = -np.inf
            column = np.random.choice(valid_locations)
            for col in valid_locations:
                row = board_object.get_next_open_row(col)
                b_copy =  board_object.copy()
                b_copy.drop_piece(row, col, self.color)
                new_score = self.minimax(b_copy, depth = depth-1, maximizingPlayer = False, alpha=alpha, beta=beta)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value

        else: # Minimizing player
            value = np.inf
            column = np.random.choice(valid_locations)
            for col in valid_locations:
                row = board_object.get_next_open_row(col)
                b_copy = board_object.copy()
                b_copy.drop_piece(row, col, self.opp_color)
                new_score = self.minimax(b_copy, depth = depth-1, maximizingPlayer = True, alpha=alpha, beta=beta)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value
        
    def play(self, board_object):
        sleep(.25)
        
        v=np.random.rand()
        if v < self.alea : col = np.random.choice(board_object.get_valid_locations())
        else : col, minimax_score = self.minimax(board_object, self.depth_max)
        row = board_object.get_next_open_row(col)
        board_object.drop_piece(row, col, self.color)

        board_object.draw() 
        sleep(.25)
        return 


# In[12]:


class Player:
    
    def __init__(self, color = YELLOW):
        self.color = color
        
    def play(self, board_object):
        col=9
        while not board_object.is_valid_location(col):
            try : col = int(input("Enter a valid colum : "))
            except : pass
                
        row = board_object.get_next_open_row(col)
        board_object.drop_piece(row, col, self.color)
            
        board_object.draw() 

        return  


# In[19]:


def main():
    board_object = Board()
    starter = -1
    while starter != 0 and starter != 1 :
        try : starter = int(input('Who starts YOU or AI [0/1] ? : '))
        except : pass
    valid_levels = [0, 1, 2, 3, 4, 5, 666]
    level = -1
    while level not in valid_levels :
        try : level = int(input('Choose the level of the AI [1-->5] ? : '))
        except : pass
    
    
    game_over = False
    board_object.draw()
    if starter == 0: 
        player1 = Player()
        player2 = AI(level = level)
    else :
        player1 = AI(level = level)
        player2 = Player()
    
    want_to_play = True 
    
    while want_to_play :
        while not game_over:
            player1.play(board_object)
            if board_object.winning_move(player1.color):
                print("Player 1 wins!!")
                game_over = True
            elif board_object.get_valid_locations() == [] :
                print('equality')
                game_over = True
            if(not game_over) : 
                player2.play(board_object)
                if board_object.winning_move(player2.color):
                    game_over = True
                elif board_object.get_valid_locations() == [] :
                    print('equality')
                    game_over = True

        ans = ''
        while ans not in ['y', 'n'] :
            try : ans = input('Play again [y,n] ? : ')
            except : pass
        if ans == 'n' : want_to_play = False
        else :
            while ans not in ['y', 'n'] :
                try : ans = input('With same conditions [y, n] ? : ')
                except : pass
            if ans == 'n':
                starter = -1
                while starter != 0 and starter != 1 :
                    try : starter = int(input('Who starts YOU or AI [0/1] ? : '))
                    except : pass
                valid_levels = [0, 1, 2, 3, 4, 5]
                level = -1
                while level not in valid_levels :
                    try : level = int(input('Choose the level of the AI [1-->5 or troll levels] ? : '))
                    except : pass
    
    return 


# In[18]:


if __name__ == '__main__':
    main()

