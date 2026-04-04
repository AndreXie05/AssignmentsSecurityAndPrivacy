import os
import time
import gc
import hashlib
import statistics
import math
from cryptography.hazmat.primitives.asymmetric import rsa

# Constante Global
BLOCK_SIZE = 32   # SHA-256 -> 32 bytes

def gerar_chave_rsa():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    numbers = private_key.private_numbers()
    n = numbers.public_numbers.n  # n = p*q
    e = numbers.public_numbers.e  # expoente público -> encriptar
    d = numbers.d                 # expoente privado -> desencriptar
    k = (n.bit_length() + 7) // 8 # tamanho do módulo em bytes (256 bytes)

    return n, e, d, k

# Função hash
def H(i, r):
    return hashlib.sha256(i.to_bytes(8, "big") + r).digest()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

# Enc(m;r) = RSA(r) || (H(0,r) xor m0) || ...
def encriptar(mensagem, n, e, k):
    r = os.urandom(BLOCK_SIZE)  # 32 bytes aleatórios

    # RSA(r)
    r_int = int.from_bytes(r, "big")
    rsa_r = pow(r_int, e, n).to_bytes(k, "big")

    # SHA-256 + XOR
    corpo = bytearray()
    indice = 0

    for i in range(0, len(mensagem), BLOCK_SIZE):
        bloco = mensagem[i:i + BLOCK_SIZE]
        mascara = H(indice, r)
        corpo.extend(xor_bytes(bloco, mascara[:len(bloco)]))
        indice += 1

    return rsa_r + bytes(corpo)

def desencriptar(cifra, n, d, k):
    rsa_r = cifra[:k]
    corpo = cifra[k:]

    # Recuperar r com RSA^-1
    rsa_r_int = int.from_bytes(rsa_r, "big")
    r_int = pow(rsa_r_int, d, n)
    r = r_int.to_bytes(BLOCK_SIZE, "big")

    mensagem = bytearray()
    indice = 0

    for i in range(0, len(corpo), BLOCK_SIZE):
        bloco = corpo[i:i + BLOCK_SIZE]
        mascara = H(indice, r)
        mensagem.extend(xor_bytes(bloco, mascara[:len(bloco)]))
        indice += 1

    return bytes(mensagem)

# Benchmark
def medir_encriptacao(mensagem, n, e, k, repeticoes):
    tempos = []
    cifras = []

    _ = encriptar(mensagem, n, e, k)  # warm-up

    gc.disable() 

    for _ in range(repeticoes):
        t0 = time.perf_counter_ns()
        cifra = encriptar(mensagem, n, e, k)
        t1 = time.perf_counter_ns()

        tempos.append((t1 - t0) / 1000)   
        cifras.append(cifra)
    
    gc.enable() 

    return tempos, cifras

def medir_desencriptacao(cifras, n, d, k):
    tempos = []

    _ = desencriptar(cifras[0], n, d, k)  # warm-up

    gc.disable() 

    for cifra in cifras:
        t0 = time.perf_counter_ns()
        _ = desencriptar(cifra, n, d, k)
        t1 = time.perf_counter_ns()

        tempos.append((t1 - t0) / 1000)   

    gc.enable() 

    return tempos


def executar_RSA(sizes):
    rsa_enc_medias = []
    rsa_enc_desvios = []
    rsa_dec_medias = []
    rsa_dec_desvios = []

    print("\n=== A Gerar Chaves RSA (2048 bits) ===")
    n_rsa, e_rsa, d_rsa, k_rsa = gerar_chave_rsa()

    for size in sizes:
        # METODOLOGIA HÍBRIDA PARA RSA
        if size <= 512:
            n = 50
        elif size <= 4096:
            n = 20
        else:
            n = 10

        nome_ficheiro = f"random_file_{size}bytes.txt"
        
        if not os.path.exists(nome_ficheiro):
            print(f"{size:<12} Ficheiro não encontrado, ignorando.")
            continue
            
        print(f"Ficheiro com {size} bytes (n={n})")

        with open(nome_ficheiro, "rb") as f:
            mensagem = f.read()

            cifra = encriptar(mensagem, n_rsa, e_rsa, k_rsa)
            recuperada = desencriptar(cifra, n_rsa, d_rsa, k_rsa)

            print("Mensagem original == recuperada?", mensagem == recuperada)

            # Passar o 'n' adaptado para as funções de medição
            tempos_enc, cifras = medir_encriptacao(mensagem, n_rsa, e_rsa, k_rsa, repeticoes=n)
            tempos_dec = medir_desencriptacao(cifras, n_rsa, d_rsa, k_rsa)

            m_enc = statistics.mean(tempos_enc)
            d_enc = statistics.stdev(tempos_enc) if len(tempos_enc) > 1 else 0
            m_dec = statistics.mean(tempos_dec)
            d_dec = statistics.stdev(tempos_dec) if len(tempos_dec) > 1 else 0

            # Intervalos de confiança a 95% (t-distribution, aproximação para n >= 10)
            t_critico = 2.262 if n <= 10 else (2.093 if n <= 20 else 2.009)

            ic_enc = t_critico * (d_enc / math.sqrt(n))
            ic_dec = t_critico * (d_dec / math.sqrt(n))

            ic_enc_lower = m_enc - ic_enc
            ic_enc_upper = m_enc + ic_enc
            ic_dec_lower = m_dec - ic_dec
            ic_dec_upper = m_dec + ic_dec

            rsa_enc_medias.append(m_enc)
            rsa_enc_desvios.append(d_enc)
            rsa_dec_medias.append(m_dec)
            rsa_dec_desvios.append(d_dec)

            print(f"Média encriptação (us): {m_enc:.2f}")
            print(f"Desvio padrão encriptação (us): {d_enc:.2f}")
            print(f"Média desencriptação (us): {m_dec:.2f}")
            print(f"Desvio padrão desencriptação (us): {d_dec:.2f}")
            print(f"IC 95% encriptação (us): [{ic_enc_lower:.2f}, {ic_enc_upper:.2f}]")
            print(f"IC 95% desencriptação (us): [{ic_dec_lower:.2f}, {ic_dec_upper:.2f}]")
            print("-" * 100, "\n")
    
    return rsa_enc_medias, rsa_enc_desvios, rsa_dec_medias, rsa_dec_desvios


#Para correr o ficheiro isoladamente, descomentar:
"""
tamanhos_teste = [8, 64, 512, 4096, 32768, 262144, 2097152]
m_enc, d_enc, m_dec, d_dec = executar_RSA(tamanhos_teste)
"""