import itertools
from typing import Any, Dict, List
from datetime import date, datetime
import json
import asyncio
from multiprocessing import Pool, TimeoutError

from constants import *
from helpers import *
from all_types import ClerkUserType, ExcelData, FilingDataType, \
    FilingType, SaveClerkUserType, SaveUserType, UserType

from clerk import save_user_to_clerk

from util import construct_user_to_save, extract_sheet, \
    extract_user, get_workbook_and_sheet_names


def parse_user_sheet():
    """
    This function parses the user details sheet in the excel file.
    """

    workbook, user_sheet_name, *_ = get_workbook_and_sheet_names(
        USERS_SHEET_NAME, DECLARATIONS_SHEET_NAME
    )

    ALL_USERS: List[UserType] = []

    user_sheet = workbook[user_sheet_name]

    data_keys = list(USER_COLUMNS.keys())
    column_keys, *users_data = user_sheet.values  # type: ignore

    for data in users_data:

        current_user: UserType = {}  # type: ignore

        for col_key, col_val in zip(column_keys, data):

            if col_key in data_keys:
                current_user[USER_COLUMNS.get(col_key)] = process_col_value(  # type: ignore
                    col_key, col_val
                )

        # exclude data without an email address
        if current_user.get("email") is None:
            continue

        ALL_USERS.append(current_user)

    with open("users_data.json", "w+", encoding="utf-8") as filing_data_file:
        json.dump(ALL_USERS, filing_data_file)

    print('PARSING ALMOST FINISHED. Users data saved to users_data.json')

    return ALL_USERS


def parse_declaration_sheet():
    r"""
    This function parses the declaration sheet in the excel file.

    :returns: A list of dictionary objects representing the rows in the file of sheet names parsed with
    their values as the unique ids in a string or a list of string and a year property in each list item
    Example:
    ```json
    [
        {
            "Securities": [
                "1600676584609x857879840086294500",
                "1600676641050x503212502662250500",
            ],
            // rest of the properties
            "year": "2019"
        },
        // Anotther dictionary object
    ]
    ```
    """

    workbook, _, declaration_sheet_name, _ = get_workbook_and_sheet_names(
        USERS_SHEET_NAME, DECLARATIONS_SHEET_NAME
    )

    # all_declarations: Dict[str, str] = {}
    all_declarations: List[Dict[str, Any]] = []

    declaration_sheet = workbook[declaration_sheet_name]

    column_keys, *declaration_data = declaration_sheet.values  # type: ignore

    sheet_names_for_mapping = DECLARATION_MAPPER.keys()

    for data in declaration_data:

        current_declare_data = {}

        """col_key's are sheet references for other sheets in Declaration sheet
        The col_val's are `unique id` values in a string or a comma separated string
        of unique ids.
        """
        for col_key, col_val in zip(column_keys, data):

            str_key = str(col_key)
            str_val = str(col_val)

            if col_key in sheet_names_for_mapping:

                mapped_sheet_name = DECLARATION_MAPPER.get(str_key)

                str_val_format = []

                if ',' in str_val:
                    str_val_format = [val.strip()
                                      for val in str_val.split(',')
                                      ]

                    current_declare_data[mapped_sheet_name] = str_val_format

                else:
                    current_declare_data[mapped_sheet_name] = str_val

            if str(col_key) == 'year':
                current_declare_data[str_key] = str_val

        all_declarations.append(current_declare_data)

    with open("declarations.json", "w+", encoding="utf-8") as filing_data_file:
        json.dump(all_declarations, filing_data_file)

    print('PARSING ALMOST FINISHED. Declaration data saved to declarations.json')

    return all_declarations


def parse_sheets_parallel(sheet_name: str, sheet_values, all_declarations: List[Dict[str, Any]]):
    r"""
    This function parses other sheets in the excel file.

    :param sheet_name: The name of the sheet. This name is used to identify the section of the filing.
    :param sheet_values: The sheet data from the excel file.
    :param all_declarations: A list of dictionary values result from the parsed `Declarations` sheet.
    """
    try:

        """Parse other sheets"""
        ALL_SHEETS_DATA: List[ExcelData] = []

        sheet_keys, *sheet_data = sheet_values

        for s_data in sheet_data:
            additional_data: ExcelData = {
                'section': sheet_name.replace(" ", ""),  # type: ignore
                'status': 'opened',
                "data": {}
            }  # type: ignore

            for col_key, col_data in zip(sheet_keys, s_data):

                # add the year from declarations
                c_key = str(col_key).lower()

                if c_key == 'unique id':

                    # set a flag for found unique id
                    unique_id_found = False

                    for _, data in enumerate(all_declarations):

                        # sheet_name is the key in the dictionary
                        # The type of values are list[str] or str
                        data_value = data.get(
                            sheet_name, None)  # type: ignore

                        if isinstance(data_value, list):

                            if str(col_data) in data_value:
                                additional_data['year'] = data.get(  # type: ignore
                                    'year')
                                unique_id_found = True
                                break

                            else:
                                continue

                        if str(col_data) == data_value:
                            additional_data['year'] = data.get(  # type: ignore
                                'year')
                            unique_id_found = True
                            break
                        else:
                            continue

                    if not unique_id_found:
                        additional_data['year'] = str(datetime.now().year)

                # TODO filingId will be added

                # process the rest of the data
                formatted_s_data = [
                    val.strftime(DATETIME_FORMAT) if isinstance(
                        val, date) else val
                    for val in s_data
                ]

            # Syntatic sugar for python update.
            additional_data['data'] |= dict(  # type: ignore
                zip(sheet_keys, formatted_s_data))  # type: ignore

            ALL_SHEETS_DATA.append(additional_data)

        return ALL_SHEETS_DATA

        # save users to clerk and get a list
        # iterate through clerk result and from the parse_user_sheet() result, extract matching
        # data for saving into the Users and ClerkUser tables into SaveUserType and ClerkUserType
        # objects.
        # save the data into the database
        # FOR EACH FILING: per the current user extracted from the excel sheet, update the filing userId property in ALL_SHEETS
        # which have the same value of Creator as the manualId of the user. Save the filing with extracted properties
        # into Filing table. get the id of filing saved.
        # FilingData: get the id of the saved filing, the data from the filing, section, userId, and save

    except (FileNotFoundError, ValueError, Exception) as ex:
        if isinstance(ex, ValueError):
            print(f"File processing error: {ex}")

        elif isinstance(ex, FileNotFoundError):
            print("File Not found error")

        else:
            raise ex


async def parse_all_sheets():
    workbook, _, _, other_sheet_names = get_workbook_and_sheet_names(
        USERS_SHEET_NAME, DECLARATIONS_SHEET_NAME
    )

    declarations = parse_declaration_sheet()

    sheets_data = [(extract_sheet(workbook, sheet_name))
                   for sheet_name in other_sheet_names]

    to_exec = [(sheet_name, sheet_data, declarations)
               for sheet_name, sheet_data in zip(other_sheet_names, sheets_data)]

    with Pool(processes=2) as pool:

        sheet_results = None
        timeout_seconds = 1

        try:
            result = pool.starmap_async(
                parse_sheets_parallel, to_exec, chunksize=10)  # type: ignore

            sheet_results = result.get(timeout=timeout_seconds)

            with open("filingData.json", "w+", encoding="utf-8") as filing_data_file:
                json.dump(sheet_results, filing_data_file)

            print('PARSING FINISHED. Filing data saved to filingData.json')

            return sheet_results

        # The timeout_seconds value may be increased if your machine is slow
        except TimeoutError:
            print(
                f"The result did not arrive within the {timeout_seconds} seconds timeout")

        finally:
            workbook.close()


async def save_to_database():
    # TODO Remove the parsing of datetime from the user sheet function
    current_date = datetime.now()

    """get all parsed data"""
    excel_users: List[UserType] = parse_user_sheet()

    # type: ignore
    all_filings: List[List[ExcelData]] = \
        await parse_all_sheets()  # type: ignore

    # unpack a list of lists
    excel_filings = list(itertools.chain.from_iterable(all_filings))

    clerk_users_to_save: List[SaveClerkUserType] = [
        extract_user(user) for user in excel_users
    ]  # type: ignore

    """Save clerk users to database"""
    saved_clerk_users = await asyncio.gather(
        *[save_user_to_clerk(user) for user in clerk_users_to_save]
    )

    """construct the users to save in the database"""
    users_to_save_in_database = []
    clerk_users_to_save_in_database = []
    filings_data_to_save = []

    # map emails to creator id for quick lookup
    creator_id_to_email = {}

    # map user email to user id for fast lookup
    # filings are numerous, this will be helpful
    email_to_user_id = {}

    for user in excel_users:
        if not creator_id_to_email.get(user['filingId']) and user.get('filingId'):
            creator_id_to_email[user['filingId']] = user['email']

    for user in excel_users:

        for c_user in saved_clerk_users:

            if user.get('email') == \
                    c_user.email_addresses[0].email_address:  # type: ignore

                clerkUserId: str = c_user.id  # type: ignore

                # construct user for database
                user_to_save: SaveUserType = construct_user_to_save(
                    user, clerkUserId)

                users_to_save_in_database.append(user_to_save)

                # map id to email for filing construction
                email_to_user_id[user_to_save['email']
                                 ] = user_to_save.get('id')

                # construct clerk user for database
                clerk_user_to_save: ClerkUserType = {
                    'id': clerkUserId,
                    'data': json.dumps(c_user),
                    'createdAt': current_date,
                    'updatedAt': current_date
                }

                clerk_users_to_save_in_database.append(clerk_user_to_save)

    """Construct filings and filings data"""
    for filing in excel_filings:

        creator_id = filing['data'].get('Creator')

        creator_email = creator_id_to_email.get(creator_id)

        user_id_for_filing: str = email_to_user_id.get(
            creator_email)  # type: ignore

        # construct filing
        filing_to_save: FilingType = {
            'userId': user_id_for_filing,
            'year': filing.get('year', '2024'),
            'status': filing.get('status', 'opened'),
            'createdAt': current_date,
            'updatedAt': current_date,
        }  # type: ignore

        # SAVE FILING HERE. The filing id will be used next
        saved_filing = {'id': 'id'}  # dummy data

        # construct filingData for user
        filing_data_to_save: FilingDataType = {
            'userId': user_id_for_filing,
            'filingId': saved_filing.id,
            'section': filing.get('section', ''),
            'createdAt': current_date,
            'updatedAt': current_date,
        }  # type: ignore

        filings_data_to_save.append(filing_data_to_save)


if __name__ == "__main__":
    asyncio.run(parse_all_sheets())
