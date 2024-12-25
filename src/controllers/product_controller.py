from src.schemas import product_schema
from src.crud import product_crud
from src.database import dependencies
from src.database import mongodb

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List


class ProductController:
    def __init__(self):
        self.router = APIRouter(prefix='/products')
        # MongoClient para gerar log de visualização
        self.product_log_client = mongodb.ProductLogClient()  

        self.router.add_api_route(
            '/', self.create_product, methods=['POST'], response_model=product_schema.Product, status_code=201
        )
        self.router.add_api_route('/', self.get_products, methods=['GET'], status_code=200)
        self.router.add_api_route(
            '/{product_id}', self.get_product, response_model=product_schema.Product, methods=['GET'], status_code=200
        )
        self.router.add_api_route(
            '/{product_id}', self.update_product, methods=['PUT'], response_model=product_schema.Product, status_code=200
        )
        self.router.add_api_route(
            '/{product_id}', self.delete_product, methods=['DELETE'], response_model=product_schema.Product, status_code=200
        )
        self.router.add_api_route(
            '/{product_id}/views', self.get_product_view_report, methods=['GET'], status_code=200
        )

    def create_product(
            self, product: product_schema.ProductCreate, db: Session = Depends(dependencies.get_db)) -> product_schema.Product:
        db_product = product_crud.create_product(db=db, product=product)
        return db_product

    def get_products(self, db:Session = Depends(dependencies.get_db)) -> List[product_schema.Product]:
        db_products = product_crud.get_products(db)
        for db_product in db_products:
            self.product_log_client.log_product_view(db_product.id)  # Log no MongoDB de cada visualização
        return db_products

    def get_product(
            self, product_id: int, db: Session = Depends(dependencies.get_db)) -> product_schema.Product:
        db_product = product_crud.find_product_by_id(product_id, db)
        self.product_log_client.log_product_view(product_id)  # Log no MongoDB de cada visualização
        return db_product

    def update_product(
            self, product_id: int, product: product_schema.ProductUpdate, db: Session = Depends(dependencies.get_db)) -> product_schema.Product:
        product_crud.find_product_by_id(product_id, db)  # Validar se o produto existe na database
        db_product = product_crud.update_product(db=db, product_id=product_id, product=product)
        return db_product

    def delete_product(
            self, product_id: int, db: Session = Depends(dependencies.get_db)) -> product_schema.Product:
        product_crud.find_product_by_id(product_id, db)  # Validar se o produto existe na database
        self.product_log_client.clear_product_logs(product_id)  # Limpa os logs do produto excluído
        db_product = product_crud.delete_product(db=db, product_id=product_id)
        return db_product

    def get_product_view_report(
            self, product_id: int, db: Session = Depends(dependencies.get_db)):
        db_product = product_crud.find_product_by_id(product_id, db)
        # Obtemos os logs de visualização do MongoDB
        product_views = self.product_log_client.get_product_view_logs(product_id)  
        # Retornamos o produto e os logs de visualização
        return {'product': db_product, 'number_of_views': len(product_views), 'views': product_views}


product_controller = ProductController()
