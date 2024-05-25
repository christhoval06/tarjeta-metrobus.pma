# -*- coding: utf-8 -*-
'''
Home Namespace
'''

from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from flask_restx import Namespace, Resource, fields

import marshmallow_dataclass

api = Namespace('home', description='', path='')

info = api.model('Info', {
    'name': fields.String,
    'version': fields.String,
    'description': fields.String,
    'author': fields.String,
    'license': fields.String,
})


@dataclass
class Info(DataClassJsonMixin):
    '''API class for imformation'''
    name: str
    version: str
    description: str
    author: str
    license: str


InfoSchema = marshmallow_dataclass.class_schema(Info)


@api.route('/')
class Home(Resource):
    '''Home'''
    @api.doc('information')
    @api.marshal_with(info)
    def get(self):
        '''Get API information'''
        return {
            "name": "tarjetametrobus-pma",
            "version": "1.0.0",
            "description": "tarjetametrobus.com api",
            "author": "Christhoval Barba<me@christhoval.dev>",
            "license": "MIT"
        }
