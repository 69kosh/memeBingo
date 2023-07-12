from events import UserUpdatedEvent
from .connect import *

async def userUpdatedEventHandler(event: UserUpdatedEvent):
    # if isGuest was True, but now is False
	if not event.newModel.isGuest and event.oldModel.isGuest:
		cardsRepo = await getCardsRepo()
		# update all cards of author, set isGuest=False
		ids = cardsRepo.findByAuthor(authorId=event.newModel.id, limit = 100500, withHidden=True)
		for id in ids:
			res = cardsRepo.update(id, CardSetIsGuestModel(isGuest=False))
			print('%s - %s' % (id, res))

		gamesRepo = await getGamesRepo()
		ids = gamesRepo.findByOwner(ownerId=event.newModel.id, limit = 100500, withHidden=True)
		# update all games of owner, set idGuest=False
		for id in ids:
			res = gamesRepo.update(id, GameSetIsGuestModel(isGuest=False))
			print('%s - %s' % (id, res))

