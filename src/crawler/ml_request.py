import requests
from bs4 import BeautifulSoup
import pandas as pd


class RequestML:
    def execute_command(self, query):
        url = f"https://lista.mercadolivre.com.br/{query.replace(' ','-')}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            html = response.text
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

crawler = RequestML()
dataframe = crawler.transform_df("iphone 12")

print(dataframe)