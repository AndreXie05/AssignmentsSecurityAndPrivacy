# Benchmarking de Mecanismos Criptográficos

**AES-256 (CTR) · RSA-2048 Híbrido · SHA-256** 
*Análise de desempenho, throughput e variabilidade em ficheiros de 8 bytes a 2 MB.*

---

## Autores

André Chen Xie, Beatriz Morais Vieira, Manuel Henrique da Silva Mota 
*Inteligência Artificial e Ciências de Dados* 
**Data:** 30 de março de 2026

---

## Descrição do Projeto

Este projeto avalia o desempenho computacional de três mecanismos criptográficos:

- **AES-256** em modo CTR (cifra simétrica)
- **RSA-2048** num esquema híbrido (RSA(r) + máscara SHA-256)
- **SHA-256** (função hash)

Os testes foram executados sobre ficheiros de texto com tamanhos: 
`8, 64, 512, 4096, 32768, 262144, 2097152` bytes.

As métricas principais incluem tempo médio de execução (microssegundos), desvio padrão, intervalo de confiança (95%), throughput (MB/s) e análise de crescimento assintótico.

---

## Metodologia Experimental

- **Isolamento de I/O:** todos os ficheiros são carregados para a RAM antes da medição (`f.read()`)
- **Warm-up:** 5 execuções iniciais para estabilizar a cache do processador
- **Controlo do Garbage Collection:** `gc.disable()` durante os ciclos de medição; `gc.enable()` após
- **Precisão:** `time.perf_counter_ns()` + conversão para μs
- **Estatística:** média, desvio padrão, intervalo de confiança (95%, 1.96 × erro padrão)

---

## Estrutura do Código

| Ficheiro       | Função                                                                       |
|----------------|------------------------------------------------------------------------------|
| `A.py`         | Geração de ficheiros de texto aleatório (ASCII imprimível)                   |
| `B.py`         | Benchmarks AES (enc/dec), análise de variabilidade (mesmo vs dif. ficheiros) |
| `C.py`         | Implementação do RSA híbrido (RSA + SHA-256 mask) e respetivos testes        |
| `D.py`         | Medição do SHA-256 usando `hashlib`                                          |
| `Evaluation.py`| Cálculo de throughput, crescimento, geração de gráficos (matplotlib)         |
| `main.py`      | Geração de ficheiros → benchmarks → gráficos → relatório                     |

## Como executar

```bash
# 1. Instalar dependências
pip install cryptography matplotlib

Existem duas formas de executar o projeto, dependendo da necessidade:

---
### Opção 1: Executar tudo de uma vez 

Esta opção corre todos os exercícios (A, B, C, D e Evaluation) automaticamente, gerando ficheiros, benchmarks e gráficos.
Para executar o ficheiro colocar no terminal: python main.py

### Opção 2: Executar cada ficheiro individualmente

Esta opção corre cada ficheiro individualmente (A, B, C ou D)

Para isso, descomentar o blobo que está comentado no fim do ficheiro
Para executar o ficheiro colocar no terminal: python nome.py



