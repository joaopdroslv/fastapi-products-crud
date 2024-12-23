from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()

class ProductLogClient:
    def __init__(self):
        try:
            # Obtém a URL de conexão do MongoDB
            mongodb_url = os.getenv('MONGODB_URL')
            if not mongodb_url:
                raise ValueError("A variável de ambiente 'MONGODB_URL' não está definida.")

            # Tenta conectar ao MongoDB
            self.mongo_client = MongoClient(mongodb_url)
            self.db = self.mongo_client['product_logs']
            self.collection = self.db['product_views']

            print("Conexão com o MongoDB estabelecida com sucesso.")
        except ConnectionError as e:
            print(f"Erro de conexão com MongoDB: {e}")
        except ValueError as e:
            print(f"Erro na configuração da URL de conexão: {e}")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

    def log_product_view(self, product_id: int):
        self.collection.insert_one(
            {"product_id": product_id, "viewed_at": datetime.now()}
        )

    def get_product_view_logs(self, product_id: int):
            logs = self.collection.find({"product_id": product_id})
            return [{"viewed_at": log["viewed_at"]} for log in logs]
