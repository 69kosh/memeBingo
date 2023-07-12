from pydantic import BaseModel
from auth.models import UserModel

class Event(BaseModel): ...

class UserUpdatedEvent(Event):
    id: str
    oldModel: UserModel
    newModel: UserModel

