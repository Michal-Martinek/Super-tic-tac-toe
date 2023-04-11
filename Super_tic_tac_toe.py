import pygame

WIDTH = 720
HEIGHT = 770
BOARD_Y = 50
CELL_SIZE = WIDTH // 9

CELL_INNER_SIZE = int(CELL_SIZE * 3/4)
MARK_THICKNESS = 5

HEADER_LINE_THICKNESS = 5
BIG_LINE_THICKNESS = 3
SMALL_LINE_THICKNESS = 1

LINE_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (0, 0, 0)

FPS = 60

pygame.init()
FONT = pygame.font.SysFont('arial', int(BOARD_Y * 3/4))
HEADER_TEXT_POS = (WIDTH // 4, BOARD_Y // 6)


def renderText(display, color, pos, text):
	label = FONT.render(text, 1, color)
	display.blit(label, pos)

class SmallBoard:
	def __init__(self, row=0, col=0):
		self.board: list[list[int]] = [[0] * 3 for i in range(3)] # 0 - unplayed, 1 - first, 2 - second
		self.row = row
		self.col = col
	
	def getFree(self, Xoff=0, Yoff=0) -> set[tuple[int, int]]:
		return set([(x + Xoff * 3, y + Yoff * 3) for x in range(3) for y in range(3) if self.board[y][x] == 0])

	@ staticmethod
	def _drawFirst(display, pos): # cross
		points = [(pos[0] + Xoff, pos[1] + Yoff) for Yoff in (CELL_SIZE - CELL_INNER_SIZE, CELL_INNER_SIZE) for Xoff in (CELL_SIZE - CELL_INNER_SIZE, CELL_INNER_SIZE)]
		pygame.draw.line(display, (255, 0, 0), points[0], points[-1], MARK_THICKNESS)
		pygame.draw.line(display, (255, 0, 0), points[1], points[2], MARK_THICKNESS)
	@ staticmethod
	def _drawSecond(display, pos): # circle
		pos = pos[0] + CELL_SIZE // 2, pos[1] + CELL_SIZE // 2
		pygame.draw.circle(display, (0, 0, 255), pos, CELL_INNER_SIZE // 2, MARK_THICKNESS)

	def draw(self, display, opened: set[tuple[int, int]]):
		pos = self.col * CELL_SIZE * 3, self.row * CELL_SIZE * 3 + BOARD_Y
		for y, cells in enumerate(self.board):
			for x, cell in enumerate(cells):
				cellPos = pos[0] + x * CELL_SIZE, pos[1] + y * CELL_SIZE
				if cell == 1:
					self._drawFirst(display, cellPos)
				elif cell == 2:
					self._drawSecond(display, cellPos)
				elif (x + self.col * 3, y + self.row * 3) in opened:
					cellPadd = (CELL_SIZE - CELL_INNER_SIZE) // 2
					pygame.draw.rect(display, (5, 91, 115), (pos[0] + CELL_SIZE * x + cellPadd, pos[1] + CELL_SIZE * y + cellPadd, CELL_INNER_SIZE, CELL_INNER_SIZE))

class Board:
	def __init__(self):
		self.board: list[list[SmallBoard]] = [[SmallBoard(row, col) for col in range(3)] for row in range(3)]
		self.openSubBoard = (-1, -1) # open all
		self.opened: set[tuple[int, int]] = self.getOpened()

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

	def makeMove(self, pos: tuple[int, int], move) -> bool:
		if free := (pos in self.opened):
			self.board[pos[1] // 3][pos[0] // 3].board[pos[1] % 3][pos[0] % 3] = move
			self.openSubBoard = pos[0] % 3, pos[1] % 3
			self.opened = self.getOpened()
		return free

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

	def _getClickPos(self, mousePos):
		if mousePos[1] < BOARD_Y: return (-1, -1)
		return (mousePos[0] // CELL_SIZE, (mousePos[1] - BOARD_Y) // CELL_SIZE)
	def click(self, mousePos) -> bool:
		pos = self._getClickPos(mousePos)
		if pos == (-1, -1): return False
		if sucess := self.board.makeMove(pos, self.playerOnTurn):
			self.advancePlayer()
		return sucess
	def advancePlayer(self):
		self.playerOnTurn = 3 - self.playerOnTurn
	def draw(self, display):
		self.board.draw(display)
		headerText = f'{("First", "Second")[self.playerOnTurn == 2]} player on turn!'
		renderText(display, LINE_COLOR, HEADER_TEXT_POS, headerText)

def main():
	display = pygame.display.set_mode((WIDTH, HEIGHT))
	
	game = Game()

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					game.click(event.pos)
		
		display.fill(BACKGROUND_COLOR)
		game.draw(display)
		pygame.display.update()
		pygame.time.Clock().tick(FPS)

if __name__ == '__main__':
	main()
