from flask import Flask
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from scraper import *

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

api = Api(
    app,
    version='1.0',
    title='Clubs & Societies API',
    description='API to fetch information about societies and clubs from university websites using the Assure Memberships Platform.',
)

resource_params = api.parser()
resource_params.add_argument('site', type=str, required=True, help='University clubs & societies website domain (Example: "dcuclubsandsocs.ie")')
resource_params.add_argument('type', type=str, required=True, help='Type of group (Example: "club" or "society")')
resource_params.add_argument('society', type=str, required=True, help='Name of the society or club (Example: "redbrick")')


@api.route('/<string:site>/<string:type>/<string:society>/events')
@api.doc(params={
    'site': 'University clubs & societies website domain (Example: "dcuclubsandsocs.ie")',
    'type': 'Type of group (Example: "club" or "society")',
    'society': 'Name of the society or club (Example: "redbrick")'
})
class EventResource(Resource):
    @api.doc(description='Retrieve all events for a specified society or club.')
    @api.response(200, 'Success')
    @api.response(404, 'Could not load events')
    def get(self, site, type, society):
        """Get all events for a club or society"""
        return scrape_events(site, society, type)


@api.route('/<string:site>/<string:type>/<string:society>/committee')
@api.doc(params={
    'site': 'University clubs & societies website domain (Example: "dcuclubsandsocs.ie")',
    'type': 'Type of group (Example: "club" or "society")',
    'society': 'Name of the society or club (Example: "redbrick")'
})
class CommitteeResource(Resource):
    @api.doc(description='Retrieve committee information for a specified society or club.')
    @api.response(200, 'Success')
    @api.response(404, 'Could not load committee information')
    def get(self, site, type, society):
        """Get the committee information for a club or society"""
        return scrape_committee(site, society, type)


@api.route('/<string:site>/<string:type>/<string:society>/gallery')
@api.doc(params={
    'site': 'University clubs & societies website domain (Example: "dcuclubsandsocs.ie")',
    'type': 'Type of group (Example: "club" or "society")',
    'society': 'Name of the society or club (Example: "redbrick")'
})
class GalleryResource(Resource):
    @api.doc(description='Retrieve gallery photos for a specified society or club.')
    @api.response(200, 'Success')
    @api.response(404, 'Could not load gallery photos')
    def get(self, site, type, society):
        """Get the gallery photos for a club or society"""
        return scrape_gallery(site, society, type)


@api.route('/<string:site>/<string:type>/<string:society>/activities')
@api.doc(params={
    'site': 'University clubs & societies website domain (Example: "dcuclubsandsocs.ie")',
    'type': 'Type of group (Example: "club" or "society")',
    'society': 'Name of the society or club (Example: "redbrick")'
})
class ActivitiesResource(Resource):
    @api.doc(description='Retrieve all weekly activities for a specified society or club.')
    @api.response(200, 'Success')
    @api.response(404, 'Could not load weekly activities')
    def get(self, site, type, society):
        """Get all weekly activities for a club or society"""
        return scrape_activities(site, society, type)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
