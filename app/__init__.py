import logging
from flask import Flask
from .user_api import user_api_ap
from flask_cors import CORS
from flask import jsonify
from werkzeug.exceptions import Unauthorized
# Custom handler for Unauthorized and ExpiredIdTokenError
from firebase_admin import auth

def handle_unauthorized(e):
    if isinstance(e, auth.ExpiredIdTokenError):
        response = jsonify({
            "error": "TOKEN_EXPIRED",
            "message": "Token expired. Please log in again."
        })
    else:
        response = jsonify({
            "error": "Unauthorized",
            "message": str(e.description)
        })
    response.status_code = 401
    return response

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    with app.app_context():
        app.register_blueprint(user_api_ap, url_prefix='/api/user')


    logging.debug("SEEHERE$$$")
    for rule in app.url_map.iter_rules():
        print(f'SEEHERE {rule.endpoint}: {rule.methods}, {rule.rule}')
    # Start the Kafka consumer threads
    app.register_error_handler(Unauthorized, handle_unauthorized)

    return app
