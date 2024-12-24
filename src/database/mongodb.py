from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()

class ProductLogClient:  
    # Seria interessante separar as responsabilidades, uma class de config outra com os métodos de log
    def __init__(self, environment: str = None):
        try:
            if environment is None:
                mongodb_url = os.getenv('MONGODB_PRODUCTION_URL')
                mongodb_database_name = os.getenv('MONGODB_PRODUCTION_DATABASE_NAME')
            if environment == 'test':
                mongodb_url = os.getenv('MONGODB_TEST_URL')
                mongodb_database_name = os.getenv('MONGODB_TEST_DATABASE_NAME')

            if not mongodb_url:
                raise ValueError("A variável de ambiente 'MONGODB_URL' não está definida.")
            if not mongodb_database_name:
                raise ValueError("A variável de ambiente 'MONGODB_TEST_DATABASE_NAME' não está definida.")

            self.mongo_client = MongoClient(mongodb_url)
            self.db = self.mongo_client[mongodb_database_name]  # Cria a database
            self.collection = self.db['product_views']  # Cria a collection

        except ConnectionError as e:
            print(f'Erro de conexão com MongoDB.')
        except ValueError as e:
            print(f'Erro na configuração da URL de conexão.')
        except Exception as e:
            print(f'Ocorreu um erro inesperado.')

    def log_product_view(self, product_id: int):
        self.collection.insert_one({'product_id': product_id, 'viewed_at': datetime.now()})

    def get_product_view_logs(self, product_id: int):
        logs = self.collection.find({'product_id': product_id})
        return [{'viewed_at': log['viewed_at']} for log in logs]

    def clear_product_logs(self, product_id: int):
        self.collection.delete_many({'product_id': product_id})
