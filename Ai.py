import time
import threading
from queue import Queue, Empty

AI_TIMEOUT = 0.1

def getAiMove(board):
	time.sleep(3)
	return board.opened.pop()

def threadLoop(queue: Queue, responseQueue: Queue, endEvent: threading.Event):
	while not endEvent.is_set():
		try:
			board = queue.get(timeout=AI_TIMEOUT)
		except Empty:
			continue
		move = getAiMove(board)
		responseQueue.put(move)


