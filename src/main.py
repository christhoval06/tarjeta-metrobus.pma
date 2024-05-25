# -*- coding: utf-8 -*-
'''
API for Tarjeta Metrobus Panama
'''
import os
from flask import Flask

from .apis import api

app = Flask(__name__)
api.init_app(app)


def main():
    '''
    Run the API
    '''
    app.run(port=int(os.environ.get('PORT', 80)), debug=True)


if __name__ == "__main__":
    main()
