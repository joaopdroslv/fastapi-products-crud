from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app import exception_handlers, exceptions
from app.controllers import product_controller

app = FastAPI()

app.add_exception_handler(
    exceptions.NotFound, exception_handlers.not_found_exception_handler
)
app.add_exception_handler(
    RequestValidationError, exception_handlers.validation_exception_handler
)

app.include_router(product_controller.product_controller.router)
