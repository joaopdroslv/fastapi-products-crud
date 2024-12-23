from src.enums import product_enum

from pydantic import BaseModel, Field, model_validator
from typing import Optional


class ProductBase(BaseModel):
    name: str = Field(max_length=128)
    description: Optional[str] = Field(max_length=255)
    price: float = Field(gt=0)
    status: product_enum.ProductStatus = Field(examples=list(product_enum.ProductStatus.__members__.keys()))
    stock_quantity: int = Field(gt=0)

    @model_validator(mode='before')
    def validate_status(cls, values):
        status_value = values.get('status')

        if status_value and status_value not in product_enum.ProductStatus.__members__:
            raise ValueError(
                f"Invalid status. Valid values are: {', '.join(product_enum.ProductStatus.__members__.keys())}"
            )
        return values


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    status: Optional[product_enum.ProductStatus] = None
    stock_quantity: Optional[int] = None


class Product(ProductBase):
    id: int

    class ConfigDict:
        from_attributes = True
