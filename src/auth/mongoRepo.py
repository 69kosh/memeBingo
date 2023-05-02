from .repo import *

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.binary import UuidRepresentation
from dotenv import load_dotenv
import os
import binascii
import hashlib

load_dotenv()
PASSWORD_SALT = os.getenv('PASSWORD_SALT')
MONGODB_URL = os.getenv('MONGODB_URL')
mongoClient = MongoClient(MONGODB_URL, uuidRepresentation='standard')
mongoDb = mongoClient.get_database('meme')
usersCollection = mongoDb.get_collection('users')
authCollection = mongoDb.get_collection('auth')

class UsersRepo(AbcUsersRepo):

    def __init__(self) -> None:
        super().__init__()

    def get(self, id:str) -> UserModel:
        data = usersCollection.find_one({'_id':id})
        if data:
            return UserModel.parse_obj(data)

    def create(self, name: str, isGuest = False) -> UserModel:
        user = UserModel(name=name, isGuest=isGuest)
        usersCollection.insert_one(user.dict(by_alias=True))
        return user

class AuthRepo(AbcAuthRepo):

    def hashPassword(self, password: str, salt2: str, iters: int = 100000) -> str:
        dk = hashlib.pbkdf2_hmac(hash_name='sha256',
                        password=bytes(password, 'utf-8'),
                        salt=bytes(PASSWORD_SALT + salt2, 'utf-8'),
                        iterations=iters)
        return binascii.hexlify(dk).decode('utf-8')

    def __init__(self) -> None:
        super().__init__()

    def checkPassword(self, email: str, password: str) -> bool:
        auth = self.getByEmail(email=email)
        if auth:
            hash = self.hashPassword(password=password, salt2=auth.email)
            return hash == auth.password

        return False

    def getByEmail(self, email: str) -> AuthModel:
        data = authCollection.find_one({'_id':email})
        if data:
            return AuthModel.parse_obj(data)

    def create(self, email: str, password: str, userId: str) -> AuthModel:
        hash = self.hashPassword(password=password, salt2=email)
        auth = AuthModel(email=email, password=hash, userId=userId)
        authCollection.insert_one(auth.dict(by_alias=True))
        return auth
