from src.exceptions import NotFound

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def not_found_exception_handler(request: Request, exception: NotFound):
    return JSONResponse(
        status_code=404,
        content={'message': f'{exception.name} not found.'}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extraindo as mensagens de erro de validação e simplificando-as
    error_details = []
    for err in exc.errors():
        field = err.get('loc')[-1]  # Localização do erro, onde o erro ocorreu
        msg = err.get('msg')  # Mensagem do erro
        error_details.append(f"Field '{str(field)}': {str(msg).lower()}")

    # Retornando uma resposta mais amigável
    return JSONResponse(
        status_code=422,
        content={
            'message': 'Validation error(s) occurred.',
            'details': error_details
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    # OBSERVAÇÃO: Neste ponto, é interessante criar um log para a exceção...
    # IMPORTANTE: Por questão de segurança, retornar mensagem genérica ao usuário.
    return JSONResponse(
        status_code=500,
        content={'message': 'Ops! Somethind went wrong, we fell sorry for this.'}
    )
