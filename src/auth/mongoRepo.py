from .repo import *
import binascii
import hashlib

class UsersRepo(AbcUsersRepo):

    def __init__(self, collection) -> None:
        super().__init__()
        self.collection = collection

    def get(self, id:str) -> UserModel | None:
        data = self.collection.find_one({'_id':id})
        if data:
            return UserModel.parse_obj(data)

    def create(self, name: str, isGuest = False) -> str:
        user = UserModel(name=name, isGuest=isGuest)
        self.collection.insert_one(user.dict(by_alias=True))
        return user.id
    
    def update(self, id:str, name: str, isGuest = False) -> str:
        res = self.collection.update_one(
                filter={'_id': id}, 
                update={'$set': {'name': name, 'isGuest': isGuest}}
            )

        return id if res.modified_count == 1 else None

class AuthRepo(AbcAuthRepo):

    def hashPassword(self, password: str, salt2: str, iters: int = 100000) -> str:
        dk = hashlib.pbkdf2_hmac(hash_name='sha256',
                        password=bytes(password, 'utf-8'),
                        salt=bytes(self.salt + salt2, 'utf-8'),
                        iterations=iters)
        return binascii.hexlify(dk).decode('utf-8')

    def __init__(self, collection, salt = 'salt') -> None:
        super().__init__()
        self.collection = collection
        self.salt = salt

    def checkPassword(self, email: str, password: str) -> bool:
        auth = self.getByEmail(email=email)
        if auth:
            hash = self.hashPassword(password=password, salt2=auth.email)
            return hash == auth.password

        return False

    def getByEmail(self, email: str) -> AuthModel:
        data = self.collection.find_one({'_id':email})
        if data:
            return AuthModel.parse_obj(data)

    def create(self, email: str, password: str, userId: str) -> str:
        hash = self.hashPassword(password=password, salt2=email)
        auth = AuthModel(email=email, password=hash, userId=userId)
        self.collection.insert_one(auth.dict(by_alias=True))
        return auth.email
