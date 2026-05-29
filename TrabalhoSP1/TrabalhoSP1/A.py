import os
import random

def generate_random_text_file(filename, size_bytes):
    
    #cria um string com todos os caracteres imprimíveis do cógigo ascii (do 32 ao 126)
    chars = ''.join(chr(i) for i in range(32, 127))

    
    # Gera conteúdo aleatório
    # Cada caractere ASCII é 1 byte, por isso size_bytes = número de caracteres
    content = ''.join(random.choice(chars) for _ in range(size_bytes)) #o random.choice escolhe 
    #um caracter pseudoaleatório da string chars
    
    # Escreve no ficheiro (w = write)
    with open(filename, 'w', encoding='utf-8') as f: #abre o ficheiro com o nome desejado
        f.write(content) #escreve no ficheiro
    
    # Verificar tamanho
    actual_size = os.path.getsize(filename) #sugestão do chat
    print(f"Ficheiro '{filename}' gerado: {actual_size} bytes )") 



def gerar(sizes):

    # Gerar um ficheiro para cada tamanho
    for size in sizes:
        filename = f"random_file_{size}bytes.txt"
        generate_random_text_file(filename, size)

#Para correr este ficheiro isoladamente, descomentar:
"""
tamanhos = [8, 64, 512, 4096, 32768, 262144, 2097152]
gerar(tamanhos)
"""



