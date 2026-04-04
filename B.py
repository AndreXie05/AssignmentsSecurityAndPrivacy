import os
import time
import gc
import math
import statistics
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def benchmark_aes_melhorado(nome_ficheiro, chave, n_iteracoes):
    
    with open(nome_ficheiro, 'rb') as f:
        dados = f.read()

    nonce = os.urandom(16)
    backend = default_backend()

    # --- ENCRIPTAÇÃO ---
    # Criamos o objeto fora para medir APENAS o processamento
    cifra_enc = Cipher(algorithms.AES(chave), modes.CTR(nonce), backend=backend)
    
    def tarefa_encriptar():
        encryptor = cifra_enc.encryptor()
        return encryptor.update(dados) + encryptor.finalize()

    # WARM-UP (Aquecimento da Encriptação)
    for _ in range(5):
        tarefa_encriptar()

    tempos_enc = []
    
    # DESATIVAR AQUI (antes de começar a medir)
    gc.disable() 
    
    for _ in range(n_iteracoes):
        t0 = time.perf_counter_ns()
        tarefa_encriptar()
        t1 = time.perf_counter_ns()
        tempos_enc.append((t1 - t0) / 1000) # Guardar em microsegundos
        
    # ATIVAR AQUI (mal termine a medição)
    gc.enable()

    # --- DECRIPTAÇÃO ---
    # Preparar o texto cifrado primeiro
    encryptor_prep = cifra_enc.encryptor()
    texto_cifrado = encryptor_prep.update(dados) + encryptor_prep.finalize()

    cifra_dec = Cipher(algorithms.AES(chave), modes.CTR(nonce), backend=backend)

    def tarefa_decriptar():
        decryptor = cifra_dec.decryptor()
        return decryptor.update(texto_cifrado) + decryptor.finalize()
    
    # WARM-UP (Aquecimento da Decriptação)
    for _ in range(5):
        tarefa_decriptar()

    tempos_dec = []
    
    # DESATIVAR AQUI
    gc.disable()
    
    for _ in range(n_iteracoes):
        t0 = time.perf_counter_ns()
        tarefa_decriptar()
        t1 = time.perf_counter_ns()
        tempos_dec.append((t1 - t0) / 1000)
        
    # ATIVAR AQUI
    gc.enable()

    # --- ESTATÍSTICA ---
    def calcular_stats(lista_tempos):
        # CORREÇÃO AQUI: Retirada a multiplicação por 1_000_000 pois já está em microsegundos
        media = statistics.mean(lista_tempos)
        desvio = statistics.stdev(lista_tempos) if len(lista_tempos) > 1 else 0
        erro = 1.96 * (desvio / math.sqrt(n_iteracoes)) if n_iteracoes > 0 else 0
        return {"media": media, "desvio": desvio, "ic": (media-erro, media+erro)}

    return calcular_stats(tempos_enc), calcular_stats(tempos_dec)


def executar_benchmarks(tamanhos, chave, ):
    # Inicializar os arrays para guardar os resultados
    medias_enc = []
    desvios_enc = []
    medias_dec = []
    desvios_dec = []

    print("\n" + "=" * 120)
    print(f"{'Tamanho (B)':<12} {'Enc Média (us)':<15} {'Enc Desv.Pad.':<15} {'Enc IC 95% (us)':<25} "
      f"{'Dec Média (us)':<15} {'Dec Desv.Pad.':<15} {'Dec IC 95% (us)':<25}")
    print("-" * 120)

    for tamanho in tamanhos:

        #numero de iteracoes:
        n_iteracoes = 100 if tamanho <= 4096 else 50 if tamanho <= 32768 else 20

        nome_ficheiro = f"random_file_{tamanho}bytes.txt"
        if os.path.exists(nome_ficheiro):
            stats_enc, stats_dec = benchmark_aes_melhorado(nome_ficheiro, chave, n_iteracoes)

            # Extrair os dados e guardar nos arrays correspondentes
            medias_enc.append(stats_enc['media'])
            desvios_enc.append(stats_enc['desvio'])
            medias_dec.append(stats_dec['media'])
            desvios_dec.append(stats_dec['desvio'])

            enc_ci_str = f"[{stats_enc['ic'][0]:.2f}, {stats_enc['ic'][1]:.2f}]"
            dec_ci_str = f"[{stats_dec['ic'][0]:.2f}, {stats_dec['ic'][1]:.2f}]"

            print(f"{tamanho:<12} "
                f"{stats_enc['media']:<15.2f} "
                f"{stats_enc['desvio']:<15.2f} "
                f"{enc_ci_str:<25} "
                f"{stats_dec['media']:<15.2f} "
                f"{stats_dec['desvio']:<15.2f} "
                f"{dec_ci_str:<25}")
        else:
            print(f"{tamanho:<12} Ficheiro não encontrado, ignorando.")
    
    # Retornar os arrays para poderem ser usados noutros ficheiros (ex: no main.py)
    return medias_enc, desvios_enc, medias_dec, desvios_dec


def comparar_variabilidade_todos_tamanhos(tamanhos, chave):
    """Compara variabilidade entre mesmo ficheiro e ficheiros diferentes para todos os tamanhos"""
    print("\n" + "="*75)
    print("ANÁLISE DE VARIABILIDADE PARA TODOS OS TAMANHOS")
    print("="*75)
    
    print(f"{'Tamanho (B)':<15} {'Mesmo Ficheiro':<35} {'Ficheiros Diferentes':<35}")
    print(f"{'':<15} {'Média (us)':<15} {'Desvio (us)':<15} {'Média (us)':<15} {'Desvio (us)':<15}")
    print("-" * 75)
    
    for tamanho in tamanhos:

        #numero de iterações:
        n_iteracoes = 100 if tamanho <= 4096 else 50 if tamanho <= 32768 else 20

        # 1. Mesmo ficheiro 
        mesmo_ficheiro_enc, _ = benchmark_aes_melhorado(f"random_file_{tamanho}bytes.txt", chave, n_iteracoes)
        
        # 2. Ficheiros diferentes
        tempos_enc_diff = []
        
        for i in range(n_iteracoes):
            nome_temp = f"temp_{i}_{tamanho}bytes.txt"
            
            with open(nome_temp, 'wb') as f:
                f.write(os.urandom(tamanho))
            
            stats_enc, _ = benchmark_aes_melhorado(nome_temp, chave, n_iteracoes)
            tempos_enc_diff.append(stats_enc['media'])
            os.remove(nome_temp)
        
        media_enc_diff = statistics.mean(tempos_enc_diff)
        desvio_enc_diff = statistics.stdev(tempos_enc_diff)
        
        # Apresentar resultados
        print(f"{tamanho:<15} "
              f"{mesmo_ficheiro_enc['media']:<15.2f} "
              f"{mesmo_ficheiro_enc['desvio']:<15.2f} "
              f"{media_enc_diff:<15.2f} "
              f"{desvio_enc_diff:<15.2f}")
    
    print("="*75)


#Para correr o ficheiro isoladamente, descomentar:
"""
tamanhos_teste = [8, 64, 512, 4096, 32768, 262144, 2097152] 
chave_teste = os.urandom(32)

m_enc, d_enc, m_dec, d_dec = executar_benchmarks(tamanhos_teste, chave_teste)
comparar_variabilidade_todos_tamanhos(tamanhos_teste, chave_teste)
"""