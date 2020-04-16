#!/usr/bin/env python
# coding: utf-8
#
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from time import sleep
import PIL.Image as pil_image
from PIL import ImageDraw

from os import system
from os.path import exists

from os import remove as remove_file
import numpy as np
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scatter import Scatter
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color
from kivy.app import App


################################################################################
#Declaration of global variables : size of the board, values representing
#red and yellow tokens, empty box and the pictures corresponding to the grid,
#the tokens and the background.
#This pictures are in rgba format, regular color picture plus a fourth channel
#alpha that represent the transparancy. This will be crucial crucial for
#compositing the images to be displayed on the screen

NB_ROWS = 6
NB_COLUMNS = 7
EMPTY = -1
YELLOW = 0
RED = 1

pil_bg_or = pil_image.open('images/background.png')
pil_grid = pil_image.open('images/grid.png')
pil_yellow = (pil_image.open(
	'images/yellow_token.png')).resize((50, 50))
pil_red = (pil_image.open(
	'images/red_token.png')).resize((50, 50))


################################################################################
#this class manages the grid itself: the placement of the pieces, the detection
#of winning moves, the display etc.

class Board:

	#static variable used to number the files of the images to display.
	i = 0

	#the constructor of the class
	def __init__(self, NB_ROWS=6, NB_COLUMNS=7):
		Board.i+=1
		self.NB_ROWS = NB_ROWS
		self.NB_COLUMNS = NB_COLUMNS
		self.EMPTY = EMPTY
		self.YELLOW = YELLOW
		self.RED = RED
		#the board it-self : a numpy arry with NB_ROWS rows and NB_COLUMNS
		#columns  of which all the cells are marked as empty
		self.board = np.ones((self.NB_ROWS, self.NB_COLUMNS)) * self.EMPTY

	#returns a copy of the current instance of the class
	def copy(self):
		new_board = Board(NB_ROWS=self.NB_ROWS, NB_COLUMNS=self.NB_COLUMNS)
		new_board.board = self.board.copy()
		return new_board

	#drops a piece (red or yellow) at the given position without verifications
	def drop_piece(self, row, col, piece):
		self.board[row, col] = piece

	#returns True if the column col is not full, ie if we could push another
	#piece
	def is_valid_location(self, col):
		if (col < 0 or col > self.NB_COLUMNS):
			return False
		else:
			return self.board[self.NB_ROWS - 1, col] == self.EMPTY

	#returns the next empty row of the column col of the board or None if there
	#aren't empty cell.
	def get_next_open_row(self, col):
		try:
			for r in range(self.NB_ROWS):
				if self.board[r, col] == self.EMPTY:
					return r
			return None
		except:
			return None


	#returns True if there are four aligned token of the color piece in 'bool'
	#mode or the positions of the winning chips.
	def winning_move(self, piece, mode = 'bool'):

		# Check horizontal locations
		for c in range(self.NB_COLUMNS - 3):
			for r in range(self.NB_ROWS):
				if self.board[r, c] == piece and self.board[r, c + 1] == piece and self.board[r, c + 2] == piece and self.board[r, c + 3] == piece:
					if mode == 'bool' : return True
					else : return [(r, c), (r, c + 3)]

		# Check vertical locations
		for c in range(self.NB_COLUMNS):
			for r in range(self.NB_ROWS - 3):
				if self.board[r, c] == piece and self.board[r + 1, c] == piece and self.board[r + 2, c] == piece and self.board[r + 3, c] == piece:
					if mode == 'bool' : return True
					else : return [(r, c), (r + 3, c)]

		# Check first diaganol
		for c in range(self.NB_COLUMNS - 3):
			for r in range(self.NB_ROWS - 3):
				if self.board[r, c] == piece and self.board[r + 1, c + 1] == piece and self.board[r + 2, c + 2] == piece and self.board[r + 3, c + 3] == piece:
					if mode == 'bool' : return True
					else : return [(r, c), (r + 3, c+3)]

		# Check second diaganol
		for c in range(self.NB_COLUMNS - 3):
			for r in range(3, self.NB_ROWS):
				if self.board[r, c] == piece and self.board[r - 1, c + 1] == piece and self.board[r - 2, c + 2] == piece and self.board[r - 3, c + 3] == piece:
					if mode == 'bool' : return True
					else : return [(r, c), (r - 3, c+3)]

		if mode == 'bool' : return False
		else : return   [(0, 0), (0, 0)]

	#returns the list of the not full columns
	def get_valid_locations(self):
		valid_locations = []
		for col in range(self.NB_COLUMNS):
			if self.is_valid_location(col):
				valid_locations.append(col)
		return valid_locations

	#generates the image to display every time someone plays
	#the idea is to push the tokens before the grid for a better visual
	#appearance
	def draw(self, game_over = False):
		global pil_bg_or, pil_grid, pil_yellow, pil_red
		pil_bg = pil_bg_or.copy()

		for i in range(self.NB_ROWS):
			for j in range(self.NB_COLUMNS):
				if(self.board[i, j] == YELLOW):
					pil_bg.paste(pil_yellow,  (129 + j * 56, 340 - i * 60), pil_yellow)
				if(self.board[i, j] == RED):
					pil_bg.paste(pil_red,   (129 + j * 56, 340 - i * 60), pil_red)

		pil_bg.paste(pil_grid, (0, 0), pil_grid)

		#if the game is over, print a line on the winning tokens to make them more visible
		if game_over :
			for piece in [self.YELLOW, self.RED ]:
				if piece == self.YELLOW : fill = (255,   5,   5, 102)
				if piece == self.RED    : fill = (255, 255,  13, 102)
				pre_coords = self.winning_move(piece, mode = 'coords')
				img1 = ImageDraw.Draw(pil_bg)
				coords = [(155 + pre_coords[0][1] * 56, 366 - pre_coords[0][0] * 60),\
						  (155 + pre_coords[1][1] * 56, 366 - pre_coords[1][0] * 60)]
				img1.line(coords, fill = (0, 0, 0, 200), width = 5)

		#remove last file to free the memory
		try:
			remove_file('.\\images\\to_disp' + str(Board.i-1) + '.png')
		except:
			pass


		filename = '.\\images\\to_disp' + str(Board.i) + '.png'
		pil_bg.save(filename, "PNG")
		print('image stored in  ', filename)

		return filename



################################################################################
#this handle the artificial intelligence of the game


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

	#returns true if  the grid is full or if someone wins
	def is_terminal_node(self, board_object):
		return board_object.winning_move(self.color) or board_object.winning_move(self.opp_color) or \
		board_object.get_valid_locations() == []

	#Minimax algorithm with alpha beta pruning
	def minimax(self, board_object, depth, maximizingPlayer=True, alpha=-np.inf, beta=np.inf):

		#check if we have to continue recursivity or not
		#if not : return  the evaluation of the board

		if  self.is_terminal_node(board_object):
			if board_object.winning_move(self.color):
				return (None, (self.depth_max - depth) * self.WIN)
			elif board_object.winning_move(self.opp_color):
				return (None, (self.depth_max - depth) *self.LOSE)
			else:  # Equality
				return (None, 0)

		if depth == 0:  # Depth is zero
			return (None, self.score_position(board_object))


		valid_locations = board_object.get_valid_locations()

		#step consisting in maximising the score of the current player (ie the ai)
		if maximizingPlayer:
			value = -np.inf #initialise the minimum score that the ai is assured
			column = np.random.choice(valid_locations) #choose randomly a valid column

			#loop on all possible shots
			for col in valid_locations:

				#play the shot
				row = board_object.get_next_open_row(col)
				b_copy = board_object.copy()
				b_copy.drop_piece(row, col, self.color)

				#continue recursivity or randomly ignores some branches (to make the ai les good)
				if depth > self.depth_max//2 or np.random.rand() >= self.alea:
					new_score = self.minimax(
						b_copy, depth=depth - 1, maximizingPlayer=False, alpha=alpha, beta=beta)[1]
				else : new_score = self.score_position(b_copy)

				#keep best shot
				if new_score > value:
					value = new_score
					column = col
				alpha = max(alpha, value)

				#the maximum score that the minimizing player is assured of becomes less than
				#the minimum score that the maximizing player is assured =>don't need to consider
				#further descendants of this node
				if alpha >= beta:
					break
			return column, value

		#step consisting in minimising the score of the adversary
		else:
			value = np.inf #initialise the maximum score that the challenger is assured
			column = np.random.choice(valid_locations)  #choose randomly a valid column

			#loop on all possible shots
			for col in valid_locations:

				#play the shot
				row = board_object.get_next_open_row(col)
				b_copy = board_object.copy()
				b_copy.drop_piece(row, col, self.opp_color)

				#continue recursivity or randomly ignores some branches (to make the ai les good)
				if depth > self.depth_max//2 or np.random.rand() >= self.alea:
					new_score = self.minimax(
						b_copy, depth=depth - 1, maximizingPlayer=True, alpha=alpha, beta=beta)[1]
				else : new_score = self.score_position(b_copy)

				#keep worst shot from the point of ia
				if new_score < value:
					value = new_score
					column = col

				#the maximum score that the minimizing player is assured of becomes less than
				#the minimum score that the maximizing player is assured =>don't need to consider
				#further descendants of this node
				beta = min(beta, value)
				if alpha >= beta:
					break

			return column, value

	def play(self, board_object):

		col, minimax_score = self.minimax(board_object, self.depth_max)
		row = board_object.get_next_open_row(col)
		board_object.drop_piece(row, col, self.color)

		return

	def set_color(self, color):
		self.color = color
		if self.color == RED:
			self.opp_color = YELLOW
		else:
			self.opp_color = RED



################################################################################
#an insistance of this class reprensents a human player


class Player:

	def __init__(self, color=YELLOW):
		self.color = color

	def set_color(self, color):
		self.color = color



################################################################################



class Connect_4(App):

	def build(self):

		self.player1 = Player()
		self.player2 = AI()
		self.board = Board()
		self.list_bords = [self.board.copy()]
		self.turn = 0
		self.game_over = False


		self.root = BoxLayout(orientation='vertical')

################################################################################

		self.intro_main_Box = BoxLayout(orientation='vertical')
		self.intro_Box1 = BoxLayout(orientation='vertical', size_hint=(1, .6))
		self.intro_Box2 = BoxLayout(orientation='horizontal', size_hint=(.1, .3))
		self.intro_Box3 = BoxLayout(orientation='horizontal', size_hint=(1, .1))

		self.intro_Box1.add_widget(Image(source='images/start.png'))
		self.intro_main_Box.add_widget(self.intro_Box1)


		self.intro_main_Box.add_widget(self.intro_Box2)

		self.spinner1 = Spinner(
			values=('AI vs Player', 'Player vs AI', '2 Players'),
			size_hint=(.27, 1),
			text='Select the number of player(s)')
		self.spinner1.bind(text=self.on_spinner1)
		self.intro_Box3.add_widget(self.spinner1)

		self.spinner2 = Spinner(
			values=('Yellow', 'Red'),
			size_hint=(.27, 1),
			text='Select the color of the tokens \nof the first player')
		self.spinner2.bind(text=self.on_spinner2)
		self.intro_Box3.add_widget(self.spinner2)

		self.spinner3 = Spinner(
			values=('1', '2', '3', '4', '5'),
			size_hint=(.27, 1),
			text='Select the level of the AI')
		self.spinner3.bind(text=self.on_spinner3)
		self.intro_Box3.add_widget(self.spinner3)

		self.intro_Box3.add_widget(Label(text='', size_hint=(.09, 1)))

		self.btn_intro = Button(text='Enter', size_hint=(.1, 1))
		self.btn_intro.bind(on_release=self.clear)
		self.intro_Box3.add_widget(self.btn_intro)

		self.intro_main_Box.add_widget(self.intro_Box3)
		self.root.add_widget(self.intro_main_Box)

################################################################################

		self.main_Box = BoxLayout(orientation='vertical')
		self.Box1 = BoxLayout(orientation='vertical', size_hint=(1, .9))
		self.Box2 = BoxLayout(orientation='horizontal', size_hint=(1, .1))

		image = Image(source='images/beginning.png')
		self.Box1.add_widget(image)
		self.label = Label(text="Enter a valid column : ", size_hint=(.27, 1))
		self.label2 = Label(text="", size_hint=(.06, 1))
		self.col_input = BoxLayout(
			orientation='horizontal', size_hint=(.54, 1))

################################################################################

		self.btn_0 = Button(text='1')
		self.btn_0.bind(on_release=self.zero)

		self.btn_1 = Button(text='2')
		self.btn_1.bind(on_release=self.one)

		self.btn_2 = Button(text='3')
		self.btn_2.bind(on_release=self.two)

		self.btn_3 = Button(text='4')
		self.btn_3.bind(on_release=self.three)

		self.btn_4 = Button(text='5')
		self.btn_4.bind(on_release=self.four)

		self.btn_5 = Button(text='6')
		self.btn_5.bind(on_release=self.five)

		self.btn_6 = Button(text='7')
		self.btn_6.bind(on_release=self.six)

		self.col_input.add_widget(self.btn_0)
		self.col_input.add_widget(self.btn_1)
		self.col_input.add_widget(self.btn_2)
		self.col_input.add_widget(self.btn_3)
		self.col_input.add_widget(self.btn_4)
		self.col_input.add_widget(self.btn_5)
		self.col_input.add_widget(self.btn_6)

		self.Box2.add_widget(self.label)
		self.Box2.add_widget(self.col_input)
		self.Box2.add_widget(self.label2)

################################################################################

		self.btn_ai = Button(text='AI')
		self.btn_ai.bind(on_release=self.ai_play)

		self.btn_undo = Button(text='undo', size_hint=(.1, 1))
		self.btn_undo.bind(on_release=self.undo)
		self.Box2.add_widget(self.btn_undo)

		self.btn_menu = Button(text='Menu', size_hint=(.1, 1))
		self.btn_menu.bind(on_release=self.menu)
		self.Box2.add_widget(self.btn_menu)

		self.main_Box.add_widget(self.Box1)
		self.main_Box.add_widget(self.Box2)

################################################################################

		self.popup_Box = BoxLayout(orientation='vertical')
		self.popup_btn_menu = Button(text='Play again', font_size='20sp',
										background_normal='',
										 background_color=[.6, .6, .6, 1])
		self.popup_btn_menu.bind(on_release=self.menu)
		self.popup_Box.add_widget(self.popup_btn_menu)

		self.popup = Popup(title='End of party', content=self.popup_Box,
						   auto_dismiss=True, size_hint=(.4, .25),
						    pos_hint={'right': .7, 'top': .25}, title_size='30sp',
							 separator_color=[.0, .0, .0, 1])


		return self.root

################################################################################

	def draw(self):
		filename = self.board.draw(self.game_over)
		image = Image(source = filename)
		remove_file(filename)
		for child in self.Box1.children:
			self.Box1.remove_widget(child)

		self.Box1.add_widget(image)

################################################################################

	def clear(self, obj):
		self.root.remove_widget(self.intro_main_Box)
		self.root.add_widget(self.main_Box)

		if isinstance(self.player1, AI) and not isinstance(self.player2, AI):
			self.player1.play(self.board)
			self.draw()



################################################################################

	def menu(self, obj):
		try:
			self.root.remove_widget(self.main_Box)
			self.root.add_widget(self.intro_main_Box)
		except:
			pass
		for i in range(self.board.i+2):
			path = '.\\images\\to_disp' + str(i) + '.png'
			if exists(path) : remove_file(path)

		for child in self.Box1.children:
			self.Box1.remove_widget(child)

		self.Box1.add_widget(Image(source='images/beginning.png'))

		i = self.board.i
		del self.board.board
		del self.board
		del self.list_bords

		self.board = Board()
		self.list_bords = [self.board.copy()]

		self.board.i = i
		self.game_over = False

################################################################################

	def ai_play(self,obj):

		if self.turn == 0 and not self.game_over and isinstance(self.player1, AI):

			self.player1.play(self.board)
			self.list_bords.append(self.board.copy())
			self.draw()


			if self.board.winning_move(self.player1.color):
				print("Player 1 wins!")
				self.game_over = True
				self.draw()
				self.popup.title = "Player 1 wins!"

				if self.player1.color == RED:
					self.popup.title_color = [1, .02, .02, .4]
				else:
					self.popup.title_color = [1, 1, .05, .4]

				self.popup.open()
			self.turn = 1 - self.turn


		if self.turn == 1 and not self.game_over and isinstance(self.player2, AI):

			self.player2.play(self.board)
			self.list_bords.append(self.board.copy())
			self.draw()

			if self.board.winning_move(self.player2.color):
				print("Player 2 wins!")
				self.game_over = True
				self.draw()
				self.popup.title = "Player 2 wins!"

				if self.player2.color == RED:
					self.popup.title_color = [1, .02, .02, .4]
				else:
					self.popup.title_color = [1, 1, .05, .4]

				self.popup.open()

			self.turn = 1 - self.turn

		sleep(1.)

	################################################################################

	def PLAY(self, col):

		if self.game_over:
			self.popup.open()

		if not self.game_over:

			if (self.turn == 0 and isinstance(self.player1, Player)):

				row = self.board.get_next_open_row(col)
				self.board.drop_piece(row, col, self.player1.color)
				self.list_bords.append(self.board.copy())

				if self.board.winning_move(self.player1.color):
					print("Player 1 wins!")
					self.game_over = True

					self.draw()

					self.popup.title = "Player 1 wins!"
					if self.player1.color == RED:
						self.popup.title_color = [1, .02, .02, 1]
					else:
						self.popup.title_color = [1, 1, .05, 1]

					self.popup.open()

				else:
					self.draw()

				if not self.game_over :
					self.btn_ai.trigger_action()

			if (self.turn == 1 and isinstance(self.player2, Player) and not self.game_over):

				row = self.board.get_next_open_row(col)
				self.board.drop_piece(row, col, self.player2.color)
				self.list_bords.append(self.board.copy())

				if self.board.winning_move(self.player2.color):
					print("Player 2 wins!")
					self.game_over = True

					self.draw()

					self.popup.title = "Player 2 wins!"
					if self.player2.color == RED:
						self.popup.title_color = [1, .02, .02, 1]
					else:
						self.popup.title_color = [1, 1, .05, 1]

					self.popup.open()

				else:
					self.draw()

				if not self.game_over :
					self.btn_ai.trigger_action()

			self.turn = 1 - self.turn
		return

################################################################################

	def undo(self,obj):

		try :
			del self.list_bords[-1]
			self.board = self.list_bords[-1]
			self.game_over = False
			self.turn = 1 - self.turn
			if  self.turn == 1 and not self.game_over and isinstance(self.player2, AI) or \
				self.turn == 0 and not self.game_over and isinstance(self.player1, AI):

				del self.list_bords[-1]
				self.board = self.list_bords[-1]
				self.game_over = False
				self.turn = 1 - self.turn

		except:
			print('Error undo')
			self.board = Board()
			self.list_bords = [self.board.copy()]
			self.turn = 0

		self.draw()

################################################################################

	def zero(self, obj): self.PLAY(0)

	def one(self, obj): self.PLAY(1)

	def two(self, obj):  self.PLAY(2)

	def three(self, obj): self.PLAY(3)

	def four(self, obj):  self.PLAY(4)

	def five(self, obj):  self.PLAY(5)

	def six(self, obj):  self.PLAY(6)

################################################################################

	def on_spinner1(self, spinner, text):
		values = ('AI vs Player', 'Player vs AI', '2 Players')
		val = self.spinner1.text
		if val == values[0]:
			self.player1 = AI()
			self.player2 = Player()
		if val == values[1]:
			self.player1 = Player()
			self.player2 = AI()
		if val == values[2]:
			self.player1 = Player(color=YELLOW)
			self.player2 = Player(color=RED)

################################################################################

	def on_spinner2(self, spinner, text):
		values = ('Yellow', 'Red')
		val = self.spinner2.text
		if val == values[0]:
			self.player1.set_color(YELLOW)
			self.player2.set_color(RED)
		if val == values[1]:
			self.player1.set_color(RED)
			self.player2.set_color(YELLOW)

################################################################################

	def on_spinner3(self, spinner, text):
		val = self.spinner3.text
		if isinstance(self.player1, AI):
			self.player1.set_level(int(val))
		if isinstance(self.player2, AI):
			self.player2.set_level(int(val))

################################################################################

if __name__ == '__main__':
	Connect_4().run()
