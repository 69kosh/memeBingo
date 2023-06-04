from .repo import *


class UsersRepo(AbcUsersRepo):
	
    users:dict[str, UserModel] = {}

    def get(self, id) -> UserModel | None:
        return self.users.get(id, None)

    def create(self, name: str, isGuest = False) -> str:
        user = UserModel(name=name, isGuest=isGuest)
        self.users[user.id] = user
        return user.id
    
    def update(self, id:str, name: str, isGuest=False) -> str:
        user = self.users[id]
        user.name = name
        user.isGuest = isGuest
        self.users[id] = user
        return id
    
class AuthRepo(AbcAuthRepo):

    auths:dict[str, AuthModel] = {}

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
