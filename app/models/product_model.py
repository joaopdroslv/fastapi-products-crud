from sqlalchemy import Column, Enum, Integer, Numeric, String

from app.database.sqlite import Base
from app.schemas import product_schema


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(Numeric, nullable=False)
    status = Column(Enum(product_schema.ProductStatus))
    stock_quantity = Column(Integer, nullable=False)
