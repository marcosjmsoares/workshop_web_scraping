from tools.mongodb import MongoConnection
import pandas as pd


def visualize_collections():
    """Visualiza dados salvos no MongoDB"""
    mongo = MongoConnection()
    
    # Obter banco de dados (use _db que é o atributo privado)
    db = mongo._db
    
    # Listar collections
    collections = db.list_collection_names()
    print(f"\n📦 Collections no MongoDB: {collections}\n")
    
    if not collections:
        print("❌ Nenhuma collection encontrada!")
        return
    
    # Para cada collection, mostrar dados
    for collection_name in collections:
        collection = db[collection_name]
        count = collection.count_documents({})
        print(f"📊 Collection '{collection_name}' - {count} documentos")
        print("-" * 100)
        
        # Buscar primeiros 5 documentos
        docs = list(collection.find().limit(5))
        
        if docs:
            # Converter para DataFrame para visualizar melhor
            df = pd.DataFrame(docs)
            
            # Remover coluna _id para ficar mais limpo
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            print(df.to_string())
            print(f"\n✅ Total: {count} documentos\n")
        else:
            print("❌ Sem documentos\n")


if __name__ == "__main__":
    visualize_collections()
