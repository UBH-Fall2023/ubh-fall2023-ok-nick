import json
from dataclasses import dataclass
from typing import Optional
from urllib.request import Request, urlopen

ENDPOINT = "https://buffalo.navigate.eab.com/api/v1/reg/dashboard/courses/"


@dataclass
class Section:
    id: str
    name: str


# sessionid cookie from UB navigate
# expect 32 characters
def classes(token: str) -> Optional[list[Section]]:
    request = Request(
        ENDPOINT,
        headers={
            "Cookie": f"sessionid={token}",
        },
    )

    with urlopen(request) as response:
        try:
            result = json.loads(response.read())
        except json.JSONDecodeError:
            # in this case it is most likely not a valid token
            # TODO: better validation check
            return None

        sections = []
        for section in result["section"].values():
            course = result["course"][str(section["course"])]
            # TODO lots of valuable information can be stored
            sections.append(
                Section(
                    # first 4 characters is the semester id
                    # from 4 to end is the class id (aka class number)
                    id=str(section["nk"][4:]),
                    name=str(course["nk"]),
                )
            )

        return sections
