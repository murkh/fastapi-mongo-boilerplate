from typing import Union
from http import HTTPStatus
from fastapi import HTTPException, status


class CustomException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Union[str, None] = None,
    ):
        if not detail:
            detail = HTTPStatus(status_code).description
        super().__init__(status_code=status_code, detail=detail)


class BadRequestException(CustomException):
    def __init__(self, detail: Union[str, None] = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NotFoundException(CustomException):
    def __init__(self, detail: Union[str, None] = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(CustomException):
    def __init__(self, detail: Union[str, None] = None):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InternalServerException(CustomException):
    def __init__(self, detail: Union[str | None] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )
