from flask import Flask
from flask_restx import Api, Resource
from flask_cors import CORS
from scraper import *

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

api = Api(app, version='1.0', title='Clubs & Socs API',
          description='Allows you to get information about societies and clubs from university websites using the Assure Memberships Platform for use in other applications.')

@api.route('/<site>/<type>/<society>/events')
class EventResource(Resource):
    def get(self, site, society, type):
        """Get all events for a society"""
        return scrape_events(site, society, type)
    
@api.route('/<site>/<type>/<society>/committee')
class CommitteeResource(Resource):
    def get(self, site, society, type):
        """Get the committee information for a society"""
        return scrape_committee(site, society, type)
    
@api.route('/<site>/<type>/<society>/gallery')
class GalleryResource(Resource):
    def get(self, site, society, type):
        """Get the gallery photos for a society"""
        return scrape_gallery(site, society, type)
    
@api.route('/<site>/<type>/<society>/activities')
class ActivitiesResource(Resource):
    def get(self, site, society, type):
        """Get all weekly activities for a society"""
        return scrape_activities(site, society, type)

if __name__ == '__main__':
    app.run(debug=True)
