# clubsandsocs-api

## Description

Allows you to get information about societies and clubs from university websites using the [Assure Memberships Platform](https://assurememberships.com) for use in other applications.

## Supported Sites

- [DCU Clubs & Societies](https://dcuclubsandsocs.ie)
  - Site Code: `dcuclubsandsocs.ie`
- [MU Clubs & Societies](https://mulife.ie/)
  - Site Code: `mulife.ie`
  

## Installation

1. Clone the repository
2. Run `pip install -r requirements.txt` to install the required packages
3. Run `flask run` to start the server

## Usage

The API has the following endpoints:

- `/<site>/<society>/events` - Get all upcoming events for a society/club
- `/<site>/<society>/committee` - Get the committee information for a society/club
- `/<site>/<society>/gallery` - Get the gallery photos for a society/club

## Example

- `/dcuclubsandsocs.ie/redbrick/events` - Get all upcoming events for Redbrick Society in DCU
- `/mulife.ie/esn/committee` - Get the committee information for the Erasmus Student Network Society in Maynooth University
- `/dcuclubsandsocs.ie/media-production/gallery` - Get the gallery photos for the Media Production Society in DCU