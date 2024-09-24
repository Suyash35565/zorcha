import datetime
import logging
import uuid

from flask import Blueprint, request, jsonify

from app.helper.date_str import convert_epoch_to_human_readable
from app.utils.token_helper import get_user_from_auth_token
from .mongo_client import mongo_client
import json 
import pprint
from werkzeug.exceptions import Unauthorized
# import firebase_admin

user_api_ap = Blueprint('user', __name__)

# Initialize the app with a service account, granting admin privileges

@user_api_ap.route('/me', methods=['GET'])
def login():
    """Login using Firebase token."""
    user = get_user_from_auth_token()

    print("seehere@@", user)
    # Fetch the user's workspaces from MongoDB
    workspaces = mongo_client.get_user_workspaces(user['user_id'])
    # Prepare response data
    response = {
        "id": user['user_id'],
        "email": user.get('email', ''),
        "workspaces": [
            {
                "id": str(workspace['_id']),
                "name": workspace['name'],
                "instagram": {
                    "profile_picture_url": workspace.get('profile_picture_url', '')
                }
            }
            for workspace in workspaces
        ],
        "created_at": user.get('createdAt')
    }
    return jsonify(response), 200

@user_api_ap.route('/workspaces', methods=['POST'])
def add_workspace():
    """Login using Firebase token."""
    user = get_user_from_auth_token(register_if_not_exists=True)
    data = request.get_json()
    instagram_data = data.get('instagram')

    if not instagram_data:
        return jsonify({"error": "Invalid input"}), 400

    # Prepare the workspace data
    workspace = {
        "user_id": user['user_id'],
        "name": instagram_data.get('name', ""),
        "instagram_id": instagram_data.get('instagram_id', ""),
        "token": instagram_data.get('token', ""),
        "expires_at": instagram_data.get('expires_at'),
        "profile_picture_url": instagram_data.get('profile_picture_url')
    }
    workspace_id = mongo_client.add_workspace(workspace)

    # Prepare response data
    return jsonify({"status": "Added", "workspace_id": str(workspace_id)}), 200


@user_api_ap.route('/workspaces/<id>', methods=['GET'])
def get_workspace_by_id(id):
    """Fetches a specific workspace by ID."""
    # Fetch the user from the Authorization token
    user = get_user_from_auth_token()

    if not user:
        return jsonify({"error": "Invalid or missing access token"}), 401

    # Fetch the workspace by its ID and ensure it belongs to the user
    workspace = mongo_client.get_workspace_by_id(id, user['user_id'])

    if not workspace:
        return jsonify({"error": "Workspace not found or access denied"}), 404

    # Format the response with workspace details
    response = {
        "id": str(workspace['_id']),
        "name": workspace['name'],
        "instagram": {
            "instagram_id": workspace['instagram_id'],
            "profile_picture_url": workspace.get('profile_picture_url', ''),
            "token": workspace.get('token', ''),
            "expires_at": workspace.get('expires_at', '')
        }
    }

    return jsonify(response), 200