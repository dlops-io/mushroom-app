import os
from typing import Any, Dict, List
from dataaccess.session import database


async def browse(
    *,
    limit: int = -1
) -> List[Dict[str, Any]]:
    """
    Retrieve a list of rows based on filters
    """

    query = """
        select *
        from leaderboard
    """

    # limit
    if limit > 0:
        query += " limit " + str(limit)

    print("query", query)
    result = await database.fetch_all(query)

    return [prep_data(row) for row in result]


def prep_data(result) -> Dict[str, Any]:
    if result is None:
        raise ValueError("Tried to prepare null result")

    result = dict(result)
    return result
