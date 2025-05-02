import yaml
import random
from fila import Fila
from evento import Evento
from escalonador import Escalonador

# Função para gerar próximo número aleatório (entre 0 e 1)
def next_random():
    global aleatorios_usados
    aleatorios_usados += 1
    return random.random()

# Função para sortear tempo de intervalo
def sortear_tempo(min_valor, max_valor):
    return min_valor + (max_valor - min_valor) * next_random()

# Função para carregar o arquivo YML
def carregar_modelo(arquivo):
    with open(arquivo, 'r') as f:
        dados = yaml.safe_load(f)
    return dados

# Função para inicializar as filas
def inicializar_filas(dados):
    filas = {}
    for f in dados['filas']:
        fila = Fila(f['id'], f['servidores'], f['capacidade'],
                    f['atendimento_min'], f['atendimento_max'], f['roteamento'])
        filas[f['id']] = fila
    return filas

# Função para imprimir o relatório final
def imprimir_resultados(filas, tempo_global):
    for id, fila in filas.items():
        print(f"\n--- Resultados da Fila {id} ---")
        total_tempo = sum(fila.tempo_estado.values())
        for estado, tempo in fila.tempo_estado.items():
            probabilidade = tempo / tempo_global if tempo_global > 0 else 0
            print(f"Estado {estado} cliente(s): Tempo acumulado = {tempo:.2f}, Probabilidade = {probabilidade:.5f}")
        print(f"Clientes perdidos: {fila.perdas}")
    print(f"\nTempo total de simulação: {tempo_global:.2f}")

# Acumula tempo de cada estado nas filas
def acumular_tempo(filas, tempo_passado):
    for fila in filas.values():
        estado = fila.num_clientes
        if estado not in fila.tempo_estado:
            fila.tempo_estado[estado] = 0
        fila.tempo_estado[estado] += tempo_passado

# Função principal
def main():
    global aleatorios_usados
    aleatorios_usados = 0

    # Carregar dados
    dados = carregar_modelo('simulador.yml')
    filas = inicializar_filas(dados)

    # Inicializar escalonador
    escalonador = Escalonador()

    # Agendar primeiro evento de chegada
    chegada_ext = dados['chegadas_externas'][0]
    intervalo = sortear_tempo(chegada_ext['intervalo_min'], chegada_ext['intervalo_max'])
    escalonador.adicionar_evento(Evento(2.0, 'CHEGADA', chegada_ext['fila']))

    tempo_atual = 2.0

    while aleatorios_usados < 100000:
        evento = escalonador.proximo_evento()
        if evento is None:
            break

        tempo_passado = evento.tempo - tempo_atual
        if tempo_passado < 0:
            tempo_passado = 0
        acumular_tempo(filas, tempo_passado)

        tempo_atual = evento.tempo

        if evento.tipo == 'CHEGADA':
            fila = filas[evento.fila_origem]
            if fila.servidores > 0:
                fila.servidores -= 1
                tempo_atendimento = sortear_tempo(fila.atendimento_min, fila.atendimento_max)
                escalonador.adicionar_evento(Evento(tempo_atual + tempo_atendimento, 'SAIDA', fila.id))
            else:
                if fila.capacidade == -1 or fila.num_clientes < fila.capacidade:
                    fila.num_clientes += 1
                else:
                    fila.perdas += 1

            # Agendar próxima chegada externa
            if evento.fila_origem == chegada_ext['fila']:
                intervalo = sortear_tempo(chegada_ext['intervalo_min'], chegada_ext['intervalo_max'])
                escalonador.adicionar_evento(Evento(tempo_atual + intervalo, 'CHEGADA', fila.id))

        elif evento.tipo == 'SAIDA':
            fila = filas[evento.fila_origem]
            if fila.num_clientes > 0:
                fila.num_clientes -= 1
                tempo_atendimento = sortear_tempo(fila.atendimento_min, fila.atendimento_max)
                escalonador.adicionar_evento(Evento(tempo_atual + tempo_atendimento, 'SAIDA', fila.id))
            else:
                fila.servidores += 1
                # Verifica roteamento
                r = next_random()
                acumulado = 0
                destino = None
                for rota in fila.roteamento:
                    acumulado += rota['probabilidade']
                    if r <= acumulado:
                        destino = rota['destino']
                        break
                if destino == "saida" or destino is None:
                    pass  # Cliente vai embora
                else:
                    destino_fila = filas[int(destino)]

                    if destino_fila.servidores > 0:
                        destino_fila.servidores -= 1
                        tempo_atendimento = sortear_tempo(destino_fila.atendimento_min, destino_fila.atendimento_max)
                        escalonador.adicionar_evento(Evento(tempo_atual + tempo_atendimento, 'SAIDA', destino_fila.id))
                    else:
                        if destino_fila.capacidade == -1 or destino_fila.num_clientes < destino_fila.capacidade:
                            destino_fila.num_clientes += 1
                        else:
                            destino_fila.perdas += 1

    imprimir_resultados(filas, tempo_atual)

if __name__ == '__main__':
    main()
