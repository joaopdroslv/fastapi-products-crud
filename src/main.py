from src.controllers import product_controller
from src import exceptions
from src import exception_handlers


from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError


app = FastAPI()

app.add_exception_handler(
    exceptions.NotFound, exception_handlers.not_found_exception_handler
)
app.add_exception_handler(
    RequestValidationError, exception_handlers.validation_exception_handler
)
app.add_exception_handler(
    Exception, exception_handlers.generic_exception_handler
)

app.include_router(product_controller.product_controller.router)
