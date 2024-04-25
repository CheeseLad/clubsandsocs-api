from flask import Flask
from flask_restx import Api, Resource
from scraper import *

app = Flask(__name__)
api = Api(app, version='1.0', title='Clubs & Socs API',
          description='Allows you to get information about societies and clubs from university websites using the Assure Memberships Platform for use in other applications.')

@api.route('/<site>/<society>/events')
class EventResource(Resource):
    def get(self, site, society):
        """Get all events for a society"""
        return scrape_events(site, society)
    
@api.route('/<site>/<society>/committee')
class CommitteeResource(Resource):
    def get(self, site, society):
        """Get the committee information for a society"""
        return scrape_committee(site, society)
    
@api.route('/<site>/<society>/gallery')
class GalleryResource(Resource):
    def get(self, site, society):
        """Get the gallery photos for a society"""
        return scrape_gallery(site, society)

if __name__ == '__main__':
    app.run(debug=True)
