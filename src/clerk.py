from typing import Union
from clerk_backend_api import Clerk, User
from dotenv import load_dotenv
from os import getenv
import asyncio

from all_types import SaveClerkUserType, UserType

load_dotenv()
user: UserType


async def save_user_to_clerk(user_to_save: SaveClerkUserType) -> Union[User, None]:
    r"""Save a user to clerk

    :param user: The user object must include the `firstName`, `lastName`, `phone`, and `email_address`
    """

    try:

        user = {
            "firstName": "Jeremy+test",
            "lastName": "Cohen",
            "phone": "+33766726663",
            "email": "jeremy+2638z4@taxdone.ch"
        }

        client = Clerk(bearer_auth=getenv("CLERK_SECRET_KEY", ""))

        clerk_user = await client.users.create_async(
            first_name=user["firstName"],
            last_name=user["lastName"],
            email_address=[user["email"]],
            phone_number=[user["phone"]],
        )

        return clerk_user

    except Exception as ex:
        raise

user_id: str


async def get_user_from_clerk() -> Union[User, None]:
    r"""gets a user from clerk

    :param user: The clerk user id
    """

    try:

        client = Clerk(bearer_auth=getenv("CLERK_SECRET_KEY", ""))

        user_ob = await client.users.get_async(
            user_id=getenv('TEST_ID', '')
        )

        print(user_ob)

    except Exception as ex:
        print(ex)
        print(type(ex))
        raise
        return None


# asyncio.run(save_user_to_clerk())
# asyncio.run(get_user_from_clerk())
