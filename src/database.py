from typing import Any, List, Union
import psycopg
from psycopg import AsyncCursor, sql
from psycopg.types.json import Json
from os import getenv
from dotenv import load_dotenv
import asyncio
from datetime import datetime
import uuid

from all_types import ClerkUserType, FilingDataType, FilingType, SaveUserType
from constants import DATETIME_FORMAT

load_dotenv()


def get_connection_string():
    keys_list = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"]

    conn_dict = {key: getenv(key, None) for key in keys_list}

    if not all(conn_dict.values()):
        raise ValueError(
            "Database connection key cannot be none. check your env values"
        )

    conn_string = "dbname={} user={} password={} port={} host={}".format(
        conn_dict.get("DB_NAME"),
        conn_dict.get("DB_USER"),
        conn_dict.get("DB_PASSWORD"),
        conn_dict.get("DB_PORT"),
        conn_dict.get("DB_HOST"),
    )

    return conn_string


users_list: List[SaveUserType]
filings_list: List[FilingType]
filings_data_list: List[FilingDataType]


async def seed_users():
    """Seed the user data into the database"""

    conn_string = get_connection_string()

    async with await psycopg.AsyncConnection.connect(conn_string) as conn:

        async with conn.cursor() as cur:

            """Columns to insert"""
            user_columns = [
                "id",
                "email",
                "clerkUserId",
                "firstName",
                "lastName",
                "gender",
                "dob",
                "accountType",
                "createdAt",
                "updatedAt",
            ]

            returning_columns = ["id", "firstName",
                                 "lastName", "createdAt", "active"]

            """Queries composition"""
            insert_user_query = compose_insertion_query(
                user_columns, "Users", returning_columns)

            list_u: List[SaveUserType] = [
                {
                    "id": uuid.uuid4(),
                    "accountType": "user",
                    "dob": "1989-10-14T00:00:00",
                    "firstName": "adrien",
                    "lastName": "el karoui",
                    "filingId": 8,
                    "phone": "763618354",
                    "email": "aElkarouiwegscheider@gmail.com",
                    "clerkUserId": "dre774dk",
                    "gender": "Male",
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now(),
                },
            ]

            params_list = [
                [
                    user["id"],
                    user["email"],
                    user["clerkUserId"],
                    user["firstName"],
                    user["lastName"],
                    user["gender"],
                    # This won't be necessary as the dob already comes in datetime
                    datetime.strptime(user["dob"], DATETIME_FORMAT),
                    user["accountType"],
                    user["createdAt"],
                    user["updatedAt"],
                ]
                for user in list_u
            ]

            saved_users = await asyncio.gather(
                *[
                    cur.execute(insert_user_query, tuple(user_params))
                    for user_params in params_list
                ]
            )

            # a list of tuple which contains the id of the record
            inserted_users = [await result.fetchone() for result in saved_users]

            # extract the id from the tuple
            return [record[0] for user in inserted_users if user is not None for record in user]


async def seed_clerk_user(cursor: AsyncCursor):
    """Seed the clerk user data into the database"""

    clerk_user_columns = ["id", "data", "createdAt", "updatedAt"]

    list_u: List[ClerkUserType] = [
        {
            "id": "user_jrhkjkjdkfk58954",
            "data": Json({"user_id": "user_jrhkjkjdkfk58954"}),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
        },
    ]

    params_list = [
        [
            user["id"],
            user["data"],
            user["createdAt"],
            user["updatedAt"],
        ]
        for user in list_u
    ]

    """Queries composition"""

    insert_clerk_user_query = compose_insertion_query(
        clerk_user_columns, "ClerkUser", ["id"])

    await asyncio.gather(
        *[
            cursor.execute(insert_clerk_user_query, tuple(user_params))
            for user_params in params_list
        ]
    )


async def seed_filing(cursor: AsyncCursor):
    """Seed the filing into the database"""

    # Columns to insert
    filing_columns = [
        "userId",
        "year",
        "status",
        "createdAt",
        "updatedAt"
    ]

    list_u: List[FilingType] = [
        {
            "userId": "user_jrhkjkjdkfk58954",
            "year": "2024",
            "status": "opened",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
        },
    ]

    params_list = [
        [
            user["userId"],
            user["year"],
            user["status"],
            user["createdAt"],
            user["updatedAt"],
        ]
        for user in list_u
    ]

    # Queries composition
    insert_filing_query = compose_insertion_query(
        filing_columns, "Filing", ["id"])

    saved_filing = await asyncio.gather(
        *[
            cursor.execute(insert_filing_query, tuple(filing_params))
            for filing_params in params_list
        ]
    )

    print(saved_filing)


async def seed_filing_data(cursor: AsyncCursor):
    """Seed the filing data into the database"""

    # Columns to insert
    filing_data_columns = [
        "userId",
        "filingId",
        "section",
        "data",
        "createdAt",
        "updatedAt"
    ]

    list_u: List[FilingDataType] = [
        {
            "userId": "user_jrhkjkjdkfk58954",
            "filingId": 8,
            "section": "2024",
            "data": Json({}),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
        },
    ]

    params_list = [
        [
            filing_data["userId"],
            filing_data['filingId'],
            filing_data["section"],
            filing_data["data"],
            filing_data["createdAt"],
            filing_data["updatedAt"],
        ]
        for filing_data in list_u
    ]

    # Queries composition
    insert_filing_data_query = compose_insertion_query(
        filing_data_columns, "FilingData", ["id"])

    saved_filing_data = await asyncio.gather(
        *[
            cursor.execute(insert_filing_data_query, tuple(filing_params))
            for filing_params in params_list
        ]
    )

    print(saved_filing_data)


def compose_insertion_query(columns: List[str], table_name: str, returning_columns: List[str]):
    r"""Compose the query for insertion

    :param columns: A list of strings that contains the names of columns to be inserted
    :param table_name: The name of the database table.
    :param returning_columns: The list of columns to return
    """
    insertion_query = sql.SQL(
        "INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING ({returning_columns})"
    ).format(
        fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
        values=sql.SQL(", ").join(sql.Placeholder() * len(columns)),
        table=sql.Identifier(table_name),
        returning_columns=sql.SQL(", ").join(
            map(sql.Identifier, returning_columns))
    )

    return insertion_query


async def get_results():

    users_ids = await seed_users()

    print(users_ids)

asyncio.run(get_results())
