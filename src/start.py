from browser.generic_crawler import GenericBrowserCrawler
from browser.crawlers.amazon_crawler import AmazonCrawler
import time

print("🔍 Scrapeando Mercado Livre...")
ml = GenericBrowserCrawler("Ml").crawl('Nintendo Switch')
print("✅ Mercado Livre concluído!")

print("\n⏳ Aguardando 10 segundos...")
time.sleep(10)

print("🔍 Scrapeando Amazon...")
amazon = AmazonCrawler().crawl('Sega')
print("✅ Amazon concluído!")

print("\n✨ Scraping finalizado!")
