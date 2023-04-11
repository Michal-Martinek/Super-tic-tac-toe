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

class SmallBoard:
	def __init__(self, row=0, col=0):
		self.board: list[list[int]] = [[0] * 3 for i in range(3)] # 0 - unplayed, 1 - first, 2 - second
		self.row = row
		self.col = col

	@ staticmethod
	def _drawFirst(display, pos): # cross
		points = [(pos[0] + Xoff, pos[1] + Yoff) for Yoff in (CELL_SIZE - CELL_INNER_SIZE, CELL_INNER_SIZE) for Xoff in (CELL_SIZE - CELL_INNER_SIZE, CELL_INNER_SIZE)]
		pygame.draw.line(display, (255, 0, 0), points[0], points[-1], MARK_THICKNESS)
		pygame.draw.line(display, (255, 0, 0), points[1], points[2], MARK_THICKNESS)
	@ staticmethod
	def _drawSecond(display, pos): # circle
		pos = pos[0] + CELL_SIZE // 2, pos[1] + CELL_SIZE // 2
		pygame.draw.circle(display, (0, 0, 255), pos, CELL_INNER_SIZE // 2, MARK_THICKNESS)

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
		pos = self.col * CELL_SIZE * 3, self.row * CELL_SIZE * 3 + BOARD_Y
		for y, cells in enumerate(self.board):
			for x, cell in enumerate(cells):
				cellPos = pos[0] + x * CELL_SIZE, pos[1] + y * CELL_SIZE
				if cell == 1:
					self._drawFirst(display, cellPos)
				elif cell == 2:
					self._drawSecond(display, cellPos)

class Board:
	def __init__(self):
		self.board: list[list[SmallBoard]] = [[SmallBoard(row, col) for col in range(3)] for row in range(3)]
	def play(self, topX, topY, innerX, innerY, move):
		self.board[topY][topX].board[innerY][innerX] = move
	def draw(self, display):
		for line in self.board:
			for board in line:
				board.draw(display)

class Game:
	def __init__(self):
		self.board = Board()
		self.playerOnTurn: int = 1 # 1, 2

	def click(self, pos) -> bool:
		if pos[1] < BOARD_Y: return False
		cellPos = pos[0] // CELL_SIZE, (pos[1] - BOARD_Y) // CELL_SIZE
		self.board.play(cellPos[0] // 3, cellPos[1] // 3, cellPos[0] % 3, cellPos[1] % 3, self.playerOnTurn)
		self.advancePlayer()
		return True
	def advancePlayer(self):
		self.playerOnTurn = 3 - self.playerOnTurn
	def draw(self, display):
		self.board.draw(display)

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