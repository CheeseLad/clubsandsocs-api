import asyncio
import datetime
import json
import re
import time
import uuid
from collections.abc import Awaitable, Callable

import pytz
import requests
from bs4 import BeautifulSoup

from api.scraper import ClubSoc, CommitteeMember, Event, GroupType, Info, InfoLink

RUBRIC_URL = "api.hellorubric.com"
EVENT_DETAILS_ENDPOINT = (
    "https://appserver.getqpay.com:9090/"
    "AppServerSwapnil/event/details"
)
DUBLIN_TZ = pytz.timezone("Europe/Dublin")


async def fetch_group(
    post: Callable[[str, dict[str, str]], Awaitable[bytes]],
    site: str,
    group_type: GroupType,
) -> list[ClubSoc]:
    """Fetch clubs or societies from a Rubric-powered site."""
    type_str = "societies" if group_type == GroupType.SOCIETY else "clubs"
    payload = {
        "firstCall": True,
        "sortType": "itemName",
        "desiredType": type_str,
        "limit": 12,
        "offset": 0,
        "sortDirection": "asc",
        "searchQuery": "",
        "eventsPeriodFilter": "All",
        "sessionid": str(uuid.uuid4()),
        "currentUrl": f"https://campus.hellorubric.com/search?type={type_str}",
        "device": "web_portal",
        "version": 4,
        "timestamp": int(time.time() * 1000),
    }

    form_data = {
        "endpoint": "getUnifiedSearch",
        "details": json.dumps(payload),
    }

    response = await post(RUBRIC_URL, form_data)
    data = json.loads(response)

    items = _extract_search_results(data)
    return [
        ClubSoc(
            id=str(item.get("societyid") or item.get("id") or ""),
            name=item.get("title") or item.get("name", ""),
            is_locked=False,
        )
        for item in items
        if item.get("title") or item.get("name")
    ]


def _extract_search_results(data):
    """Extract list of result items from search API response."""
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []
    for key in ("results", "items", "data", "societies", "clubs"):
        value = data.get(key)
        if isinstance(value, list):
            return value
    return []


async def fetch_committee(
    post: Callable[[str, dict[str, str]], Awaitable[bytes]],
    site: str,
    group_type: GroupType,
    id: str,
) -> list[CommitteeMember]:
    """Fetch committee members for a Rubric-powered site."""
    payload = {
        "societyid": id,
        "domain": "campus.hellorubric.com",
        "currentUrl": f"https://campus.hellorubric.com/?s={id}",
        "device": "web_portal",
        "version": 4,
        "timestamp": int(time.time() * 1000),
    }

    form_data = {
        "endpoint": "getSocietyLandingPage",
        "details": json.dumps(payload),
    }

    response = await post(RUBRIC_URL, form_data)
    data = json.loads(response)

    committee: list[CommitteeMember] = []

    for section in data.get("sections", []):
        if section.get("sectionname") == "Committee":
            for member in section.get("array", []):
                committee.append(
                    CommitteeMember(
                        name=member.get("title"),
                        position=member.get("subtitle"),
                    )
                )
            break

    return committee


async def fetch_events(
    post: Callable[[str, dict[str, str]], Awaitable[bytes]],
    site: str,
    group_type: GroupType,
    id: str,
) -> list[Event]:
    """Fetch events for a Rubric-powered site."""
    payload = {
        "societyid": id,
        "domain": "campus.hellorubric.com",
        "currentUrl": f"https://campus.hellorubric.com/?s={id}",
        "device": "web_portal",
        "version": 4,
        "timestamp": int(time.time() * 1000),
    }

    form_data = {
        "endpoint": "getSocietyLandingPage",
        "details": json.dumps(payload),
    }

    response = await post(RUBRIC_URL, form_data)
    data = json.loads(response)

    events: list[Event] = []

    for section in data.get("sections", []):
        if section.get("sectionname") == "Events":
            event_items = [
                event for event in section.get("array", [])
                if event.get("eventid")
            ]

            detail_tasks = [
                _fetch_event_details(post, event["eventid"], id)
                for event in event_items
            ]
            details_list = await asyncio.gather(*detail_tasks)

            for details in details_list:
                if not details:
                    continue

                start_str = _parse_datetime(details.get("eventTime"))
                end_str = _parse_datetime(details.get("eventEndTime"))

                day = ""
                start = _utc_now()
                end = _utc_now()

                if start_str:
                    try:
                        dt = datetime.datetime.fromisoformat(start_str)
                        day = dt.strftime("%A").lower()
                        start = _localize_to_utc(dt)
                    except ValueError:
                        pass

                if end_str:
                    try:
                        end = _localize_to_utc(
                            datetime.datetime.fromisoformat(end_str)
                        )
                    except ValueError:
                        pass

                event_status = details.get("eventStatus")
                if event_status == "Offline":
                    event_type = "IN-PERSON"
                else:
                    event_type = event_status or "IN-PERSON"

                cost = _get_event_cost(details)
                capacity = details.get("maxTickets")
                if isinstance(capacity, int):
                    capacity = capacity if capacity > 0 else None
                else:
                    capacity = None

                events.append(
                    Event(
                        name=details.get("eventName", ""),
                        image=details.get("bannerImageURL"),
                        start=start,
                        end=end,
                        day=day,
                        cost=cost,
                        capacity=capacity,
                        type=event_type,
                        location=details.get("eventAddress"),
                        description=_strip_html(
                            details.get("eventDescription")
                        ),
                    )
                )

            break

    return events


async def fetch_info(
    post: Callable[[str, dict[str, str]], Awaitable[bytes]],
    site: str,
    group_type: GroupType,
    id: str,
) -> Info:
    """Fetch info for a Rubric-powered site."""
    payload = {
        "societyid": id,
        "domain": "campus.hellorubric.com",
        "currentUrl": f"https://campus.hellorubric.com/?s={id}",
        "device": "web_portal",
        "version": 4,
        "timestamp": int(time.time() * 1000),
    }

    form_data = {
        "endpoint": "getSocietyLandingPage",
        "details": json.dumps(payload),
    }

    response = await post(RUBRIC_URL, form_data)
    data = json.loads(response)

    name = data.get("name")
    icon = data.get("logo_uploaded")
    title = data.get("name")
    about = data.get("description")
    links = _extract_links(data)

    return Info(
        id=id,
        name=name or "",
        icon=icon,
        title=title or "",
        about=about,
        links=links or None,
    )


async def fetch_links(
    post: Callable[[str, dict[str, str]], Awaitable[bytes]],
    site: str,
    group_type: GroupType,
    id: str,
) -> list[InfoLink]:
    """Fetch links for a Rubric-powered site."""
    payload = {
        "societyid": id,
        "domain": "campus.hellorubric.com",
        "currentUrl": f"https://campus.hellorubric.com/?s={id}",
        "device": "web_portal",
        "version": 4,
        "timestamp": int(time.time() * 1000),
    }

    form_data = {
        "endpoint": "getSocietyLandingPage",
        "details": json.dumps(payload),
    }

    response = await post(RUBRIC_URL, form_data)
    data = json.loads(response)
    return _extract_links(data)


def _extract_links(data: dict) -> list[InfoLink]:
    """Extract links from Rubric API response data."""
    links: list[InfoLink] = []

    if data.get("discordurl"):
        links.append(InfoLink("Discord Server", data["discordurl"]))

    email_name = data.get("societyemail")
    email_domain = data.get("emaildomain")
    if email_name and email_domain:
        email = email_name if "@" in email_name else f"{email_name}@{email_domain}"
        links.append(InfoLink("Email Society", f"mailto:{email}"))

    if data.get("facebookurl"):
        links.append(InfoLink("Facebook Page", data["facebookurl"]))

    if data.get("instagramurl"):
        links.append(InfoLink("Instagram Profile", data["instagramurl"]))

    if data.get("linkedinurl"):
        links.append(InfoLink("LinkedIn Profile", data["linkedinurl"]))

    if data.get("tiktokurl"):
        links.append(InfoLink("TikTok Profile", data["tiktokurl"]))

    return links


async def _fetch_event_details(
    post: Callable[[str, dict[str, str]], Awaitable[bytes]],
    event_id: str,
    society_id: str,
) -> dict | None:
    details_payload = {
        "eventId": str(event_id),
        "currentUrl": f"https://campus.hellorubric.com/?s={society_id}",
        "device": "web_portal",
        "version": 4,
        "timestamp": int(time.time() * 1000),
    }

    form_data = {
        "details": json.dumps(details_payload),
        "endpoint": EVENT_DETAILS_ENDPOINT,
    }

    try:
        response = await post(RUBRIC_URL, form_data)
        data = json.loads(response)
        if not data.get("success"):
            return None
        return data.get("eventDetails")
    except Exception:
        return None


def _parse_datetime(value: str | None) -> str | None:
    if not value:
        return None

    formats = [
        "%a, %d %b %Y %I:%M %p",
        "%a, %d %b %Y, %I:%M %p",
        "%a, %d %b %Y %I.%M %p",
        "%a, %d %b %Y, %I.%M %p",
    ]

    for fmt in formats:
        try:
            return datetime.datetime.strptime(value, fmt).isoformat()
        except ValueError:
            pass

    return None


def _strip_html(html: str | None) -> str | None:
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    return text if text else None


def _get_event_cost(details: dict) -> float:
    possible_fields = [
        "eventCost",
        "cost",
        "price",
        "ticketPrice",
        "eventPrice",
    ]

    for field in possible_fields:
        value = details.get(field)
        if value is None:
            continue
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r"\d+(?:\.\d+)?", str(value))
        if match:
            return float(match.group())

    return 0.0


def _localize_to_utc(dt: datetime.datetime) -> datetime.datetime:
    return DUBLIN_TZ.localize(dt).astimezone(pytz.utc)


def _utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)
