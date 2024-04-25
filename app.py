from flask import Flask
from flask_restx import Api, Resource
from scraper import *

app = Flask(__name__)
api = Api(app, version='1.0', title='Clubs & Socs API',
          description='Allows easy retrieval of event and committee information.')

@api.route('/<site>/<society>/events')
class EventResource(Resource):
    def get(self, site, society):
        """Get events for a specific society"""
        return scrape_events(site, society)
    
@api.route('/<site>/<society>/committee')
class CommitteeResource(Resource):
    def get(self, site, society):
        """Get the committee information for a specific society"""
        return scrape_committee(site, society)
    
@api.route('/<site>/<society>/gallery')
class GalleryResource(Resource):
    def get(self, site, society):
        """Get the photons in the gallery for a specific society"""
        return scrape_gallery(site, society)

if __name__ == '__main__':
    app.run(debug=True)
