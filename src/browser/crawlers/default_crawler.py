from abc import ABC, abstractmethod

from browser.provider.generic_b_crawler import GenericBrowserCrawler
from tools.redis_client import RedisClient
from tools.mongodb import MongoConnection


class AbstractCrawler(ABC):
    """Classe abstrata base para todos os crawlers"""
    
    def __init__(self):
        self.browser = GenericBrowserCrawler().get_browser()
        self.redis = RedisClient.get()
        self.mongo = MongoConnection()

    @abstractmethod
    def crawl(self, query):
        """Método principal de scraping"""
        pass
    
    @abstractmethod
    def execute_main(self):
        """Executa lógica principal"""
        pass
    
    @abstractmethod
    def execute_before(self):
        """Executa antes do scraping"""
        pass

    @abstractmethod
    def extraction(self):
        """Extrai dados da página"""
        pass

    def get_steps(self, site):
        """Obtém configuração do site do Redis"""
        return self.redis.get(site)
    
    def save_data(self, data):
        """Salva dados no MongoDB"""
        try:
            self.mongo.save_dataframe(data)
            print("✅ DataFrame salvo no MongoDB com sucesso.")
        except Exception as e:
            raise Exception(f"Não foi possível salvar os dados no Mongo: {e}")
