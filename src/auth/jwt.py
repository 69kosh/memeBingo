
import time
import jwt
from dotenv import load_dotenv
import os
from fastapi.security.http import *
from fastapi import Request, Response, Depends

load_dotenv()
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
JWT_MAXAGE = int(os.getenv('JWT_MAXAGE', 600))
JWT_REFRESH_MAXAGE = int(os.getenv('JWT_REFRESH_MAXAGE', 24*3600))
TOKEN_NAME = 'at'
REFRESH_TOKEN_NAME = 'rt'


def signToken(data: dict, expires: int = 600) -> str:
    payload = data.copy()
    iat = int(time.time())
    payload["iat"] = iat - 1
    payload["exp"] = iat + expires
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


def decodeToken(token: str) -> dict | None:
    try:
        decodedToken = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decodedToken if decodedToken["exp"] >= time.time() else None
    except Exception as e:
        return None


def setTokens(response: Response, payload: dict, refreshPayload: dict = None):
    refreshPayload = payload if refreshPayload is None else refreshPayload
    token = signToken(payload)
    refreshToken = signToken(refreshPayload, JWT_REFRESH_MAXAGE)
    response.set_cookie(key=TOKEN_NAME, value=token, max_age=JWT_MAXAGE,
                        httponly=True)#, samesite='none', secure=True)
    response.set_cookie(key=REFRESH_TOKEN_NAME, value=refreshToken,
                        max_age=JWT_REFRESH_MAXAGE, httponly=True)#, samesite='none', secure=True)


def cleanTokens(response: Response):
    response.delete_cookie(key=TOKEN_NAME, httponly=True,
                           samesite='none', secure=True)
    response.delete_cookie(key=REFRESH_TOKEN_NAME,
                           httponly=True, samesite='none', secure=True)


def checkRefreshToken(request: Request):
    refreshToken = request.cookies.get(REFRESH_TOKEN_NAME)
    payload = decodeToken(refreshToken)
    if payload is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Not authenticated"
        )
    return payload


def checkAccess(rulesChecker: callable):
    def inner(request: Request):

        token = request.cookies.get(TOKEN_NAME)
        payload = decodeToken(token)
        subject = {} if payload is None else payload
        access = rulesChecker(subject=subject, request=dict(request))

        if not access:
            if not (token and payload):
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Not authenticated"
                )
            else:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Not authorized"
                )

    return inner


def mustBeAuthorized(subject, request):
    return subject.get('userId', None) is not None


def mustBeNotAuthorized(subject, request):
    return subject.get('userId', None) is None


def getJWTPayload(request: Request) -> dict:
    token = request.cookies.get(TOKEN_NAME)
    payload = decodeToken(token)
    return {} if payload is None else payload
