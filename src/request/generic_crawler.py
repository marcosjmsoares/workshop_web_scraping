from datetime import datetime
import json
import time
import random

from bs4 import BeautifulSoup
import pandas as pd
import requests
from request.crawlers.default_crawler import AbstractCrawler


class GenericRequestCrawler(AbstractCrawler):
    def __init__(self, type):
        super().__init__()
        self.type = type

    def crawl(self, query):
        self.query = query
        self.configs = json.loads(self.get_steps(self.type))
        if self.configs is None:
            raise Exception("Crawler Não configurado!")
        self.get_data()
        self.extraction()
        self.transform_to_df_and_improve()
        self.save_data(self.df)

    def get_data(self):
        """Faz requisição com retry automático e respeito ao servidor"""
        url = f"{self.configs['link']['path']}{self.query.replace(' ', self.configs['link']['connector'])}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"📡 Requisição para: {url}")
                response = requests.get(url, headers=headers, timeout=15)

                if response.status_code == 503:
                    # Erro temporário - tenta novamente com delay maior
                    retry_count += 1
                    # Delay exponencial maior: 10, 20, 40 segundos
                    wait_time = 10 * (2 ** (retry_count - 1))
                    print(f"⏳ Status 503 (Serviço Indisponível)")
                    print(f"   Tentativa {retry_count}/{max_retries}. Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code == 429:
                    # Too Many Requests - aguarde mais tempo
                    retry_count += 1
                    wait_time = 15 * (2 ** (retry_count - 1))
                    print(f"⏳ Status 429 (Muitas Requisições - Rate Limit)")
                    print(f"   Tentativa {retry_count}/{max_retries}. Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code > 400:
                    raise Exception(f"Status Code {response.status_code} != 200")
                
                self.data = response.text
                print(f"✅ Requisição bem-sucedida (Status {response.status_code})")
                return
            
            except requests.exceptions.Timeout:
                retry_count += 1
                wait_time = 10 * (2 ** (retry_count - 1))
                print(f"⏳ Timeout na requisição. Tentativa {retry_count}/{max_retries}. Aguardando {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            except requests.exceptions.RequestException as e:
                retry_count += 1
                wait_time = 10 * (2 ** (retry_count - 1))
                print(f"⏳ Erro na requisição: {e}")
                print(f"   Tentativa {retry_count}/{max_retries}. Aguardando {wait_time}s...")
                time.sleep(wait_time)
                continue
        
        raise Exception(f"Falha após {max_retries} tentativas. Servidor pode estar bloqueando.")

    def extraction(self):
        """Extrai dados com delay entre processamentos"""
        soup = BeautifulSoup(self.data, "html.parser")
        
        # Buscar elementos raiz
        if self.configs["search"]["custom"]:
            results = soup.find_all(self.configs["search"]["tag"], self.configs["search"]["custom"])
        else:
            results = soup.find_all(self.configs["search"]["tag"], class_=self.configs["search"]["class"])

        print(f"📦 Encontrados {len(results)} produtos")
        
        data = []
        for idx, result in enumerate(results):
            product = {}
            for step in self.configs["product"]:
                config = self.configs["product"][step]
                try:
                    content = self._extract_value(result, config)
                    product[step] = content
                except Exception as e:
                    print(f"   ⚠️ Erro ao extrair {step}: {e}")
                    product[step] = config.get("default", "N/A")
            data.append(product)
            
            # Delay aleatório entre processamentos (simula comportamento humano)
            if idx < len(results) - 1:
                delay = random.uniform(0.5, 1.5)
                time.sleep(delay)
        
        self.df = data

    def _extract_value(self, element, config):
        """
        Extrai um valor de um elemento HTML baseado na configuração
        """
        try:
            tag = config.get("tag")
            css_class = config.get("class")
            attribute = config.get("attribute", "text")
            default = config.get("default", "N/A")

            # Buscar o elemento
            if css_class:
                found_element = element.find(tag, class_=css_class)
            else:
                found_element = element.find(tag)

            if found_element is None:
                return default

            # Extrair o valor
            if attribute == "text":
                value = found_element.get_text(strip=True)
            else:
                value = found_element.get(attribute)

            return value if value else default

        except Exception as e:
            return config.get("default", "N/A")

    def transform_to_df_and_improve(self):
        df = pd.DataFrame(self.df)
        df = df.assign(keyword=self.query)
        df = df.assign(ecommerce=self.type)
        df = df.assign(dateTimeReference=datetime.now().isoformat())
        df = df.assign(crawlerType="Request")
        self.df = df
