class Evento:
    def __init__(self, tempo, tipo, fila_origem, fila_destino=None):
        self.tempo = tempo
        self.tipo = tipo  # 'CHEGADA', 'SAIDA', 'PASSAGEM'
        self.fila_origem = fila_origem
        self.fila_destino = fila_destino

    def __lt__(self, other):
        return self.tempo < other.tempo
