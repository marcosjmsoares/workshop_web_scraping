import json
from redis_client import RedisClient


def populate_redis():
    """Popula o Redis com as configurações dos crawlers"""
    
    # Obter a instância singleton do Redis
    redis_client = RedisClient.get()
    
    # Testar conexão
    try:
        redis_client.ping()
        print("✓ Conectado ao Redis com sucesso!")
    except Exception as e:
        print(f"✗ Erro ao conectar ao Redis: {e}")
        print("Execute 'docker-compose up -d' primeiro.")
        return
    
    # Configuração completa para Mercado Livre (baseada no seu código funcional)
    ml_config = {
        "link": {
            "path": "https://lista.mercadolivre.com.br/",
            "connector": "-"
        },
        "script": {
            "before": [],
            "after": []
        },
        "search": {
            "custom": False,
            "tag": "li",
            "class": "ui-search-layout__item",
            "wait": {
                "class": "ui-search-layout__item",
                "timeout": 10
            }
        },
        "product": {
            "title": {
                "column": "Produto",
                "tag": "h2",
                "class": "poly-box poly-component__title",
                "attribute": "text",
                "default": "N/A"
            },
            "price": {
                "column": "Preço",
                "tag": "span",
                "class": "andes-money-amount__fraction",
                "attribute": "text",
                "default": "N/A"
            },
            "link": {
                "column": "URL",
                "tag": "a",
                "attribute": "href",
                "default": "N/A"
            }
        }
    }
    
    # Configuração completa para Amazon
    amazon_config = {
        "link": {
            "path": "https://www.amazon.com.br/s?k=",
            "connector": "+"
        },
        "script": {
            "before": [],
            "after": []
        },
        "search": {
            "custom": False,
            "tag": "div",
            "class": "s-result-item",
            "wait": {
                "class": "s-result-item",
                "timeout": 10
            }
        },
        "product": {
            "title": {
                "column": "Produto",
                "tag": "h2",
                "class": "a-text-normal",
                "attribute": "text",
                "default": "N/A"
            },
            "price": {
                "column": "Preço",
                "tag": "span",
                "class": "a-price-whole",
                "attribute": "text",
                "default": "N/A"
            },
            "link": {
                "column": "URL",
                "tag": "a",
                "class": "s-link-style",
                "attribute": "href",
                "default": "N/A"
            }
        }
    }
    
    # Salvar no Redis como JSON string
    redis_client.set('Ml', json.dumps(ml_config, ensure_ascii=False))
    redis_client.set('Amazon', json.dumps(amazon_config, ensure_ascii=False))
    
    print("\n✓ Redis populado com sucesso!")
    
    # Verificar chaves salvas
    keys = redis_client.keys('*')
    print(f"\nChaves disponíveis: {keys}")
    
    # Exibir configurações
    ml_data = redis_client.get('Ml')
    
    print(f"\nConfiguração 'Ml':")
    print(json.dumps(json.loads(ml_data), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    populate_redis()
