from app.models import product_model
from app.schemas import product_schema
from app import exceptions

from sqlalchemy.orm import Session


def create_product(db: Session, product: product_schema.ProductCreate):
    db_product = product_model.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session):
    return db.query(product_model.Product).all()


def update_product(product_id: int, product: product_schema.ProductUpdate, db: Session):
    db_product = find_product_by_id(product_id, db)
    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(product_id: int, db: Session):
    db_product = find_product_by_id(product_id, db)
    db.delete(db_product)
    db.commit()
    return db_product


def find_product_by_id(product_id: int, db: Session):
    db_product = db.query(product_model.Product).filter(product_model.Product.id == product_id).first()
    if not db_product:
        raise exceptions.NotFound('Product')
    return db_product
