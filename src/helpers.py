from datetime import datetime
import os
from pathlib import Path
import functools
import random

from constants import DATETIME_FORMAT, FILE_NAME


@functools.lru_cache
def find_excel_file():

    try:
        cwd = os.getcwd()
        resolved_paths = [path.resolve()
                          for path in Path(cwd).rglob("*migration_data.xlsx")]

        if len(resolved_paths) == 0:
            raise FileNotFoundError

        filenames = [str(path).rsplit('/', maxsplit=1)[-1]
                     for path in resolved_paths]

        is_filename = FILE_NAME in filenames

        if not is_filename:
            raise FileNotFoundError(f'Migration filename must be {FILE_NAME}')

        return resolved_paths[0]
    except:
        raise


def process_col_value(col_key: str, col_val) -> str:
    r"""Utility function that parses columns with datetime and accountType

    :param col_key: The key of the column. Columns of `datetime` type,
    will be processed specially, together with columns that start with `Admin` and `Phone`. Any `col_val` that
      is `None` will be assigned a unqiuely generated
    value.

    :param col_val: The value of the column.

    """
    if isinstance(col_val, datetime):
        return col_val.strftime(DATETIME_FORMAT)

    if col_key.startswith("Admin"):
        return "user" if col_val == "no" or None else "admin"

    if col_key.startswith("Phone"):
        if col_val is None:
            return random_phone_generator()
        elif isinstance(col_val, int):
            return str(col_val)
        return col_val

    return col_val


def random_phone_generator():
    r"""Generates a random phone number with country code +41"""

    num_str = ''.join([str(random.randrange(0, 9)) for _ in range(0, 9)])

    return '+41' + num_str
