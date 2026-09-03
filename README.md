# clubsandsocs-api

## Description

Allows you to get information about societies and clubs from university websites using the [Assure Memberships Platform](https://assurememberships.com) or [Rubric](https://campus.hellorubric.com) for use in other applications.

## Supported Sites (Rubric Platform)

- [DCU Clubs & Socs](https://campus.hellorubric.com/search?type=societies&country=IE&state=Leinster&universityid=541)
  - Site Code: `dcuclubsandsocs.ie`

Notes: 
- Instead of society names (redbrick), use their IDs instead (14412). 
- Only the following endpoints are supported for Rubric sites:
  - `/<site>/<type>/<id>/events` - Get all upcoming events for a club/society
  - `/<site>/<type>/<id>/committee` - Get the committee information for a club/society
  - `/<site>/<type>` - Get all clubs/societies for a university
  - `/<site>/<type>/<id>` - Get info for a club/society
  - `/<site>/<type>/<id>/links` - Get the social media links for a club/society

## Supported Sites (Assure Memberships Platform)

- [MU Clubs & Societies](https://mulife.ie/)
  - Site Code: `mulife.ie`
- [SETU Waterford Sports Clubs & Societies](https://waterford.sportsclubsandsocieties.setu.ie/)
  - Site Code: `waterford.sportsclubsandsocieties.setu.ie`
- [SETU Carlow Sports Clubs & Societies](https://carlow.sportsclubsandsocieties.setu.ie/)
  - Site Code: `carlow.sportsclubsandsocieties.setu.ie`
- [UL Clubs & Societies](https://ulwolves.ie/)
  - Site Code: `ulwolves.ie`
- [ATU Galway-Mayo Clubs & Socs](https://galwaymayo.atusulife.ie/)
  - Site Code: `galwaymayo.atusulife.ie`
- [ATU Sligo Clubs & Socs](https://sligo.atusulife.ie/)
  - Site Code: `sligo.atusulife.ie`
- [ATU Donegal Clubs & Socs](https://donegal.atusulife.ie/)
  - Site Code: `donegal.atusulife.ie`
  
## Supported Types

- `society`
- `club`

## Running the Project

### With Docker

1. Clone the repository
2. Run `docker compose up` to start the API server

### Without Docker

1. Clone the repository
2. Run `pip install -r requirements.txt` to install the required packages
3. (Linux/macOS) Run `granian --interface asgi api.app:app --loop uvloop --host 0.0.0.0 --port 4000` to start the API server
4. (Windows) Run `granian --interface asgi api.app:app --host 0.0.0.0 --port 4000` to start the API server

## Usage

The API has the following endpoints:

- `/<site>/<type>/<id>/activities` - Get all weekly activities for a club/society
- `/<site>/<type>/<id>/fixtures` - Get all upcoming fixtures for a club/society
- `/<site>/<type>/<id>/events` - Get all upcoming events for a club/society
- `/<site>/<type>/<id>/committee` - Get the committee information for a club/society
- `/<site>/<type>/<id>/gallery` - Get the gallery photos for a club/society
- `/<site>/<type>` - Get all clubs/societies for a university
- `/<site>/<type>/<id>` - Get info for a club/society
- `/<site>/<type>/<id>/awards` - Get the awards for a club/society
- `/<site>/<type>/<id>/links` - Get the social media links for a club/society

## API Usage Examples

- `/ulwolves.ie/society` - Get all societies in the University of Limerick
- `/mulife.ie/club/table-tennis/activities` - Get all weekly activities for the Table Tennis Club in Maynooth University
- `/carlow.sportsclubsandsocieties.setu.ie/society/science/events` - Get all upcoming events for the Science Society in SETU Carlow
- `/mulife.ie/society/esn/committee` - Get committee information for the Erasmus Student Network Society in Maynooth University
- `/galwaymayo.atusulife.ie/society/galway-engineering/gallery` - Get gallery photos for the Engineering Society in ATU Galway-Mayo
- `/ulwolves.ie/society/computer` - Get info on the Computer Society of the University of Limerick
