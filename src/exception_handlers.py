from src.exceptions import NotFound

from fastapi import Request
from fastapi.responses import JSONResponse


async def not_found_exception_handler(request: Request, exception: NotFound):
    return JSONResponse(
        status_code=404,
        content={'message': f'{exception.name} not found.'}
    )
