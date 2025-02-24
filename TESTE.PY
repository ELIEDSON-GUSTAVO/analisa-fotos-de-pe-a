import cv2
import os
import time
import json
import hashlib
from PIL import ImageGrab
import pandas as pd

# Pasta onde os perfis de alumínio estão armazenados
pasta_perfis = r'P:\ENGENHARIA\PERFIS ALUMINIO'
# Pasta para salvar as imagens de referência associadas
pasta_imagens_referencias = r'IMAGENS_REFERENCIAS'
# Caminho para salvar as associações
arquivo_associacoes = "associacoes.json"
# Caminho do arquivo Excel com códigos de referência
arquivo_excel = r'XTLS.xlsx'

# Certificar-se de que a pasta de imagens de referências existe
if not os.path.exists(pasta_imagens_referencias):
    os.makedirs(pasta_imagens_referencias)

# Carregar as associações de perfil (nome do perfil com base na imagem de referência)
def carregar_associacoes():
    if os.path.exists(arquivo_associacoes):
        with open(arquivo_associacoes, 'r') as f:
            return json.load(f)
    return {}

# Salvar as associações
def salvar_associacoes(associacoes):
    with open(arquivo_associacoes, 'w') as f:
        json.dump(associacoes, f, indent=4)

def calcular_hash_imagem(imagem):
    """
    Calcula o hash de uma imagem para usar como identificador único.
    """
    hash_md5 = hashlib.md5()
    with open(imagem, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def comparar_imagens(img1, img2):
    """
    Compara duas imagens usando ORB e Lowe's Ratio Test.
    Retorna True se as imagens forem semelhantes.
    """
    orb = cv2.ORB_create(nfeatures=1000)
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        return False

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    matches = bf.knnMatch(des1, des2, k=2)

    # Aplica o Lowe's Ratio Test
    good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

    return len(good_matches) > 10  # Ajuste o número de correspondências mínimas

def encontrar_perfil(imagem_referencia, pasta_perfis, associacoes):
    """
    Encontra perfis de alumínio na pasta que correspondem à imagem de referência,
    considerando variações de tamanho, espessura e outras diferenças.
    """
    # Carrega a imagem de referência (print da área de transferência)
    img_ref = cv2.imread(imagem_referencia, cv2.IMREAD_GRAYSCALE)
    if img_ref is None:
        print("Erro: Não foi possível carregar a imagem de referência.")
        return []

    # Verifica se a imagem de referência já foi associada a algum perfil
    for ref, dados in associacoes.items():
        img_ref_salva = cv2.imread(dados["imagem_referencia"], cv2.IMREAD_GRAYSCALE)
        if img_ref_salva is None:
            continue

        if comparar_imagens(img_ref, img_ref_salva):
            print(f"Referência já aprendida. Usando o perfil: {dados['perfil']}")
            abrir_imagem(dados["imagem_referencia"])
            abrir_arquivo(dados["caminho_arquivo"])
            return [(dados["perfil"], 1.0, [])]

    # Se não encontrou uma correspondência salva, procura automaticamente
    orb = cv2.ORB_create(nfeatures=1000)
    kp_ref, des_ref = orb.detectAndCompute(img_ref, None)
    
    if des_ref is None:
        print("Erro: Não foram encontrados descritores na imagem de referência.")
        return []

    resultados = []

    for nome_arquivo in os.listdir(pasta_perfis):
        if nome_arquivo.lower().endswith(('.jpg', '.png')):
            caminho_arquivo = os.path.join(pasta_perfis, nome_arquivo)

            try:
                img_perfil = cv2.imread(caminho_arquivo, cv2.IMREAD_GRAYSCALE)
                
                if img_perfil is None:
                    print(f"Erro ao carregar a imagem {nome_arquivo}. Verifique o arquivo.")
                    continue

                kp_perfil, des_perfil = orb.detectAndCompute(img_perfil, None)

                if des_ref is not None and des_perfil is not None:
                    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
                    matches = bf.knnMatch(des_ref, des_perfil, k=2)

                    # Aplica o Lowe's Ratio Test
                    good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

                    if len(good_matches) > 10:  # Ajuste o número de correspondências mínimas
                        confianca = sum([match.distance for match in good_matches]) / len(good_matches)
                        resultados.append((nome_arquivo, confianca, good_matches))

            except Exception as e:
                print(f"Erro ao processar {nome_arquivo}: {e}")

    if not resultados:
        print("Nenhum perfil correspondente encontrado.")
        return []

    # Ordena pela confiança (menor valor de confiança é mais confiável)
    resultados.sort(key=lambda x: x[1])

    melhor_correspondencia = resultados[0]
    print(f"Melhor correspondência encontrada: {melhor_correspondencia[0]} com confiança {melhor_correspondencia[1]:.4f}")
    
    return resultados

def abrir_imagem(caminho_imagem):
    """Abre a imagem com o programa padrão do sistema"""
    if os.path.exists(caminho_imagem):
        try:
            os.startfile(caminho_imagem)  # No Windows
        except Exception as e:
            print(f"Erro ao abrir a imagem {caminho_imagem}: {e}")
    else:
        print(f"Erro: O arquivo {caminho_imagem} não foi encontrado.")

def abrir_arquivo(caminho_arquivo):
    """Abre o arquivo do perfil com o programa padrão do sistema"""
    if os.path.exists(caminho_arquivo):
        try:
            os.startfile(caminho_arquivo)  # No Windows
        except Exception as e:
            print(f"Erro ao abrir o arquivo {caminho_arquivo}: {e}")
    else:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")

def procurar_codigo_excel(nome_stl):
    """
    Pesquisa o código de referência no arquivo Excel com base no nome do STL.
    """
    try:
        df = pd.read_excel(arquivo_excel)
        # Filtra a linha onde a descrição contém o nome do STL
        filtro = df[df['Descrição'].str.contains(nome_stl, case=False, na=False)]
        
        if not filtro.empty:
            codigo_referencia = filtro.iloc[0]['Cód. Referência']
            print(f"Código encontrado: {codigo_referencia}")  # Aqui é onde o código é impresso no terminal
            return codigo_referencia
        else:
            print("Código não encontrado na descrição do Excel.")
            return None
    except Exception as e:
        print(f"Erro ao buscar no arquivo Excel: {e}")
        return None

def processar_print_area_transferencia():
    """Captura a imagem da área de transferência e salva como arquivo temporário"""
    print("Monitorando a área de transferência...")
    ultimo_print = None
    associacoes = carregar_associacoes()  # Carregar as associações salvas

    while True:
        try:
            imagem = ImageGrab.grabclipboard()
            if imagem is not None and imagem != ultimo_print:
                print("\nNovo print detectado.")
                ultimo_print = imagem

                caminho_print = "print_temp.png"
                imagem.save(caminho_print)
                print(f"Print salvo em: {caminho_print}")

                # Calcula o hash da imagem para usar como identificador único
                hash_imagem = calcular_hash_imagem(caminho_print)

                resultados = encontrar_perfil(caminho_print, pasta_perfis, associacoes)

                if resultados:
                    print("Perfis encontrados:")
                    for nome_arquivo, confianca, good_matches in resultados:
                        print(f"Arquivo: {nome_arquivo}, Confiança: {confianca:.4f}")
                        caminho_perfil = os.path.join(pasta_perfis, nome_arquivo)
                        abrir_imagem(caminho_perfil)
                        abrir_arquivo(caminho_perfil)  # Abre também o arquivo do perfil
                        
                        # Pesquisa o código no Excel
                        codigo = procurar_codigo_excel(nome_arquivo)
                        if codigo:
                            print(f"Código do perfil {nome_arquivo}: {codigo}")
                        break  # Abre apenas o melhor resultado
                else:
                    print("Nenhum perfil correspondente encontrado. Por favor, mostre a imagem correta.")
                    referencia = input("Digite o nome do perfil correto: ")

                    # Salva a imagem de referência associada ao nome do perfil
                    caminho_imagem_ref = os.path.join(pasta_imagens_referencias, f"{referencia}.png")
                    imagem.save(caminho_imagem_ref)

                    # Associa o nome do perfil ao caminho da imagem
                    caminho_arquivo_perfil = os.path.join(pasta_perfis, f"{referencia}.jpg")  # Pode ser outro formato
                    associacoes[hash_imagem] = {
                        "perfil": referencia,
                        "imagem_referencia": caminho_imagem_ref,
                        "caminho_arquivo": caminho_arquivo_perfil
                    }
                    salvar_associacoes(associacoes)
                    print(f"Referência associada ao perfil {referencia} e imagem salva.")

                os.remove(caminho_print)  # Remove a imagem temporária
                print("\nPronto para processar outro print...")

        except Exception as e:
            print(f"Erro ao processar a área de transferência: {e}")

        time.sleep(0.5)  # Reduz a latência

# Executa o monitoramento
if __name__ == "__main__":
    if not os.path.exists(pasta_perfis):
        print(f"Erro: A pasta {pasta_perfis} não foi encontrada.")
    else:
        processar_print_area_transferencia()
