
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
    token = signToken(payload)
    refreshToken = signToken(payload, JWT_REFRESH_MAXAGE)
    response.set_cookie(key="token", value=token, max_age=JWT_MAXAGE, httponly=True)
    response.set_cookie(key="refreshToken", value=refreshToken, max_age=JWT_REFRESH_MAXAGE, httponly=True)

def cleanTokens(response: Response):
    response.delete_cookie(key="token", httponly=True)
    response.delete_cookie(key="refreshToken", httponly=True)

def accessControl(rulesChecker: callable):
    def inner(request: Request):
        
        token = request.cookies.get('token')
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

def isAuthorized(subject, request):
    return subject.get('userId', None) is not None

def isNotAuthorized(subject, request):
    return subject.get('userId', None) is None

def getJWTPayload(request: Request) -> dict:
    token = request.cookies.get('token')
    payload = decodeToken(token)
    return {} if payload is None else payload

