from abc import ABC
from .models import AuthModel, UserModel
import uuid
import time

class AbcUsersRepo(ABC):
    def get(self, id: str) -> UserModel:
        ...
    def create(self, name: str, isGuest = False) -> UserModel:
        ...

class MemoUsersRepo(AbcUsersRepo):
	
    users = {}

    def __init__(self) -> None:
        super().__init__()
        self.users['123'] = UserModel(
            id='123', name='mmm', isGuest=False, createdAt=0)

    def get(self, id) -> UserModel:
        return self.users.get(id, None)

    def create(self, name: str, isGuest = False) -> UserModel:
        id = str(uuid.uuid4())
        self.users[id] = UserModel(id=id, name=name, isGuest=isGuest, createdAt=time.time())
        return self.users[id]

class AbcAuthRepo(ABC):
    def checkPassword(self, email: str, password: str) -> bool:
        ...

    def getByEmail(self, email: str) -> AuthModel:
        ...

    def create(self, email: str, password: str, userId: str) -> AuthModel:
        ...

class MemoAuthRepo(AbcAuthRepo):

    auths = {}

    def __init__(self) -> None:
        super().__init__()
        self.auths['m@m.m'] = AuthModel(email='m@m.m',
                                        password='mmm', userId='123')

    def checkPassword(self, email: str, password: str) -> bool:
        auth = self.auths.get(email, None)
        if auth is None:
            return False

        return auth.email == email and auth.password == password

    def getByEmail(self, email: str) -> AuthModel:
        return self.auths.get(email, None)

    def create(self, email: str, password: str, userId: str) -> AuthModel:
        if email in self.auths:
            raise Exception('Email already exists')
        
        self.auths[email] = AuthModel(email=email, password=password, userId=userId)
        return self.auths[email]
