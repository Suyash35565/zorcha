from datetime import datetime
import requests
from flask import request
from firebase_admin import auth
from werkzeug.exceptions import Unauthorized
from app.mongo_client import mongo_client

# Helper function to verify Firebase ID token
def verify_firebase_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        print("SEEHERE", decoded_token)
        return decoded_token
    except Exception as e:
        raise e

# {
#    "name":"Watson Test",
#    "picture":"https://lh3.googleusercontent.com/a/ACg8ocI9EUIbS_xQ2ZqoiEqZA5P1IwVRvbBtQc4U0GVE1utwCqeg=s96-c",
#    "iss":"https://securetoken.google.com/zorcha-1fce5",
#    "aud":"zorcha-1fce5",
#    "auth_time":1726117587,
#    "user_id":"GtbkEE1QVDZYY8mxpINe6STUo6h1",
#    "sub":"GtbkEE1QVDZYY8mxpINe6STUo6h1",
#    "iat":1726117587,
#    "exp":1726121187,
#    "email":"watson43517@gmail.com",
#    "email_verified":true,
#    "firebase":{
#       "identities":{
#          "google.com":[
#             "103143158650215013099"
#          ],
#          "email":[
#             "watson43517@gmail.com"
#          ]
#       },
#       "sign_in_provider":"google.com"
#    },
#    "uid":"GtbkEE1QVDZYY8mxpINe6STUo6h1"
# }

def get_user_from_auth_token(register_if_not_exists=False):
    """
    Extracts the user from the Firebase access token in the Authorization header and verifies it.
    If the user doesn't exist and register_if_not_exists is True, register the user.
    """

    # Retrieve the token from the Authorization header
    auth_token = request.headers.get('Authorization')

    if not auth_token:
        raise Unauthorized("Access token is missing.")  # Return 401 Unauthorized if no token is found

    # Strip the "Bearer " prefix if it exists
    if auth_token.startswith('Bearer '):
        auth_token = auth_token.split(' ')[1]

    try:
        # Verify the Firebase ID token
        decoded_token = verify_firebase_token(auth_token)
        uid = decoded_token['uid']  # Extract the user ID from the decoded token

        # Use MongoDB client to find the user by Firebase UID
        user = mongo_client.get_user_by_id(uid)

        # If the user doesn't exist and registration is allowed
        if not user and register_if_not_exists:
            # Register the new user in the system
            user = {
                "user_id": uid,
                "email": decoded_token.get('email'),
                "name": decoded_token.get('name', ''),
                "createdAt": datetime.now(),  # Add any additional fields you need
                "onboarding_answer": "",
                "picture": decoded_token.get('picture', '')
            }
            # Insert the new user into the MongoDB collection
            mongo_client.save_new_user(user)
            return user  # Return the newly registered user

        elif not user:
            raise Unauthorized("User not found for the provided token.")  # Return 401 if user is not found

        return user  # Return the user if found

    # except auth.InvalidIdTokenError:
    #     raise Unauthorized("Invalid ID token.")  # Return 401 if the token is invalid

    # except auth.ExpiredIdTokenError:
    #     raise Unauthorized("ID token has expired.")  # Return 401 if the token is expired

    except Exception as e:
        raise Unauthorized(f"Error verifying token: {str(e)}")  # Handle any other exceptions
