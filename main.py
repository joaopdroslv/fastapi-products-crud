from src.controllers import product_controller

from fastapi import FastAPI
import uvicorn


app = FastAPI()

app.include_router(product_controller.product_controller.router)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
