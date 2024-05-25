'''
API v1
'''
# from flask import Blueprint
from flask_restx import Api

from .home import api as ns_home
from .cat import api as ns_cat
from .card import api as ns_card

# blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(
    title='Tarjetametrobus-pma API Documentation',
    version='1.0.0',
    doc='/docs/api',
    description='tarjetametrobus.com api',
    contact='Christhoval Barba',
    contact_email='me@christhoval.dev',
    contact_url='https://s.christhoval.dev',
    prefix='/api/v1',
    # All API metadatas
)

api.add_namespace(ns_home, path='/')
api.add_namespace(ns_cat, path='/cats')
api.add_namespace(ns_card, path='/card')
