from src.controllers import product_controller

from fastapi import FastAPI


app = FastAPI()

app.include_router(product_controller.product_controller.router)
