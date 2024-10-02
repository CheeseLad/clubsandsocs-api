import dataclasses
import datetime
import enum
import re

import aiohttp
from bs4 import BeautifulSoup, ResultSet, Tag

from api import types, utils


class GroupType(enum.Enum):
    CLUB = "club"
    SOCIETY = "society"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:130.0) Gecko/20100101 Firefox/130.0"
}
CLUB_SOC_PATH = "{site}/{type}/{name}"
WHITESPACE_REGEX = re.compile(r"^\s+|\s+$|\s+(?=\s)")


@dataclasses.dataclass
class Event:
    name: str
    image: str | None
    start: datetime.datetime
    end: datetime.datetime
    cost: float
    capacity: int
    type: str
    location: str
    description: str


@dataclasses.dataclass
class Activity:
    name: str
    image: str | None
    day: str
    start: datetime.datetime
    end: datetime.datetime
    capacity: int
    type: str
    location: str
    description: str


@dataclasses.dataclass
class CommitteeMember:
    name: str
    position: str


@dataclasses.dataclass
class ClubSoc:
    id: str
    name: str
    is_locked: bool


@dataclasses.dataclass
class Info:
    info: str


class Scraper:
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = aiohttp.ClientSession()

        return self._session

    async def get(self, url: str) -> bytes:
        async with self.session.request(
            "GET",
            f"https://{url}",
        ) as r:
            r.raise_for_status()
            return await r.read()

    async def fetch_group(self, site: str, group_type: GroupType) -> list[ClubSoc]:
        data = await self.get(
            site,
        )
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

    # TODO: use enum for event type
    # TODO: use 'id' instead of 'name' for parameter
    async def _fetch_events_activities(
        self, site: str, name: str, group_type: GroupType, event_type: str
    ) -> list[Activity | Event]:
        data = await self.get(
            CLUB_SOC_PATH.format(site=site, type=group_type.value, name=name)
        )

        soup = BeautifulSoup(data, "html5lib")
        events_data = soup.find("div", attrs={"id": event_type})

        if not events_data:
            return []

        assert isinstance(events_data, Tag)

        event_count = events_data.find(
            "span", attrs={"class": "float-right badge badge-light"}
        )
        assert event_count is not None
        event_count = int(event_count.text)

        if event_count < 1:
            return []

        event_table = events_data.find("div", attrs={"class": "table-responsive"})
        assert isinstance(event_table, Tag)

        events_info_list: ResultSet[Tag] = event_table.find_all(
            "tr", attrs={"class": "show_info pointer"}
        )
        events_info_hidden: ResultSet[Tag] = event_table.find_all(
            "tr", attrs={"class": "d-none"}
        )
        assert events_info_list is not None and events_info_hidden is not None

        events: list[Activity | Event] = []
        i = 0
        while i < len(events_info_list):
            event_info = events_info_list[i]

            event_image = event_info.find("img")
            assert isinstance(event_image, Tag | None)
            if event_image is not None:
                event_image = event_image["src"]
                if isinstance(event_image, list):
                    event_image = event_image[0]

            event_name = event_info.find("th", attrs={"class": "h5 align-middle"})
            assert isinstance(event_name, Tag)
            event_name = event_name.text.strip()

            i += 1

            event_info = events_info_list[i]
            event_data: ResultSet[Tag] = event_info.find_all(
                "td", attrs={"class": "text-center align-middle"}
            )

            def get_info(edata: ResultSet[Tag], index: int) -> str:
                d = edata[index].find("b")
                assert d is not None
                return d.text

            capacity = get_info(event_data, 4)
            type = get_info(event_data, 5)
            location = get_info(events_info_hidden, i)

            description_tags: ResultSet[Tag] = events_info_hidden[i].findAll("p")
            description = "\n\n".join(
                [
                    re.sub(
                        WHITESPACE_REGEX, "", description_tag.text.replace("\xa0", "")
                    )
                    for description_tag in description_tags
                ]
            )

            if event_type == "activities":
                day = get_info(event_data, 1)[:-1]
                upcoming_date = utils.str_to_datetime(day)
                start = utils.str_to_datetime(get_info(event_data, 2), upcoming_date)
                end = utils.str_to_datetime(get_info(event_data, 3), upcoming_date)

                events.append(
                    Activity(
                        name=event_name,
                        image=event_image,
                        day=day,
                        start=start,
                        end=end,
                        capacity=int(capacity),
                        type=type,
                        location=location,
                        description=description,
                    )
                )
            else:
                start = utils.str_to_datetime(get_info(event_data, 1))
                end = utils.str_to_datetime(get_info(event_data, 2), start)
                cost = get_info(event_data, 3)

                if cost == "FREE":
                    cost = 0
                else:
                    match = re.search(r"[0-9\.]+", cost)
                    assert match
                    cost = float(match.group())

                events.append(
                    Event(
                        name=event_name,
                        image=event_image,
                        start=start,
                        end=end,
                        cost=cost,
                        capacity=int(capacity),
                        type=type,
                        location=location,
                        description=description,
                    )
                )

            i += 1

        return events

    async def fetch_committee(
        self, site: str, name: str, group_type: GroupType
    ) -> list[CommitteeMember]:
        data = await self.get(
            CLUB_SOC_PATH.format(site=site, type=group_type.value, name=name)
        )

        soup = BeautifulSoup(data, "html5lib")
        committee_table = soup.find("div", attrs={"id": "committee_table"})
        assert isinstance(committee_table, Tag)
        committee_names: ResultSet[Tag] = committee_table.find_all("th")
        committee_roles: ResultSet[Tag] = committee_table.find_all("td")

        committee: list[CommitteeMember] = []
        for name_, role in zip(committee_names, committee_roles):
            committee.append(
                CommitteeMember(
                    name=name_.text.strip(),
                    position=role.text.strip(),
                )
            )

        return committee

    async def fetch_gallery(
        self, site: str, name: str, group_type: GroupType
    ) -> list[str]:
        data = await self.get(
            CLUB_SOC_PATH.format(site=site, type=group_type.value, name=name)
        )
        soup = BeautifulSoup(data, "html5lib")
        gallery = soup.find(
            "div", attrs={"class": "row photo_gallery mt-5 overflow-auto"}
        )
        assert isinstance(gallery, Tag)
        images: ResultSet[Tag] = gallery.find_all("img")

        urls: list[str] = []
        for img in images:
            img = img["src"]
            if isinstance(img, list):
                urls.append(img[0])
            else:
                urls.append(img)

        return urls

    async def fetch_activities(
        self, site: str, name: str, group_type: GroupType
    ) -> list[Activity]:
        activities = await self._fetch_events_activities(
            site, name, group_type, "activities"
        )
        assert types.is_obj_list(activities, Activity)
        return activities

    async def fetch_events(
        self, site: str, name: str, group_type: GroupType
    ) -> list[Event]:
        events = await self._fetch_events_activities(site, name, group_type, "events")
        assert types.is_obj_list(events, Event)
        return events

    async def fetch_info(
        self,
        site: str,
        name: str,
        group_type: GroupType,
    ) -> Info:
        data = await self.get(
            CLUB_SOC_PATH.format(site=site, type=group_type.value, name=name)
        )
        soup = BeautifulSoup(data, "html5lib")

        table = soup.find("div", attrs={"id": "about_table"})
        assert isinstance(table, Tag)
        container = table.find("div", attrs={"class": "card-body"})
        assert isinstance(container, Tag)
        about_div = container.find("div")
        assert isinstance(about_div, Tag)

        return Info(info=about_div.text)
