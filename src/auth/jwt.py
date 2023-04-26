
import time
import jwt
from decouple import config
from typing import Optional
from fastapi.openapi.models import HTTPBase as HTTPBaseModel
from fastapi.security.http import *
from fastapi import Request, Response

JWT_SECRET = config('jwt_secret')
JWT_ALGORITHM = config('jwt_algorithm')


class JWTPayload(BaseModel):
    payload: dict


def signToken(data: dict, expires: int = 600) -> str:
    payload = data.copy()
    payload["expires"] = time.time() + expires
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


def decodeToken(token: str) -> dict | None:
    try:
        decodedToken = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decodedToken if decodedToken["expires"] >= time.time() else None
    except:
        return None

def setTokens(response: Response, payload: dict):
    refreshTokenMaxAge = 7*24*3600
    tokenMaxAge = 600
    token = signToken(payload)
    refreshToken = signToken(payload, 7*24*3600)
    response.set_cookie(key="token", value=token, max_age=tokenMaxAge, httponly=True)
    response.set_cookie(key="refreshToken", value=refreshToken, max_age=refreshTokenMaxAge, httponly=True)
    response.set_cookie(key="schema", value=JWTCookies.__schema_name__, max_age=refreshTokenMaxAge, httponly=True)


class JWTCookies(HTTPBase):
    __schema_name__ = "JWTCookies"

    def __init__(
            self,
            *,
            scheme_name: Optional[str] = None,
            description: Optional[str] = None,
            auto_error: bool = True,
    ):
        self.model = HTTPBaseModel(
            scheme=self.__schema_name__, description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(
            self, request: Request
    ) -> Optional[JWTPayload]:
        scheme = request.cookies.get('schema')
        if scheme.lower() != self.__schema_name__:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Invalid authentication credentials",
            )
        token = request.cookies.get('token')
        payload = decodeToken(token)
        if not (token and payload):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Not authenticated"
                )
            else:
                return None
        return JWTPayload(payload=payload)
