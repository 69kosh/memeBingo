
from auth.mongoRepo import *

async def getUsersRepo():
	return AbcUsersRepo()

def getUserAttributes(userId) -> UserModel:
    return getUsersRepo().get(userId)
