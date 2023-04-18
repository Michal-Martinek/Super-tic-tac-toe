import threading
from queue import Queue, Empty
from typing import Union

from Super_tic_tac_toe import Board, SmallBoard

AI_TIMEOUT = 0.1

MINIMAX_DEPTH_LIMIT = 1
WIN_PROBABILITY_DEPTH_LIMIT = 2

# TODO caching?
def smallBoardWinProbability(board: SmallBoard, onTurn=2, smallProbs=None, depth=0) -> float: # 0 - lose, 1 - win, 0.5 - draw
	if depth >= WIN_PROBABILITY_DEPTH_LIMIT:
		return 0.5
	if board.done():
		return [.5, 0., 1.][board.won]
	prob, num = 0.0, 0
	for y, line in enumerate(board.board):
		for x, cell in enumerate(line):
			if cell == 0:
				p = smallBoardWinProbability(board.madeMove(x, y, onTurn), 3 - onTurn, smallProbs, depth + 1)
				prob += p * (1. if smallProbs is None else smallProbs[y][x])
				num += 1
	if num == 0: return 0.0 # TODO needed?
	return prob / num
def value(board: Board) -> float:
	smallProbs = [[smallBoardWinProbability(b) for b in line] for line in board.board]
	prob = smallBoardWinProbability(board.toSmallBoard(), smallProbs=smallProbs)
	if prob in [0., 1.]:
		return float('inf') * (2 * prob - 1.)
	return prob
def minimax(board: Board, onTurn=2, depth=0) -> Union[Board, tuple[int, int]]:
	if depth >= MINIMAX_DEPTH_LIMIT:
		return board
	possibleNext = [board.moveMade(pos, onTurn) for pos in board.opened]
	if not possibleNext or board.done: assert False
	# TODO sort by cost to optimize

	bests = [minimax(nex, 3 - onTurn, depth + 1) for nex in possibleNext]
	best = [min, max][onTurn - 1](bests, key=lambda b: value(b)) # lambda b: (value(a) < value(b)) ^ (2 - onTurn))
	return best if depth != 0 else list(board.opened)[bests.index(best)]

def threadLoop(queue: Queue, responseQueue: Queue[tuple[int, int]], endEvent: threading.Event):
	while not endEvent.is_set():
		try:
			board = queue.get(timeout=AI_TIMEOUT)
		except Empty:
			continue
		move = minimax(board)
		responseQueue.put(move)
