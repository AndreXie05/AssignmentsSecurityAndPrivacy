import matplotlib.pyplot as plt
import math

def imprimir_analise_avancada(nome_algoritmo, tamanhos_bytes, medias_us):
    """Calcula e imprime Throughput e Crescimento Assintótico"""
    print(f"\n=== Análise de Performance: {nome_algoritmo} ===")
    print(f"{'Tamanho (B)':<15} {'Tempo (us)':<15} {'Throughput (MB/s)':<20} {'Crescimento':<15}")
    print("-" * 75)
    
    tempo_anterior = None
    
    for i in range(len(tamanhos_bytes)):
        tamanho = tamanhos_bytes[i]
        tempo_us = medias_us[i]
        
        # Calcular Throughput: (Megabytes) / (Segundos)
        tamanho_mb = tamanho / (1024 * 1024)
        tempo_s = tempo_us / 1_000_000
        throughput = tamanho_mb / tempo_s if tempo_s > 0 else 0
        
        # Calcular Multiplicador de Crescimento
        if tempo_anterior is not None and tempo_anterior > 0:
            crescimento = tempo_us / tempo_anterior
            crescimento_str = f"{crescimento:.2f}x"
        else:
            crescimento_str = "-"
            
        print(f"{size_format(tamanho):<15} {tempo_us:<15.2f} {throughput:<20.2f} {crescimento_str:<15}")
        tempo_anterior = tempo_us

def size_format(b):
    """Auxiliar para formatar o tamanho"""
    return f"{b} B"

def gerar_grafico_comparativo(tamanhos, resultados):

    plt.figure(figsize=(12, 7))

    # Desenhar cada linha com os seus respetivos "garfos" 
    for label, dados in resultados.items():
        plt.errorbar(tamanhos, dados['medias'], yerr=dados['desvios'], 
                     fmt=dados['fmt'], capsize=5, label=label)

    plt.xscale('log', base=2)
    plt.yscale('log', base=10)
    plt.title('Comparação de Performance Criptográfica (Escala Logarítmica)')
    plt.xlabel('Tamanho do Ficheiro (Bytes)')
    plt.ylabel('Tempo de Execução (μs)')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig('analise_performance.png')
    print("\n[Gráfico guardado como 'analise_performance.png']")
    plt.show()

def gerar_grafico_pequenos(tamanhos, aes_enc, sha):
    """Gera o Gráfico 2: AES vs SHA (Eixo X Categórico para espaçamento igual)"""
    # Usar strings para o eixo X obriga o matplotlib a espaçar os pontos por igual
    tamanhos_str = [f"{t}B" for t in tamanhos[:4]] 
    aes_pequenos = aes_enc[:4]
    sha_pequenos = sha[:4]

    plt.figure(figsize=(10, 6))
    plt.plot(tamanhos_str, aes_pequenos, marker='o', color='#1f77b4', label='AES-256 Enc')
    plt.plot(tamanhos_str, sha_pequenos, marker='^', color='#9467bd', label='SHA-256')

    plt.title('Comparação Linear em Ficheiros Pequenos (8B a 4KB)')
    plt.xlabel('Tamanho do Ficheiro (Bytes)')
    plt.ylabel('Tempo de Execução (μs)')
    
    plt.grid(True, ls="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig('grafico2_pequenos.png')
    print("[Gráfico guardado como 'grafico2_pequenos.png']")
    plt.close()

def gerar_grafico_throughput(aes_tempo, rsa_tempo, sha_tempo):
    """Gera o Gráfico 3: Gráfico de barras com o Throughput (Eixo Y Logarítmico)"""
    tamanho_mb = 2097152 / (1024 * 1024)
    
    aes_tp = tamanho_mb / (aes_tempo / 1_000_000)
    rsa_tp = tamanho_mb / (rsa_tempo / 1_000_000)
    sha_tp = tamanho_mb / (sha_tempo / 1_000_000)

    labels = ['AES-256 Enc', 'SHA-256', 'RSA Híbrido Enc']
    valores = [aes_tp, sha_tp, rsa_tp]
    cores = ['#1f77b4', '#9467bd', '#2ca02c']

    plt.figure(figsize=(9, 6))
    bars = plt.bar(labels, valores, color=cores)
    
    # CORREÇÃO: Eixo Y em log base 10 para a barra do RSA não desaparecer
    plt.yscale('log', base=10)
    
    # Ajustar a posição do texto para a escala logarítmica (multiplicar em vez de somar)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval * 1.25, 
                 f'{yval:.2f} MB/s', ha='center', va='bottom', fontweight='bold')

    plt.title('Throughput para Ficheiros de 2 MB (Escala Logarítmica)')
    plt.ylabel('Velocidade (MB/s) - Escala Logarítmica')
    plt.grid(True, axis='y', which="both", ls="--", alpha=0.6)
    
    # Aumentar o limite superior do eixo Y para o texto não ser cortado
    plt.ylim(top=max(valores) * 4) 
    
    plt.tight_layout()
    plt.savefig('grafico3_throughput.png')
    print("[Gráfico guardado como 'grafico3_throughput.png']")
    plt.close()

def gerar_grafico_rsa(tamanhos, rsa_enc, rsa_dec):
    """Gera o Gráfico 4: Discrepância de Tempo Cifra vs Decifra do RSA (Ambos Eixos Log)"""
    plt.figure(figsize=(10, 6))
    
    plt.plot(tamanhos, rsa_enc, marker='s', color='#2ca02c', label='RSA Enc')
    plt.plot(tamanhos, rsa_dec, marker='s', color='#d62728', linestyle='--', label='RSA Dec')

    plt.xscale('log', base=2)
    # CORREÇÃO: Eixo Y em log base 10 para ver a separação inicial das linhas
    plt.yscale('log', base=10) 
    
    plt.title('Discrepância de Tempo no RSA (Cifra vs. Decifra)')
    plt.xlabel('Tamanho do Ficheiro (Bytes) - Escala Logarítmica')
    plt.ylabel('Tempo de Execução (μs) - Escala Logarítmica')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig('grafico4_rsa.png')
    print("[Gráfico guardado como 'grafico4_rsa.png']")
    plt.close()