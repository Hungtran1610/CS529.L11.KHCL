from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

from system.logger import make_logger
from system.exceptions import register_error_handlers
from system.model_encoder import AlchemyEncoder
from system.model_base import Session

load_dotenv(find_dotenv(), override=True)  # Load env before run powerpaint

SWAGGER_CONFIG = {
    "swagger": "2.0",
    "info": {
        "title": "RockSearch API",
        "description": "Description: API For Project CS529.L11.KHCL \n Developed By: 陳金興 \n Docs written by: 陳金興 \n Person taking all the abusive and boclotsuclaodong: 陳金興 \n save 陳金興 from boclotsuclaodong \n 我太累了 \n 睏得睜不開眼來",
        "contact": {
            "name": "Rockship",
            "email": "hung.tran@rockship.co",
            "url": "http://rockship.co/#",
        },
        "license": {
            "name": "Apache 2.0",
            "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
        },
        "termsOfService": "http://rockship.co/#",
        "version": "1.0.0",
    },
    "consumes": [
        "application/json",
        "text/plain"
    ],
    "produces": [
        "application/json"
    ],
    "basePath": "/",
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "JWT": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    },
}

def create_app():
    app = Flask(__name__)

    from blueprint.health_check import bp as health_check_router

    app.register_blueprint(health_check_router)

    CORS(app, expose_headers=["X-Total-Count"])
    Swagger(app, template=SWAGGER_CONFIG)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.json_encoder = AlchemyEncoder
    register_error_handlers(app)
    app.sess = Session()
    make_logger(app)

    from model.db import db
    db.init_app(app)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

