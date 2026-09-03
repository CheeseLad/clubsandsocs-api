import re
from collections.abc import Awaitable, Callable

from bs4 import BeautifulSoup

from api.scraper import ClubSoc, GroupType


async def fetch_group(
    get: Callable[[str], Awaitable[bytes]],
    site: str,
    group_type: GroupType,
) -> list[ClubSoc]:
    """Fetch clubs or societies from an Assure Memberships-powered site."""
    data = await get(site)
    soup = BeautifulSoup(data, "html5lib")
    results = soup.find_all(
        "a",
        href=re.compile(
            r"{site}\/{group}\/.+".format(site=site, group=group_type.value)
        ),
    )

    clubsocs: list[ClubSoc] = []
    for res in results:
        if not res.get("title"):
            continue

        name = res["title"]
        locked = name.endswith("(awaiting committee unlock)")
        if locked:
            name = name.replace("(awaiting committee unlock)", "").strip()

        match = re.search(
            r"\/{group}\/(?P<id>.+)".format(group=group_type.value), res["href"]
        )
        if not match or not (id := match.group("id")):
            raise ValueError(f"could not get {group_type.value} id for '{name}'")

        clubsocs.append(
            ClubSoc(
                id=id,
                name=name,
                is_locked=locked,
            )
        )

    return clubsocs
