from events import *
from memeBingo.eventHandles import userUpdatedEventHandler

async def sendEvent(event: Event):
    # dispatch local
    # not good but fast
    print(event)
    if isinstance(event, UserUpdatedEvent):
        await userUpdatedEventHandler(event)
