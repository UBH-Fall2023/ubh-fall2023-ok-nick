from typing import NamedTuple, Optional

from synapse.api.errors import HttpResponseException
from synapse.http.client import BaseHttpClient

ENDPOINT = "https://buffalo.navigate.eab.com/api/v1/reg/dashboard/courses/"


class Section(NamedTuple):
    id: str
    name: str
    section: str
    title: str
    description: str


# sessionid cookie from UB navigate
# expect 32 characters
async def classes(client: BaseHttpClient, token: str) -> Optional[list[Section]]:
    try:
        result = await client.get_json(
            ENDPOINT,
            headers={
                # b"Cookie": [f"sessionid={token}".encode()],
                b"Cookie": [b"sessionid=rd82n7gkozbgmzy5bfbb3f3jsgvnr5o7"]
            },
        )
    except HttpResponseException as e:
        # invalid token
        if e.code == 401:
            return None
        raise

    sections = []
    seen = set()
    for section in result["section"].values():
        id = section["nk"][4:]
        if id not in seen:
            seen.add(id)
            course = result["course"][str(section["course"])]
            # TODO lots of valuable information can be stored
            sections.append(
                Section(
                    # first 4 characters is the semester id
                    # from 4 to end is the class id (aka class number)
                    id=str(id),
                    name=str(course["nk"]),
                    section=section["cd"],
                    title=course["title"],
                    description=course["desc"],
                )
            )

    return sections
