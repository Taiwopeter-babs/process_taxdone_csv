from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from pydantic import Json
from uuid import UUID


class UserType(TypedDict):
    """### Type for the user object"""

    firstName: str
    lastName: str
    accountType: Literal["admin", "user"]
    dob: str
    email: str
    phone: str
    filingId: Union[int, None]
    gender: Optional[str]


class SaveUserType(UserType):
    """### Type for the user to save object"""

    id: UUID
    clerkUserId: str
    firstName: str
    gender: str
    createdAt: datetime
    updatedAt: datetime
    dob: datetime


class SaveClerkUserType:
    """### Type for the clerk user to save object"""

    first_name: str
    last_name: str
    email: List[str]
    phone: List[str]


class ClerkUserType(TypedDict):
    """### Type for the clerk user"""

    id: str
    data: Json
    createdAt: datetime
    updatedAt: datetime


class FilingType(TypedDict):
    """### Type for the filing to save"""

    userId: str
    year: str
    status: str
    createdAt: datetime
    updatedAt: datetime


class FilingDataType(TypedDict):
    """### Type for the filing data to save"""

    userId: str
    filingId: int
    section: str
    data: Json | None
    createdAt: datetime
    updatedAt: datetime


class ExcelData(TypedDict):
    """### Type for the declaration sheet"""

    section: str
    status: str
    year: str
    data: Dict[str, Any]
