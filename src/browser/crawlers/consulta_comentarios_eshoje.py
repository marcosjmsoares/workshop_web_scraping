from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd


class ComentarioESHoje:
    def __init__(self):
        # Configuração das opções do Chrome para rodar em modo headless (sem interface gráfica)
        self.chrome_options = Options()
        
        # Desabilita o modo sandbox (necessário em alguns ambientes)
        self.chrome_options.add_argument("--no-sandbox")
        
        # Executa o navegador sem interface gráfica
        self.chrome_options.add_argument("--headless")
        
        # Desabilita as políticas de segurança web
        self.chrome_options.add_argument("--disable-web-security")
        
        # Desabilita o uso de /dev/shm (útil em ambientes com pouca memória)
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Desativa a pressão de memória
        self.chrome_options.add_argument("--memory-pressure-off")
        
        # Ignora erros de certificado SSL
        self.chrome_options.add_argument("--ignore-certificate-errors")
        
        # Remove a flag de detecção de automação
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Define um user-agent real para evitar bloqueios
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    def execute_command(self, url):
        # Inicializa o driver do Chrome com as opções configuradas
        driver = webdriver.Chrome(options=self.chrome_options)
        
        # Acessa a URL fornecida
        driver.get(url)
        
        # Aguarda até que os comentários sejam carregados na página
        try:
            # Espera até 10 segundos pela presença de elementos com classe "comment"
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "comment"))
            )
        except Exception as e:
            # Captura e exibe erro caso os comentários não sejam carregados
            print(f"Erro ao carregar elementos: {e}")
        
        # Aguarda 2 segundos adicionais para garantir carregamento completo
        time.sleep(2)
        
        # Captura o código HTML completo da página
        html = driver.page_source
        
        # Fecha o navegador
        driver.quit()

        # Cria objeto BeautifulSoup para fazer parsing do HTML
        soup = BeautifulSoup(html, "html.parser")
        
        # Busca todos os elementos <li> que possuem a classe "comment"
        results = soup.find_all("li", class_="comment")
        
        # Lista para armazenar os dados extraídos
        data = []

        # Exibe quantos comentários foram encontrados
        print(f"Encontrados {len(results)} comentários")

        # Itera sobre cada comentário encontrado
        for result in results:
            try:
#---------------------------------------------------------------------------------------------------------------------------------------                
                # ===== EXTRAÇÃO DO NOME DO AUTOR =====
                author = "N/A"  # Valor padrão caso não encontre
                
                # Tenta encontrar o nome dentro da tag <cite>
                author_tag = result.find("cite")
                
                # Se encontrou a tag, extrai o texto
                if author_tag:
                    author = author_tag.get_text(strip=True)
 
#---------------------------------------------------------------------------------------------------------------------------------------
                # ===== EXTRAÇÃO DA DATA DO COMENTÁRIO =====
                date = "N/A"  # Valor padrão caso não encontre
                hora = "N/A"  # Valor padrão para hora

                # Tenta encontrar tag <time> com classe "comment-date"
                date_tag = result.find("time pubdate")
                                
                # Se não encontrou, tenta qualquer tag <time>
                if not date_tag:
                    date_tag = result.find("time")

                # Tenta <a> com classe "comment-date"
                if not date_tag:
                    date_tag = result.find("a", class_="comment-link")

                # Tenta <span> com classe "comment-date"
                if not date_tag:
                    date_tag = result.find("span", class_="comment-date")

                # Busca por classes que contenham "comment-meta" ou "comment-metadata"
                if not date_tag:
                    meta_tag = result.find(class_=lambda x: x and ("comment-meta" in x or "comment-metadata" in x))
                    if meta_tag:
                        date_tag = meta_tag.find("time") or meta_tag.find("a") or meta_tag

                # Se encontrou a tag, extrai a data
                if date_tag:
                    # Tenta pegar o atributo "datetime" primeiro (formato ISO)
                    date_full = date_tag.get("datetime")
                    
                    # Se não tiver atributo datetime, pega o texto da tag
                    if not date_full:
                        date_full = date_tag.get_text(strip=True)
                    
                    # Limpa a string removendo tabs, quebras de linha e espaços extras
                    if date_full:
                        # Remove \t (tabs), \n (quebras de linha) e \r (retorno de carro)
                        date_full = date_full.replace('\t', '').replace('\n', '').replace('\r', '')
                        # Remove espaços múltiplos e deixa apenas um espaço entre palavras
                        date_full = ' '.join(date_full.split())
                        
                        # Separa a data e hora usando "No" como divisor
                        if " No " in date_full:
                            # Divide a string em duas partes usando "No" como separador
                            partes = date_full.split(" No ")
                            # A primeira parte é a data
                            date = partes[0].strip()
                            # A segunda parte é a hora
                            hora = partes[1].strip() if len(partes) > 1 else "N/A"
                        else:
                            # Se não encontrar "No", mantém tudo como data
                            date = date_full
                            hora = "N/A"

#---------------------------------------------------------------------------------------------------------------------------------------
                # ===== EXTRAÇÃO DO TEXTO DO COMENTÁRIO =====
                text = "N/A"  # Valor padrão caso não encontre
                
                # Tenta encontrar <div> com classe "comment-content"
                text_tag = result.find("div", class_="comment-content")
                
                # Se não encontrou, tenta classe "comment-text"
                if not text_tag:
                    text_tag = result.find("div", class_="comment-text")
                
                # Tenta classe "comment-body"
                if not text_tag:
                    text_tag = result.find("div", class_="comment-body")
                
                # Busca por qualquer classe que contenha "comment" e "content" ou "text"
                if not text_tag:
                    text_tag = result.find("div", class_=lambda x: x and "comment" in x and ("content" in x or "text" in x or "body" in x))
                
                # Se ainda não encontrou, tenta pegar o primeiro <p> dentro do comentário
                if not text_tag:
                    text_tag = result.find("p")
                
                # Se encontrou a tag, extrai o texto
                if text_tag:
                    text = text_tag.get_text(strip=True)
                
                # Adiciona os dados extraídos à lista
                data.append({
                    "URL": url,
                    "Autor": author,
                    "Data": date,
                    "Hora": hora,
                    "Comentário": text
                })
                
            except Exception as e:
                # Captura erros ao processar um comentário específico e continua para o próximo
                print(f"Erro ao processar um comentário: {e}")
                continue

        # Retorna a lista com todos os dados coletados
        return data

    def transform_df(self, url):
        # Executa a coleta de dados
        data = self.execute_command(url)
        
        # Converte a lista de dicionários em um DataFrame do pandas
        df = pd.DataFrame(data)
        
        # Retorna o DataFrame
        return df


# ===== EXECUÇÃO DO CÓDIGO =====
# Instancia a classe ComentarioESHoje
crawler = ComentarioESHoje()

# Define a lista de URLs da notícia que contém os comentários
urls = [
    "https://eshoje.com.br/saude/2025/10/surto-misterioso-no-hospital-santa-rita-deixa-26-funcionarios-internados/",
    "https://eshoje.com.br/saude/2025/10/vigilancia-sanitaria-emite-alerta-estadual-para-conter-surto-no-hospital-santa-rita/", 
    "https://eshoje.com.br/saude/2025/10/agua-de-esgoto-invade-setores-do-hospital-santa-rita-apos-fortes-chuvas-na-grande-vitoria/",
    "https://eshoje.com.br/saude/2025/10/secretario-reforca-investigacao-no-hospital-santa-rita-e-garante-seguranca-apos-surto/",
    "https://eshoje.com.br/saude/2025/10/secretario-descarta-risco-a-populacao-em-surto-no-hospital-santa-rita/",
    "https://eshoje.com.br/saude/2025/10/o-que-se-sabe-ate-agora-sobre-o-surto-de-contaminacoes-no-hospital-santa-rita/",
    "https://eshoje.com.br/saude/2025/10/numero-de-trabalhadores-infectados-no-hospital-santa-rita-sobe-para-34/",
    "https://eshoje.com.br/saude/2025/10/especialistas-da-ufes-e-da-saude-publica-esclarecem-surto-de-infeccao-no-hospital-santa-rita/",
    "https://eshoje.com.br/saude/2025/10/legionelose-surto-no-hospital-santa-rita-liga-alerta-sobre-manutencao-de-ar-condicionado/",
    "https://eshoje.com.br/saude/2025/10/sobe-para-88-numero-de-casos-suspeitos-de-contaminacao-no-hospital-santa-rita/",
    "https://eshoje.com.br/saude/2025/10/analises-descartam-presenca-de-virus-em-surto-no-hospital-santa-rita-em-vitoria/",
    "https://eshoje.com.br/saude/2025/11/atualizacao-sobre-surto-no-santa-rita/"
]

# Lista para armazenar todos os DataFrames
all_dataframes = []

# Itera sobre cada URL
for idx, url in enumerate(urls, start=1):
    print(f"\n{'='*80}")
    print(f"[{idx}/{len(urls)}] Processando: {url}")
    print(f"{'='*80}")
    
    try:
        # Executa a coleta para essa URL
        df = crawler.transform_df(url)
        
        # Adiciona o DataFrame à lista
        all_dataframes.append(df)
        
        print(f"✓ Coletados {len(df)} comentários desta URL")
        
    except Exception as e:
        print(f"✗ Erro ao processar {url}: {e}")
        continue
    
    # Pausa de 2 segundos entre requisições para não sobrecarregar o servidor
    time.sleep(2)

# Combina todos os DataFrames em um único
dataframe_final = pd.concat(all_dataframes, ignore_index=True)

# Exibe o DataFrame final
print(f"\n{'='*80}")
print(f"RESULTADO FINAL")
print(f"{'='*80}")
print(dataframe_final)
print(f"\nTotal de comentários coletados: {len(dataframe_final)}")
print(f"Total de URLs processadas: {len(all_dataframes)}/{len(urls)}")

# Salva todos os comentários em um único arquivo CSV
dataframe_final.to_csv("comentarios_eshoje_completo.csv", index=False, encoding="utf-8-sig")
print("\n✓ Arquivo salvo: comentarios_eshoje_completo.csv")