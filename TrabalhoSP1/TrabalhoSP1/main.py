import os
import statistics
import matplotlib.pyplot as plt

# Importar as funções dos módulos = exercícios
from A import generate_random_text_file, gerar
from B import benchmark_aes_melhorado, comparar_variabilidade_todos_tamanhos, executar_benchmarks
from C import gerar_chave_rsa, medir_encriptacao, medir_desencriptacao, encriptar, desencriptar, executar_RSA
from D import medir_sha256_hashlib, executar_SHA
from Evaluation import imprimir_analise_avancada, gerar_grafico_comparativo, gerar_grafico_pequenos, gerar_grafico_throughput, gerar_grafico_rsa



def main():
    # DEfINIÇÕES:
    tamanhos = [8, 64, 512, 4096, 32768, 262144, 2097152]
    
    
    #GERAÇÃO DE FICHEIROS - EXERCÍCIO A
    print("=========== GERAR FICHEIROS - EXERCÍCIO A ==========")
    gerar(tamanhos)
    print() #Parágrafo


    #AES - EXERCÍCIO B
    print("=========== AES - EXERCÍCIO B ==========")
    chave_teste = os.urandom(32)
    m_enc_AES, d_enc_AES, m_dec_AES, d_dec_AES = executar_benchmarks(tamanhos, chave_teste)
    comparar_variabilidade_todos_tamanhos(tamanhos, chave_teste)
    print() #parágrafo


    #RSA - EXERCÍCIO C
    print("=========== RSA - EXERCÍCIO C ==========")
    m_enc_RSA, d_enc_RSA, m_dec_RSA, d_dec_RSA = executar_RSA(tamanhos)
    print()


    #SHA-256 - EXERCÍCIO D
    print("=========== SHA-256 - EXERCÍCIO A ==========")
    m_SHA, d_SHA = executar_SHA(tamanhos)
    print()

    # 5. ANÁLISE AVANÇADA (Evaluation)
    print("\n=========== FASE 5: ANÁLISE DE TAXA E CRESCIMENTO ==========")
    imprimir_analise_avancada("AES-256 Enc", tamanhos, m_enc_AES)
    imprimir_analise_avancada("RSA-2048 Enc", tamanhos, m_enc_RSA)
    imprimir_analise_avancada("SHA-256", tamanhos, m_SHA)

    # 6. GRÁFICOS (Organizamos os dados para a função do Evaluation)
    dados_grafico = {
        'AES Enc': {'medias': m_enc_AES, 'desvios': d_enc_AES, 'fmt': '-o'},
        'AES Dec': {'medias': m_dec_AES, 'desvios': d_dec_AES, 'fmt': '--o'},
        'RSA Enc': {'medias': m_enc_RSA, 'desvios': d_enc_RSA, 'fmt': '-s'},
        'RSA Dec': {'medias': m_dec_RSA, 'desvios': d_dec_RSA, 'fmt': '--s'},
        'SHA-256': {'medias': m_SHA,     'desvios': d_SHA,     'fmt': '-^'}
    }
    
    gerar_grafico_comparativo(tamanhos, dados_grafico)

    print("\n=========== A GERAR GRÁFICOS ADICIONAIS ==========")
    
    # Gráfico 2: AES vs SHA em ficheiros pequenos
    gerar_grafico_pequenos(tamanhos, m_enc_AES, m_SHA)
    
    # Gráfico 3: Throughput do último ficheiro (índice -1 corresponde aos 2 MB)
    gerar_grafico_throughput(m_enc_AES[-1], m_enc_RSA[-1], m_SHA[-1])
    
    # Gráfico 4: Discrepância do RSA
    gerar_grafico_rsa(tamanhos, m_enc_RSA, m_dec_RSA)

# CChamar a função main() no final do ficheiro
if __name__ == "__main__":
    main()