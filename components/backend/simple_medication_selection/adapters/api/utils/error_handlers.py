from typing import Any

from pydantic import ValidationError
from falcon import Request, Response
from falcon import status_codes

from simple_medication_selection.application.errors import (
    Error, ErrorsList
)


def validation_error(
    request: Request, response: Response,
    error: ValidationError, params: dict[str, Any],
):
    response.status = status_codes.HTTP_400
    response.media = error.errors()


def app_error(
    request: Request, response: Response,
    error: Error, params: dict[str, Any],
):
    response.status = status_codes.HTTP_400
    response.media = [{'type': error.code,
                       'msg': error.message,
                       'ctx': error.context}]


def app_errors_list(
    request: Request, response: Response,
    error: ErrorsList, params: dict[str, Any],
):
    response.status = status_codes.HTTP_400
    response.media = [
        {'type': e.code,
         'msg': e.message,
         'ctx': e.context}
        for e in error.errors
    ]
