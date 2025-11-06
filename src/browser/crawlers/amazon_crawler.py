from .default_crawler import AbstractCrawler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time


class AmazonCrawler(AbstractCrawler):
    """Crawler específico para Amazon"""
    
    def crawl(self, query):
        """Método principal de scraping"""
        self.query = query
        self.execute_before()
        self.execute_main()
        self.extraction()
        self.transform_to_df_and_improve()
        self.save_data(self.df)
        return self.df

    def execute_before(self):
        """Preparação antes de scraping"""
        print(f"🔍 Preparando para buscar: {self.query}")

    def execute_main(self):
        """Executa a busca no Amazon"""
        url = f"https://www.amazon.com.br/s?k={self.query.replace(' ', '+')}"
        print(f"📡 Navegando para: {url}")
        self.browser.get(url)
        
        try:
            WebDriverWait(self.browser, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "s-result-item"))
            )
            print("✅ Elementos carregados")
        except Exception as e:
            print(f"⚠️ Erro ao aguardar elementos: {e}")
        
        time.sleep(2)

    def extraction(self):
        """Extrai dados do HTML"""
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        results = soup.find_all("div", class_="s-result-item")
        
        print(f"📦 Encontrados {len(results)} produtos")
        
        data = []
        for result in results:
            try:
                # Título
                title_tag = result.find("h2")
                title = title_tag.get_text(strip=True) if title_tag else "N/A"
                
                # Preço
                price_tag = result.find("span", class_="a-price-whole")
                price = price_tag.get_text(strip=True) if price_tag else "N/A"
                
                # Link
                link_tag = result.find("a", class_="s-link-style")
                link = link_tag.get("href") if link_tag else "N/A"
                
                if title and title != "N/A":
                    data.append({"Produto": title, "Preço": price, "URL": link})
            except Exception as e:
                print(f"   ⚠️ Erro ao processar resultado: {e}")
                continue
        
        self.df = data

    def transform_to_df_and_improve(self):
        """Transforma dados em DataFrame"""
        df = pd.DataFrame(self.df)
        df = df.assign(keyword=self.query)
        df = df.assign(ecommerce="Amazon")
        df = df.assign(dateTimeReference=datetime.now().isoformat())
        df = df.assign(crawlerType="Browser")
        self.df = df
