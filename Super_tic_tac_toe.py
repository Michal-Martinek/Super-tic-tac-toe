import pygame

WIDTH = 720
HEIGHT = 770
BOARD_Y = 50
CELL_SIZE = WIDTH // 9

CELL_INNER_SIZE = int(CELL_SIZE * 3/4)
CELL_PADDING = (CELL_SIZE - CELL_INNER_SIZE) // 2
MARK_THICKNESS = 5
BIG_MARK_THICKESS_ADD = 8


HEADER_LINE_THICKNESS = 5
BIG_LINE_THICKNESS = 3
SMALL_LINE_THICKNESS = 1

LINE_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (0, 0, 0)
SHADOW_MARK_COLOR = (128, 128, 128)

MENU_HEADER_RECT = pygame.Rect(100, 70, WIDTH-200, 100)
MENU_BUTTON_WIDTH = 150
MENU_BUTTON_RECTS = [pygame.Rect(WIDTH//2 - MENU_BUTTON_WIDTH//2, 250, MENU_BUTTON_WIDTH, 80),  pygame.Rect(WIDTH//2 - MENU_BUTTON_WIDTH//2, 380, MENU_BUTTON_WIDTH, 80)]

FPS = 60

pygame.init()
FONT = pygame.font.SysFont('arial', int(BOARD_Y * 3/4))
HEADER_FONT = pygame.font.SysFont('arial', 80)
HEADER_TEXT_POS = (WIDTH // 4, BOARD_Y // 6)


def renderText(display, color, pos, text, font=FONT):
	label = font.render(text, 1, color)
	display.blit(label, pos)
def renderTextInRect(display, color, rect, text, font=FONT, backgroundColor=None, boundaryColor=None, boundaryThickness=3):
	label = font.render(text, 1, color)
	pos = pygame.Rect(0, 0, label.get_width(), label.get_height())
	pos.center = rect.center
	if backgroundColor: pygame.draw.rect(display, backgroundColor, rect)
	if boundaryColor: pygame.draw.rect(display, boundaryColor, rect, boundaryThickness)
	display.blit(label, pos)

class SmallBoard:
	def __init__(self, row=0, col=0):
		self.board: list[list[int]] = [[0] * 3 for i in range(3)] # 0 - unplayed, 1 - first, 2 - second
		self.row = row
		self.col = col
		self.won = 0 # 0, 1, 2
	
	def makeMove(self, X, Y, move) -> bool:
		assert not self.won, 'cannot make moves to won sub-boards'
		self.board[Y][X] = move
		self.won = self.isWon()
		return self.won
	def isWon(self) -> int:
		for i in range(3):
			row = all([tile == self.board[i][0] for tile in self.board[i]]) and self.board[i][0]
			col = all([self.board[j][i] == self.board[0][i] for j in range(3)]) and self.board[0][i]
			if row or col: return row or col
		dia1 = self.board[0][0] == self.board[1][1] == self.board[2][2]
		dia2 = self.board[0][2] == self.board[1][1] == self.board[2][0]
		return (dia1 and self.board[0][0]) or (dia2 and self.board[0][2])
	def getFree(self, Xoff=0, Yoff=0) -> set[tuple[int, int]]:
		if self.won: return set()
		return set([(x + Xoff * 3, y + Yoff * 3) for x in range(3) for y in range(3) if self.board[y][x] == 0])

	@ staticmethod
	def _drawFirst(display, pos, shadow=False, big=False): # cross
		endOff = CELL_SIZE - CELL_PADDING if not big else 3 * CELL_SIZE - CELL_PADDING
		points = [(pos[0] + Xoff, pos[1] + Yoff) for Yoff in (CELL_PADDING, endOff) for Xoff in (CELL_PADDING, endOff)]
		color = (255, 0, 0) if not shadow else SHADOW_MARK_COLOR
		pygame.draw.line(display, color, points[0], points[-1], MARK_THICKNESS + big * BIG_MARK_THICKESS_ADD)
		pygame.draw.line(display, color, points[1], points[2], MARK_THICKNESS + big * BIG_MARK_THICKESS_ADD)
	@ staticmethod
	def _drawSecond(display, pos, shadow=False, big=False): # circle
		pos = pos[0] + CELL_SIZE // 2, pos[1] + CELL_SIZE // 2
		if big: pos = pos[0] + CELL_SIZE, pos[1] + CELL_SIZE
		radius = CELL_INNER_SIZE // 2 if not big else CELL_SIZE * 3 // 2 - CELL_PADDING
		pygame.draw.circle(display, (0, 0, 255) if not shadow else SHADOW_MARK_COLOR, pos, radius, MARK_THICKNESS)

	def draw(self, display, opened: set[tuple[int, int]]):
		pos = self.col * CELL_SIZE * 3, self.row * CELL_SIZE * 3 + BOARD_Y
		for y, cells in enumerate(self.board):
			for x, cell in enumerate(cells):
				cellPos = pos[0] + x * CELL_SIZE, pos[1] + y * CELL_SIZE
				if cell == 1:
					self._drawFirst(display, cellPos, self.won)
				elif cell == 2:
					self._drawSecond(display, cellPos, self.won)
				elif (x + self.col * 3, y + self.row * 3) in opened:
					pygame.draw.rect(display, (5, 91, 115), (pos[0] + CELL_SIZE * x + CELL_PADDING, pos[1] + CELL_SIZE * y + CELL_PADDING, CELL_INNER_SIZE, CELL_INNER_SIZE))
		if self.won:
			(self._drawFirst, self._drawSecond)[self.won-1](display, (self.col * CELL_SIZE * 3, self.row * CELL_SIZE * 3 + BOARD_Y), big=True)

class Board:
	def __init__(self):
		self.board: list[list[SmallBoard]] = [[SmallBoard(row, col) for col in range(3)] for row in range(3)]
		self.openSubBoard = (-1, -1) # open all
		self.opened: set[tuple[int, int]] = self.getOpened()
		self.won = 0 # 0, 1, 2

	def getOpened(self) -> set[tuple[int, int]]:
		if self.openSubBoard != (-1, -1):
			opened = self.board[self.openSubBoard[1]][self.openSubBoard[0]].getFree(*self.openSubBoard)
		if self.openSubBoard == (-1, -1) or len(opened) == 0:
			self.openSubBoard = (-1, -1)
			opened = set()
			for x in range(3):
				for y in range(3):
					opened = opened.union(self.board[y][x].getFree(x, y))
		return opened
	def checkWholeWin(self):
		board = SmallBoard()
		board.board = [[b.won for b in line] for line in self.board]
		return board.isWon()
	def makeMove(self, pos: tuple[int, int], move) -> tuple[bool, int]:
		if free := (pos in self.opened):
			won = self.board[pos[1] // 3][pos[0] // 3].makeMove(pos[0] % 3, pos[1] % 3, move)
			if won:
				self.won = self.checkWholeWin()
			self.openSubBoard = pos[0] % 3, pos[1] % 3
			if self.board[pos[1] % 3][pos[0] % 3].won: self.openSubBoard = (-1, -1)
			self.opened = self.getOpened()
		return free, self.won

	def drawLines(self, display, pos=(0, 0), big=True):
		if big: pygame.draw.line(display, LINE_COLOR, (0, BOARD_Y), (WIDTH, BOARD_Y), HEADER_LINE_THICKNESS)
		for i in range(3):
			cellSize = WIDTH // 3 if big else WIDTH // 9			
			drawPos = pos[0] * WIDTH // 3 + cellSize * i, pos[1] * WIDTH // 3 + cellSize * i + BOARD_Y
			thickness = BIG_LINE_THICKNESS if big else SMALL_LINE_THICKNESS
			pygame.draw.line(display, LINE_COLOR, (0, drawPos[1]), (WIDTH, drawPos[1]), thickness) # horizontal
			pygame.draw.line(display, LINE_COLOR, (drawPos[0], BOARD_Y), (drawPos[0], HEIGHT), thickness) # vertical
			if big:
				for j in range(3):
					self.drawLines(display, (i, j), False)
	def draw(self, display):
		self.drawLines(display)
		for line in self.board:
			for board in line:
				board.draw(display, self.opened)

class Game:
	def __init__(self):
		self.board = Board()
		self.playerOnTurn: int = 1 # 1, 2
		self.won = 0 # 0, 1, 2

	def _getClickPos(self, mousePos):
		if mousePos[1] < BOARD_Y: return (-1, -1)
		return (mousePos[0] // CELL_SIZE, (mousePos[1] - BOARD_Y) // CELL_SIZE)
	def click(self, mousePos) -> bool:
		pos = self._getClickPos(mousePos)
		if pos == (-1, -1): return False
		sucess, won = self.board.makeMove(pos, self.playerOnTurn)
		if sucess:
			if won: self.won = won
			self.advancePlayer()
		return sucess
	def advancePlayer(self):
		self.playerOnTurn = 3 - self.playerOnTurn
	def draw(self, display):
		self.board.draw(display)
		headerText = f'{("First", "Second")[self.playerOnTurn == 2]} player on turn!'
		renderText(display, LINE_COLOR, HEADER_TEXT_POS, headerText)

def menu(display: pygame.Surface) -> int: # modes: 0 - exit, 1 - PvP, 2 - vs ai
	display.fill(BACKGROUND_COLOR)
	renderTextInRect(display, (255, 0, 0), MENU_HEADER_RECT, 'Super-tic-tac-toe', HEADER_FONT)
	renderTextInRect(display, (0, 0, 0), MENU_BUTTON_RECTS[0], 'PvP', FONT, (255, 255, 255), (0, 0, 255))
	renderTextInRect(display, (0, 0, 0), MENU_BUTTON_RECTS[1], 'PvAi', FONT, (255, 255, 255), (0, 0, 255))
	pygame.display.update()

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return 0
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					if MENU_BUTTON_RECTS[0].collidepoint(event.pos):
						return 1
					if MENU_BUTTON_RECTS[1].collidepoint(event.pos):
						return 2
		pygame.time.Clock().tick(FPS)
def winScreen(display: pygame.Surface, won: int):
	assert won in [1, 2]
	display.fill(BACKGROUND_COLOR)
	renderTextInRect(display, (255, 255, 255), MENU_HEADER_RECT, f'{["First", "Second"][won-1]} player won!!', HEADER_FONT)
	renderText(display, (255, 0, 0), (200, 500), 'Click to exit...')
	pygame.display.update()

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
			elif event.type == pygame.MOUSEBUTTONDOWN:
				return
		pygame.time.Clock().tick(FPS)

def game(display: pygame.Surface, mode: int) -> int:	
	game = Game()
	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					game.click(event.pos)
		
		if game.won:
			running = False
		else:
			display.fill(BACKGROUND_COLOR)
			game.draw(display)
			pygame.display.update()
			pygame.time.Clock().tick(FPS)
	return game.won

def main():
	display = pygame.display.set_mode((WIDTH, HEIGHT))
	mode = menu(display)
	if mode == 0: return
	won = game(display, mode)
	winScreen(display, 2)

if __name__ == '__main__':
	main()
