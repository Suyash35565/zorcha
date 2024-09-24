from firebase_admin import auth, credentials, initialize_app
import os
from app import create_app
from app.setup_logging import setup_logging

if __name__ == "__main__":
    app = create_app()
    setup_logging()
    cert_path = os.path.join(os.path.dirname(__file__), 'cert1.pem')
    key_path = os.path.join(os.path.dirname(__file__), 'key1.pem')

    if os.path.exists(cert_path) and os.path.exists(key_path):
        app.run(debug=True, ssl_context=(cert_path, key_path))
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)