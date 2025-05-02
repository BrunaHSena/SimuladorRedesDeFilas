import heapq

class Escalonador:
    def __init__(self):
        self.eventos = []

    def adicionar_evento(self, evento):
        heapq.heappush(self.eventos, evento)

    def proximo_evento(self):
        return heapq.heappop(self.eventos) if self.eventos else None
