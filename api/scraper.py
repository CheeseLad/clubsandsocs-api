import dataclasses
import datetime
import enum
import re

import aiohttp
from bs4 import BeautifulSoup, ResultSet, Tag

from api import types, utils


class GroupType(enum.Enum):
    """The group type."""

    CLUB = "club"
    """A club."""
    SOCIETY = "society"
    """A society."""


class EventType(enum.Enum):
    """The event type."""

    ACTIVITY = "activities"
    """An activity."""
    EVENT = "events"
    """An event."""
    FIXTURE = "fixtures"
    """A fixture."""


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:130.0) Gecko/20100101 Firefox/130.0"
}
CLUB_SOC_PATH = "{site}/{type}/{id}"


@dataclasses.dataclass
class Event:
    """An event."""

    name: str
    """The event name."""
    image: str | None
    """The event poster."""
    start: datetime.datetime
    """The event's start time."""
    end: datetime.datetime
    """The event's end time."""
    day: str
    """The day the event is on (`monday`, `tuesday`, etc.)."""
    cost: float
    """The event cost."""
    capacity: int | None
    """The event maximum capacity."""
    type: str
    """The event type. Usually `IN-PERSON` or `VIRTUAL`."""
    location: str | None
    """The event location."""
    description: str
    """The event description."""


@dataclasses.dataclass
class Activity:
    """A weekly activity."""

    name: str
    """The activity name."""
    image: str | None
    """The activity poster."""
    day: str
    """The day the activity is on (`monday`, `tuesday`, etc.)."""
    start: datetime.datetime
    """The activity start time."""
    end: datetime.datetime
    """The activity end time."""
    capacity: int | None
    """The activity maximum capacity."""
    type: str
    """The activity type. Usually `IN-PERSON` or `VIRTUAL`."""
    location: str | None
    """The activity location."""
    description: str
    """The activity description."""
    
@dataclasses.dataclass
class Fixture:
    """A fixture."""

    name: str
    """The fixture name."""
    image: str | None
    """The fixture poster."""
    start: datetime.datetime
    """The fixture's start time."""
    competition: str
    """The fixture competition."""
    type: str
    """The fixture type. Usually `HOME` or `AWAY`."""
    location: str | None
    """The fixture location."""
    description: str
    """The fixture description."""


@dataclasses.dataclass
class CommitteeMember:
    """A committee member."""

    name: str | None
    """Their name. (`None` if hidden)."""
    position: str
    """Their committee position."""


@dataclasses.dataclass
class ClubSoc:
    """A club or society."""

    id: str
    """The ID used in the club or society's page URL."""
    name: str
    """The club or society name."""
    is_locked: bool
    """Whether the club or society is locked."""

@dataclasses.dataclass
class InfoLink:
    """A link in the club or society's info."""

    name: str
    """The link name."""
    url: str
    """The link URL."""


@dataclasses.dataclass
class Info:
    """Info on a club or society."""

    id: str
    """The ID used in the club or society's page URL."""
    name: str
    """The club or society name."""
    icon: str | None
    """The club or society icon."""
    title: str
    """The club or society title."""
    about: str | None
    """Info on the club or society."""

    links: list[InfoLink] | None
    """Links provided by the club or society."""


@dataclasses.dataclass
class InfoAward:
    """An award in the club or society's info."""

    year: str
    """The year the award was won."""
    name: str
    """The award name."""
    winner: str
    """The award winner."""
    type: str
    """The award type."""


class Scraper:
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    @property
    def session(self) -> aiohttp.ClientSession:
        """The aiohttp ClientSession to use for requests."""
        if not self._session:
            self._session = aiohttp.ClientSession()

        return self._session

    async def get(self, url: str) -> bytes:
        """Make a `GET` request to `url`."""
        async with self.session.request(
            "GET",
            f"https://{url}",
        ) as r:
            r.raise_for_status()
            return await r.read()

    async def fetch_group(self, site: str, group_type: GroupType) -> list[ClubSoc]:
        """Fetch items items belonging to a group (clubs or societies)."""
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

    async def _fetch_events_activities_fixtures(
        self, site: str, id: str, group_type: GroupType, event_type: EventType
    ) -> list[Event | Activity | Fixture]:
        """Fetch events, activities or fixtures for a club or society."""
        data = await self.get(
            CLUB_SOC_PATH.format(site=site, type=group_type.value, id=id)
        )

        soup = BeautifulSoup(data, "html5lib")
        events_data = soup.find("div", attrs={"id": event_type.value})

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

            def get_info(edata: ResultSet[Tag], name: str) -> str | None:
                for tag in edata:
                    if name in tag.text.lower():
                        d = tag.find("b")
                        assert d is not None
                        return d.text

            capacity = get_info(event_data, "max")
            location = get_info(events_info_hidden[i], "location")

            description_tags: ResultSet[Tag] = events_info_hidden[i].findAll("p")
            description = "\n\n".join(
                [
                    utils.strip_whitespace(description_tag.text)
                    for description_tag in description_tags
                ]
            )

            start_str = get_info(event_data, "start")
            assert start_str is not None
            if event_type is not EventType.FIXTURE:
                end_str = get_info(event_data, "end")
                #assert end_str is not None

            if event_type is EventType.ACTIVITY:
                type_ = get_info(event_data, "activity")
                assert type_ is not None

                day = get_info(event_data, "day")[:-1].lower()
                assert day is not None
                upcoming_date = utils.str_to_datetime(day)

                # if today is the same day as the activity, it is
                # converted to a week ahead so we undo this
                today = datetime.datetime.now(datetime.timezone.utc)
                if upcoming_date.weekday() == today.weekday():
                    upcoming_date -= datetime.timedelta(weeks=1)

                start = utils.str_to_datetime(start_str, upcoming_date)
                end = utils.str_to_datetime(end_str, upcoming_date)

                events.append(
                    Activity(
                        name=event_name,
                        image=event_image,
                        day=day,
                        start=start,
                        end=end,
                        capacity=int(capacity) if capacity is not None else capacity,
                        type=type_,
                        location=location,
                        description=description,
                    )
                )
            elif event_type is EventType.FIXTURE:
                type_ = get_info(event_data, "fixture")
                assert type_ is not None
                
                competition = None
                end_str = get_info(event_data, "end")
                #assert end_str is not None
                start = utils.str_to_datetime(start_str)

                events.append(
                    Fixture(
                        name=event_name,
                        image=event_image,
                        start=start,
                        competition=None,
                        type=type_,
                        location=location,
                        description=description,
                    )
                )
            else:
                type_ = get_info(event_data, "event")
                assert type_ is not None

                start = utils.str_to_datetime(start_str)
                day = start.strftime("%A").lower()
                end = utils.str_to_datetime(end_str, start)
                cost = get_info(event_data, "cost")
                assert cost is not None

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
                        day=day,
                        start=start,
                        end=end,
                        cost=cost,
                        capacity=int(capacity) if capacity is not None else capacity,
                        type=type_,
                        location=location,
                        description=description,
                    )
                )

            i += 1

        return events

    async def fetch_committee(
        self, site: str, id: str, group_type: GroupType
    ) -> list[CommitteeMember]:
        """Fetch committee members for a club or society."""
        data = await self.get(
            CLUB_SOC_PATH.format(site=site, type=group_type.value, id=id)
        )

        soup = BeautifulSoup(data, "html5lib")
        committee_table = soup.find("div", attrs={"id": "committee_table"})
        assert isinstance(committee_table, Tag)
        committee_roles: ResultSet[Tag] = committee_table.find_all("th")
        committee_names: ResultSet[Tag] = committee_table.find_all("td")

        committee: list[CommitteeMember] = []
        for role, name_ in zip(committee_roles, committee_names):
            committee.append(
                CommitteeMember(
                    name=None
                    if (name := name_.text.strip()) == "(name hidden)"
                    else name,
                    position=role.text.strip(),
                )
            )

        return committee

    async def fetch_gallery(
        self, site: str, id: str, group_type: GroupType
    ) -> list[str]:
        """Fetch images in the gallery for a club or society."""
        data = await self.get(
            CLUB_SOC_PATH.format(site=site, type=group_type.value, id=id)
        )
        soup = BeautifulSoup(data, "html5lib")
        gallery = soup.find(
            "div", attrs={"class": "row photo_gallery mt-5 overflow-auto"}
        )
        if not gallery:
            return []

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
        self, site: str, id: str, group_type: GroupType
    ) -> list[Activity]:
        """Fetch activities for a club or society."""
        activities = await self._fetch_events_activities_fixtures(
            site, id, group_type, EventType.ACTIVITY
        )
        assert types.is_obj_list(activities, Activity)
        return activities

    async def fetch_events(
        self, site: str, id: str, group_type: GroupType
    ) -> list[Event]:
        """Fetch events for a club or society."""
        events = await self._fetch_events_activities_fixtures(
            site, id, group_type, EventType.EVENT
        )
        assert types.is_obj_list(events, Event)
        return events
    
    async def fetch_fixtures(
        self, site: str, id: str, group_type: GroupType
    ) -> list[Fixture]:
        """Fetch fixtures for a club or society."""
        fixtures = await self._fetch_events_activities_fixtures(
            site, id, group_type, EventType.FIXTURE
        )
        assert types.is_obj_list(fixtures, Fixture)
        return fixtures

    async def fetch_info(
        self,
        site: str,
        id: str,
        group_type: GroupType,
    ) -> Info:
        """Fetch info on a club or society."""
        data = await self.get(
            CLUB_SOC_PATH.format(site=site, type=group_type.value, id=id)
        )
        soup = BeautifulSoup(data, "html5lib")

        name = soup.find("div", attrs={"class": "section-heading text-center pt-5"})
        assert isinstance(name, Tag)
        name = utils.strip_whitespace(name.text)

        table = soup.find("div", attrs={"id": "about_table"})
        assert isinstance(table, Tag)
        container = table.find("div", attrs={"class": "card-body"})
        assert isinstance(container, Tag)

        about_div = container.find("div", attrs={"class": "mb-n2"})
        if about_div:
            assert isinstance(about_div, Tag)
            about_div.decompose()

        infos: ResultSet[Tag] = container.find_all(recursive=False)

        info = "\n".join([tag.text for tag in infos])
        info = utils.strip_whitespace(info)

        section = soup.find("section", attrs={"class": "clearfix faded-bg"})
        assert isinstance(section, Tag)

        title = section.find("div", attrs={"class": "col-12 text-center"})
        assert isinstance(title, Tag)
        title = utils.strip_whitespace(title.text)

        img_container = section.find(
            "div", attrs={"class": "wow fadeInDown w-100 mb-3"}
        )
        if not img_container:
            img = None
        else:
            assert isinstance(img_container, Tag)
            img = img_container.find("img")
            assert isinstance(img, Tag)

            img = img["src"]
            if isinstance(img, list):
                img = img[0]
                

        return Info(
            id=id,
            name=name,
            icon=img,
            title=title,
            about=info or None,
            links=await self.fetch_links(site, id, group_type) or None,
        )
        
        
    async def fetch_awards(
        self, site: str, id: str, group_type: GroupType
    ) -> list[InfoAward]:
        """Fetch awards for a club or society."""
        data = await self.get(
            CLUB_SOC_PATH.format(site=site, type=group_type.value, id=id)
        )
        soup = BeautifulSoup(data, "html5lib")
        awards_table = soup.find("div", attrs={"id": "awards_table"})
        assert isinstance(awards_table, Tag)
    
        awards: ResultSet[Tag] = awards_table.find_all("tr")
        awards_list: list[InfoAward] = []
    
        for award in awards:
            year = award.find("th").text.strip()
            name_tag = award.find("td").find("b")
            name = name_tag.text.strip() if name_tag else ""
            winner_tag = award.find("td").find("i")
            print(winner_tag)
            winner = winner_tag.get("title", "").strip() if winner_tag else ""
            type_ = award.find("td").find("small").text.strip().replace(":","")
            
            
            awards_list.append(InfoAward(year, name, winner, type_))

        return awards_list
    
    async def fetch_links(
        self, site: str, id: str, group_type: GroupType
    ) -> list[InfoLink]:
        """Fetch links for a club or society."""
        data = await self.get(
            CLUB_SOC_PATH.format(site=site, type=group_type.value, id=id)
        )
        soup = BeautifulSoup(data, "html5lib")
        links_table = soup.find("div", attrs={"id": "links_table"})
        assert isinstance(links_table, Tag)
        links: ResultSet[Tag] = links_table.find_all("a")

        links_list: list[InfoLink] = []
        for link in links:
            name = link.get("title") or link.text.strip()
            links_list.append(InfoLink(name, url=link["href"]))

        return links_list
