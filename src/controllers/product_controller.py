from src.schemas import product_schema
from src.crud import product_crud
from src.database import dependencies
from src.database import mongo_db

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session



class ProductController:
    def __init__(self):
        self.router = APIRouter(prefix='/products')
        self.product_log_client = mongo_db.ProductLogClient()  # MongoClient para gerar log de visualização

        self.router.add_api_route(
            '/', self.create_product, methods=['POST'], response_model=product_schema.ProductCreate, status_code=201
        )
        self.router.add_api_route(
            '/', self.get_products, methods=['GET'], status_code=200
        )
        self.router.add_api_route(
            '/{product_id}', self.get_product, methods=['GET'], status_code=200
        )
        self.router.add_api_route(
            '/{product_id}', self.update_product, methods=['PUT'], response_model=product_schema.ProductUpdate, status_code=200
        )
        self.router.add_api_route(
            '/{product_id}', self.delete_product, methods=['DELETE'], response_model=product_schema.ProductBase, status_code=200
        )
        self.router.add_api_route(
            '/{product_id}/views', self.get_product_view_report, methods=['GET'], status_code=200
        )

    def create_product(self, product: product_schema.ProductCreate, db: Session = Depends(dependencies.get_db)):
        db_product = product_crud.create_product(db=db, product=product)
        return db_product

    def get_products(self, db:Session = Depends(dependencies.get_db)):
        db_products = product_crud.get_products(db)
        return db_products

    def get_product(self, product_id: int, db: Session = Depends(dependencies.get_db)):
        db_product = product_crud.get_product(db, product_id)
        if db_product is None:
            raise HTTPException(status_code=404, detail='Product not found')

        # Log no MongoDB de cada visualização
        self.product_log_client.log_product_view(product_id)

        return db_product

    def update_product(self, product_id: int, product: product_schema.ProductUpdate, db: Session = Depends(dependencies.get_db)):
        db_product = product_crud.get_product(db, product_id)
        if db_product is None:
            raise HTTPException(status_code=404, detail='Product not found')

        updated_product = product_crud.update_product(db=db, product_id=product_id, product=product)
        return updated_product

    def delete_product(self, product_id: int, db: Session = Depends(dependencies.get_db)):
        db_product = product_crud.get_product(db, product_id)
        if db_product is None:
            raise HTTPException(status_code=404, detail='Product not found')

        deleted_product = product_crud.delete_product(db=db, product_id=product_id)
        return deleted_product

    def get_product_view_report(self, product_id: int, db: Session = Depends(dependencies.get_db)):
        db_product = product_crud.get_product(db, product_id)
        if db_product is None:
            raise HTTPException(status_code=404, detail='Product not found')

        # Obtemos os logs de visualização do MongoDB
        product_views = self.product_log_client.get_product_view_logs(product_id)

        # Retornamos o produto e os logs de visualização
        return {'product': db_product, 'number_of_views': len(product_views), 'views': product_views}


product_controller = ProductController()
