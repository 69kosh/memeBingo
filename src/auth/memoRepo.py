from .repo import *


class UsersRepo(AbcUsersRepo):
	
    users = {}

    def get(self, id) -> UserModel | None:
        return self.users.get(id, None)

    def create(self, name: str, isGuest = False) -> str:
        user = UserModel(name=name, isGuest=isGuest)
        self.users[user.id] = user
        return user.id

class AuthRepo(AbcAuthRepo):

    auths = {}

    def checkPassword(self, email: str, password: str) -> bool:
        auth = self.auths.get(email, None)
        if auth is None:
            return False

        return auth.email == email and auth.password == password

    def getByEmail(self, email: str) -> AuthModel:
        return self.auths.get(email, None)

    def create(self, email: str, password: str, userId: str) -> str:
        if email in self.auths:
            raise Exception('Email already exists')
        
        self.auths[email] = AuthModel(email=email, password=password, userId=userId)
        return email
