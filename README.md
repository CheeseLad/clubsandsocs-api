# clubsandsocs-api

## Description

Allows you to get information about societies and clubs from university websites using the [Assure Memberships Platform](https://assurememberships.com) for use in other applications.

## Supported Sites

- [DCU Clubs & Socs](https://dcuclubsandsocs.ie)
  - Site Code: `dcuclubsandsocs.ie`
- [MU Clubs & Societies](https://mulife.ie/)
  - Site Code: `mulife.ie`
- [SETU Waterford Sports Clubs & Societies](https://waterford.sportsclubsandsocieties.setu.ie/)
  - Site Code: `waterford.sportsclubsandsocieties.setu.ie`
- [UL Clubs & Societies](https://ulwolves.ie/)
  - Site Code: `ulwolves.ie`
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
3. Run `uvicorn api.app:app --host=0.0.0.0 --port=4000 --no-access-log` to start the API server

## Usage

The API has the following endpoints:

- `/<site>/<type>` - Get all clubs/societies for a university
- `/<site>/<type>/<id>/activities` - Get all weekly activities for a club/society
- `/<site>/<type>/<id>/events` - Get all upcoming events for a club/society
- `/<site>/<type>/<id>/committee` - Get the committee information for a club/society
- `/<site>/<type>/<id>/gallery` - Get the gallery photos for a club/society
- `/<site>/<type>/<id>` - Get info for a club/society

## API Usage Examples

- `/ulwolves.ie/society` - Get all societies in the University of Limerick
- `/mulife.ie/club/table-tennis/activities` - Get all weekly activities for the Table Tennis Club in Maynooth University
- `/dcuclubsandsocs.ie/society/redbrick/events` - Get all upcoming events for the Redbrick Society in DCU
- `/mulife.ie/society/esn/committee` - Get committee information for the Erasmus Student Network Society in Maynooth University
- `/dcuclubsandsocs.ie/society/media-production/gallery` - Get gallery photos for the Media Production Society in DCU
- `/ulwolves.ie/society/computer` - Get info on the Computer Society of the University of Limerick
