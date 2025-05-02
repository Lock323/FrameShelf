from fastapi.exceptions import RequestValidationError

from fastapi import Request
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from exceptions import InvalidLoginTokenError, InvalidResetPWTokenError
from starlette.responses import RedirectResponse

async def valid_exc_handler(request: Request, exc: RequestValidationError):
    '''
    функция переписывает стандартную обработку ошибок валидаци fastapi
    '''
    for error in exc.errors():
        loc = error["loc"][1]
        if loc == 'password' or loc == 'new_password':
            message = error["msg"]
            message = message[13:]
            return PlainTextResponse(message, status_code=422)
        elif loc == 'email':
            message = error["msg"]
            message = message[13:]
            return PlainTextResponse(message, status_code=422)
        elif loc == 'username':
            message = error["msg"]
            message = message[13:]
            return PlainTextResponse(message, status_code=422)
        else:
            return JSONResponse(
                status_code=409,
                content=jsonable_encoder({"detail": exc.errors()}),
            )


async def login_token_exc_handler(request: Request, exc: InvalidLoginTokenError):
    if request.headers.get("HX-Request") == "true":
        response = PlainTextResponse(status_code=302)
        response.headers["HX-Redirect"] = "/log_in"
        return response
    else:
        response = RedirectResponse(url="/log_in", status_code=302)
        return response


async def reset_pw_token_exc_handler(request: Request, exc: InvalidResetPWTokenError):
    response = PlainTextResponse("Error: Link expired or already has been used", status_code=400)
    return response
