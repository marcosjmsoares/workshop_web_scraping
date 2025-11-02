from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd


class BrowserML:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-web-security")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--memory-pressure-off")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(options=self.chrome_options)

    def execute_command(self, query):
        url = f"https://lista.mercadolivre.com.br/{query.replace(' ', '-')}"
        self.driver.get(url)
        
        # Espera até que os itens da lista sejam carregados
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "ui-search-layout__item"))
            )
        except Exception as e:
            print(f"Erro ao carregar elementos: {e}")
        
        time.sleep(2)
        html = self.driver.page_source
        self.driver.quit()

        soup = BeautifulSoup(html, "html.parser")
        
        # Buscar todos os <li> com a classe ui-search-layout__item
        results = soup.find_all("li", class_="ui-search-layout__item")
        data = []

        print(f"Encontrados {len(results)} resultados")

        for result in results:
            try:
                # Título do produto - procura por várias possibilidades
                title = "N/A"
                
                # Tenta encontrar o título em diferentes estruturas
                title_tag = result.find("h2", class_="poly-box poly-component__title")
                if not title_tag:
                    title_tag = result.find("h2")
                if not title_tag:
                    title_tag = result.find("a", class_="poly-component__title")
                
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    title = title.lstrip()
                
                # Preço
                price_tag = result.find("span", class_="andes-money-amount__fraction")
                price = price_tag.text.strip() if price_tag else "N/A"
                
                # Link do produto
                link_tag = result.find("a", href=True)
                link = link_tag["href"] if link_tag else "N/A"
                
                data.append({"Produto": title, "Preço": price, "URL": link})
                
            except Exception as e:
                print(f"Erro ao processar um resultado: {e}")
                continue

        return data

    def transform_df(self, query):
        data = self.execute_command(query)
        df = pd.DataFrame(data)
        return df


crawler = BrowserML()
dataframe = crawler.transform_df("Playstation")
print(dataframe)
