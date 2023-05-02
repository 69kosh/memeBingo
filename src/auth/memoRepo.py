from .repo import *


class UsersRepo(AbcUsersRepo):
	
    users = {}

    def __init__(self) -> None:
        super().__init__()

    def get(self, id) -> UserModel:
        return self.users.get(id, None)

    def create(self, name: str, isGuest = False) -> UserModel:
        user = UserModel(name=name, isGuest=isGuest)
        self.users[user.id] = user
        return user.id

class AuthRepo(AbcAuthRepo):

    auths = {}

    def __init__(self) -> None:
        super().__init__()

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
