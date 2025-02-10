from pydantic import BaseModel, Field, model_validator
from typing import Optional
from enum import Enum


class ProductStatus(Enum):
    in_stock = 'em_estoque'
    in_replacement = 'em_reposicao'
    out_of_stock = 'em_falta'


class ProductBase(BaseModel):
    name: str = Field(max_length=128)
    description: str = Field(max_length=255)
    price: float = Field(gt=0)
    status: ProductStatus
    stock_quantity: int

    @model_validator(mode='after')
    def validate_status(cls, product):
        """
        ProductsStatus rules:
            - out_of_stock: 'stock_quantity' should be == 0
            - in_stock: 'stock_quantity' should be > 0
            - in_replacement: 'stock_quantity' should be > 0
        """
        status = product.status
        stock_quantity = product.stock_quantity

        if status == ProductStatus.out_of_stock and stock_quantity > 0:
            raise ValueError('If its out of stock, stock quantity should be 0.')
        if (status in [ProductStatus.in_stock, ProductStatus.in_replacement]) and stock_quantity <= 0:
            raise ValueError('If the product is avaliable or in replacement, stock quantity should be greater than 0.')
        return product


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    """Not all fields are mandatory when updating"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    status: Optional[ProductStatus] = None
    stock_quantity: Optional[int] = None

    @model_validator(mode='after')
    def validate_price(cls, product):
        if product.price is not None and product.price <= 0.0:
            print('got here')
            raise ValueError('Price must be greater than 0.')
        return product


class Product(ProductBase):
    id: int

    class ConfigDict:
        from_attributes = True
