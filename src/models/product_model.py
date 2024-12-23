from src.database.sqlite import Base
from src.enums import product_enum

from sqlalchemy import Column, String, Numeric, Integer, Enum


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(Numeric, nullable=False)
    status = Column(Enum(product_enum.ProductStatus))
    stock_quantity = Column(Integer, nullable=False)
