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

## Installation

1. Clone the repository
2. Run `pip install -r requirements.txt` to install the required packages
3. Run `flask run` to start the API server

## Usage

The API has the following endpoints:

- `/<site>/<type>/<society>/events` - Get all upcoming events for a society/club
- `/<site>/<type>/<society>/committee` - Get the committee information for a society/club
- `/<site>/<type>/<society>/gallery` - Get the gallery photos for a society/club

## Example

- `/dcuclubsandsocs.ie/society/redbrick/events` - Get all upcoming events for Redbrick Society in DCU
- `/mulife.ie/society/esn/committee` - Get the committee information for the Erasmus Student Network Society in Maynooth University
- `/dcuclubsandsocs.ie/society/media-production/gallery` - Get the gallery photos for the Media Production Society in DCU
- `/mulife.ie/club/table-tennis/activities` - Get all weekly activities for the Table Tennis Club in Maynooth University