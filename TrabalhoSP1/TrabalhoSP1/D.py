import time
import gc
import hashlib
import statistics
import math # Importado para o cálculo do Intervalo de Confiança 

def medir_sha256_hashlib(ficheiro, num_execucoes=10):
    tempos = []
    
    # 1. LER O FICHEIRO PARA A MEMÓRIA ANTES DO CRONÓMETRO! 
    with open(ficheiro, 'rb') as f:
        dados = f.read()

    # WARM-UP (Aquecimento do SHA-256)
    for _ in range(5):
        h_temp = hashlib.sha256()
        h_temp.update(dados)
        h_temp.digest()
    
    # DESATIVAR GC ANTES DO LOOP 
    gc.disable()
    
    for _ in range(num_execucoes):
        # Ligar o cronómetro
        inicio = time.perf_counter_ns()
        
        sha256 = hashlib.sha256()
        sha256.update(dados) # Fazer o hash dos dados que já estão na RAM 
        sha256.digest()      # Finalizar o hash 
        
        # Desligar o cronómetro
        fim = time.perf_counter_ns()
        
        tempos.append((fim - inicio) / 1000)  # converter para μs 
    
    # ATIVAR GC DEPOIS DO LOOP 
    gc.enable()
    
    media = statistics.mean(tempos) 
    desvio = statistics.stdev(tempos) if num_execucoes > 1 else 0 
    
    # Cálculo do Intervalo de Confiança (95%) [cite: 3, 11]
    erro = 1.96 * (desvio / math.sqrt(num_execucoes)) if num_execucoes > 1 else 0 
    ic = (media - erro, media + erro) 
    
    return media, desvio, ic


def executar_SHA(sizes):
    # Inicializar os arrays para guardar os resultados 
    sha_medias = []
    sha_desvios = []
    
    ficheiros = [f"random_file_{size}bytes.txt" for size in sizes] 
    # cabeçalho da tabela 
    print(f"{'Tamanho (bytes)':>15} {'Média (μs)':>15} {'Desvio (μs)':>15} {'IC 95% (μs)':>25}")

    for size, ficheiro in zip(sizes, ficheiros):
        # Ajustar número de execuções conforme o tamanho do ficheiro 
        if size <= 4096:
            n = 100
        elif size <= 32768:
            n = 50
        else:
            n = 20
    
        media, desvio, ic = medir_sha256_hashlib(ficheiro, n)
        
        # Guardar os resultados nas listas 
        sha_medias.append(media) 
        sha_desvios.append(desvio)
        
        ic_str = f"[{ic[0]:.2f}, {ic[1]:.2f}]" 
        print(f"{size:<20} {media:<14.2f} {desvio:<25.2f} {ic_str:<25}")
        
    # Retornar os arrays para o main.py 
    return sha_medias, sha_desvios

# Para correr o ficheiro isoladamente, descomentar:
"""
sizes_teste = [8, 64, 512, 4096, 32768, 262144, 2097152] 
medias, desvios = executar_SHA(sizes_teste)
"""