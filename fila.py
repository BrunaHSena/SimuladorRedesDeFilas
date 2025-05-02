class Fila:
    def __init__(self, id, servidores, capacidade, atendimento_min, atendimento_max, roteamento):
        self.id = id
        self.servidores = servidores
        self.capacidade = capacidade
        self.atendimento_min = atendimento_min
        self.atendimento_max = atendimento_max
        self.roteamento = roteamento
        self.num_clientes = 0
        self.tempo_estado = {}
        self.perdas = 0
