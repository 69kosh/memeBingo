from abc import ABC
from .models import CardModel, GameModel

class AbcCardsRepo(ABC):
    def get(self, id: str) -> CardModel:
        ...
    def create(self) -> CardModel:
        ...

class AbcGamesRepo(ABC):

    def get(self, id: str) -> GameModel:
        ...
    def create(self) -> GameModel:
        ...
        