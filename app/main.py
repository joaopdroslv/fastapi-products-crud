from app.controllers import product_controller
from app import exception_handlers
from app import exceptions


from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError


app = FastAPI()

app.add_exception_handler(
    exceptions.NotFound, exception_handlers.not_found_exception_handler
)
app.add_exception_handler(
    RequestValidationError, exception_handlers.validation_exception_handler
)

app.include_router(product_controller.product_controller.router)
