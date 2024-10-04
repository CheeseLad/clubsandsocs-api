from typing import Annotated, TypeAlias

from fastapi import FastAPI, Path

from api.scraper import (
    Activity,
    ClubSoc,
    CommitteeMember,
    Event,
    GroupType,
    Info,
    Scraper,
)

app = FastAPI(
    version="2.0",
    title="Clubs & Societies API",
    description="API to fetch information about clubs and societies from university websites using the Assure Memberships Platform.",
    docs_url="/",
)
scraper = Scraper()

SITE_PARAM: TypeAlias = Annotated[
    str,
    Path(
        description="University clubs & societies website domain.",
        example="dcuclubsandsocs.ie",
    ),
]
TYPE_PARAM: TypeAlias = Annotated[
    GroupType, Path(description="Type of group.", example="society")
]
ID_PARAM: TypeAlias = Annotated[
    str, Path(description="ID of the club or society.", example="redbrick")
]


@app.get(
    "/{site}/{type}/{id}/activities", summary="Get a club or society's activities."
)
async def get_activities(
    site: SITE_PARAM,
    type: TYPE_PARAM,
    id: ID_PARAM,
) -> list[Activity]:
    return await scraper.fetch_activities(site, id, type)


@app.get("/{site}/{type}/{id}/events", summary="Get a club or society's events.")
async def get_events(
    site: SITE_PARAM,
    type: TYPE_PARAM,
    id: ID_PARAM,
) -> list[Event]:
    return await scraper.fetch_events(site, id, type)


@app.get(
    "/{site}/{type}/{id}/committee",
    summary="Get a club or society's committee members.",
)
async def get_committee(
    site: SITE_PARAM,
    type: TYPE_PARAM,
    id: ID_PARAM,
) -> list[CommitteeMember]:
    return await scraper.fetch_committee(site, id, type)


@app.get(
    "/{site}/{type}/{id}/gallery", summary="Get a club or society's gallery of photos."
)
async def get_gallery(
    site: SITE_PARAM,
    type: TYPE_PARAM,
    id: ID_PARAM,
) -> list[str]:
    return await scraper.fetch_gallery(site, id, type)


@app.get("/{site}/{type}", summary="List clubs or societies in a university.")
async def get_group_items(
    site: SITE_PARAM,
    type: TYPE_PARAM,
) -> list[ClubSoc]:
    return await scraper.fetch_group(site, type)


@app.get("/{site}/{type}/{id}", summary="Get info about a club or society.")
async def get_info(site: SITE_PARAM, type: TYPE_PARAM, id: ID_PARAM) -> Info:
    return await scraper.fetch_info(site, id, type)
