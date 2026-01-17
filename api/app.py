from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, TypeAlias

from fastapi import FastAPI, Path

from api.scraper import (
    Activity,
    ClubSoc,
    CommitteeMember,
    Event,
    Fixture,
    GroupType,
    Info,
    InfoLink,
    InfoAward,
    Scraper,
)

from fastapi.middleware.cors import CORSMiddleware



scraper = Scraper()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    # Close session on shutdown
    await scraper.session.close()


app = FastAPI(
    version="2.0",
    title="Clubs & Societies API",
    description="API to fetch information about clubs and societies from university websites using the Assure Memberships Platform.",
    docs_url="/",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

SITE_PARAM: TypeAlias = Annotated[
    str,
    Path(
        description="University clubs & societies website domain.",
        examples=["dcuclubsandsocs.ie"],
    ),
]
TYPE_PARAM: TypeAlias = Annotated[
    GroupType, Path(description="Type of group.", examples=["society"])
]
ID_PARAM: TypeAlias = Annotated[
    str, Path(description="ID of the club or society.", examples=["redbrick"])
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

@app.get(
    "/{site}/{type}/{id}/fixtures", summary="Get a club or society's fixtures."
)
async def get_fixtures(
    site: SITE_PARAM,
    type: TYPE_PARAM,
    id: ID_PARAM,
) -> list[Fixture]:
    return await scraper.fetch_fixtures(site, id, type)

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


@app.get("/{site}/{type}/{id}/awards", summary="Get a club or society's list of awards.")
async def get_awards(
    site: SITE_PARAM,
    type: TYPE_PARAM,
    id: ID_PARAM,
) -> list[InfoAward]:
    return await scraper.fetch_awards(site, id, type)

@app.get("/{site}/{type}/{id}/links", summary="Get a club or society's list of links.")
async def get_links(
    site: SITE_PARAM,
    type: TYPE_PARAM,
    id: ID_PARAM,
) -> list[InfoLink]:
    return await scraper.fetch_links(site, id, type)
