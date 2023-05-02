from abc import ABC
from .models import AuthModel, UserModel

class AbcUsersRepo(ABC):
    def get(self, id: str) -> UserModel:
        ...
    def create(self, name: str, isGuest = False) -> UserModel:
        ...

class AbcAuthRepo(ABC):
    def checkPassword(self, email: str, password: str) -> bool:
        ...

    def getByEmail(self, email: str) -> AuthModel:
        ...

    def create(self, email: str, password: str, userId: str) -> AuthModel:
        ...
        