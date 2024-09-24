import uuid
from pymongo import MongoClient
from datetime import datetime
import json
import logging
from bson import ObjectId

class MongoClientDB:
    def __init__(self, host='localhost', port=27017, db_name='zorcha_db'):
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        logging.getLogger("pymongo").setLevel(logging.CRITICAL)
        logging.getLogger("pymongo.connection").setLevel(logging.CRITICAL)

    def save_token(self, user_id, token):
        """Saves or updates the firebase token for a user."""
        self.db.users.update_one(
            {'user_id': user_id},
            {'$set': {'firebase_token': token}},
            upsert=True
        )

    # ======= USER COLLECTIONS ============

    def save_new_user(self, user):
        # Insert the new user into the 'users' collection
        result = self.db.users.insert_one(user)
        # Return the inserted user ID
        return str(result.inserted_id)

    def get_user_by_token(self, token):
        """Finds a user based on their firebase token."""
        return self.db.users.find_one({'firebase_token': token})

    def get_user_by_id(self, user_id):
        """Finds a user based on their firebase token."""
        return self.db.users.find_one({'user_id': user_id})

    def save_instagram_token(self, user_id, instagram_token):
        """Saves the Instagram token for a user."""
        self.db.users.update_one(
            {'user_id': user_id},
            {'$set': {'instagram_token': instagram_token}},
            upsert=True
        )

    def check_instagram_connected(self, user_id):
        """Checks if a user has an Instagram token."""
        user = self.db.users.find_one({'user_id': user_id})
        return bool(user.get('instagram_token')) if user else False

    def save_onboarding_list(self, user_id, onboarding_list):
        """Saves the onboarding preferences for a user."""
        self.db.users.update_one(
            {'user_id': user_id},
            {'$set': {'onboarding_list': onboarding_list}},
            upsert=True
        )

    def get_onboarding_list(self, user_id):
        """Gets the onboarding preferences for a user."""
        user = self.db.users.find_one({'user_id': user_id})
        return user.get('onboarding_list') if user else []

    def add_random_dump(self, msg):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.db.webhook_dump.insert_one({
            'timestamp': timestamp,
            'message': msg
        })

    def get_automations(self, fb_id):
        pipeline = [
            {'$match': {'fb_id': fb_id}},
            {'$addFields': {'_id': {'$toString': '$_id'}}}
        ]
        # Return the result of the aggregation pipeline
        return self.db.user_automations.aggregate(pipeline)

    def find_automation(self, fb_id, postId):
        tp = self.get_automations(fb_id)
        if tp is None:
            return None

        for existing_post in tp:
            if existing_post['postId'] == postId:
                return existing_post
        return None

    def remove_automation(self, fb_id, postId):
        tp = self.get_automations(fb_id)
        if tp is None:
            return None

        updated_tp = [post for post in tp if post['postId'] != postId]

        if len(updated_tp) != len(tp):
            self.db.user_automations.update_one(
                {'fb_id': fb_id},
                {'$set': {'posts': updated_tp}}
            )
            return updated_tp

        return None
    
    def find_automation_by_id(self, automationId):
        automation = self.db.user_automations.find_one({
            '_id': ObjectId(automationId),
        })
        return automation
    
    def change_status_automation(self, automationId, status):
        automationId = ObjectId(automationId) if isinstance(automationId, str) else automationId
        mongo_client.db.user_automations.update_one(
            {'_id': automationId},
            {'$set': {'status': status}}
        )

    def add_tracked_posts(self, fb_id, post):
        # Check if any other post for the same fbUserId and postId exists with status "ACTIVE"
        existing_post = self.db.user_automations.find_one({
            'fb_id': fb_id,
            'postId': post['postId'],
            'status': "ACTIVE"
        })

        if existing_post:
            print("An active automation exists for this post. Skipping...")
            return None  # Exit if an active post already exists for this fbUserId and postId

        # If no active post exists, insert the post as a new document
        self.db.user_automations.insert_one({
            'fb_id': fb_id,
            **post  # Insert the post as a separate record
        })
        print("Post added successfully!")

    def get_user_messages(self, fb_id):
        ret = self.db.user_messages.find_one({'fb_id': fb_id})
        return ret['comments'] if ret else []

    def add_user_messages(self, fb_id, comment):
        self.db.user_messages.insert_one({
            'fb_id': fb_id,
            **comment  # Insert the post as a separate record
        })

    def fetch_config(self):
        config = self.db.zorcha_config.find_one()
        if config is None:
            default_config = {
                "recurringMinutes": 3,
                "recurringEnabled": False
            }
            self.db.zorcha_config.insert_one(default_config)
            return default_config
        else:
            return config

    def get_recurring_posts(self, fb_id):
        ret = self.db.user_recurring_posts.find_one({'fb_id': fb_id})
        return ret['posts'] if ret else []

    def add_recurring_post(self, fb_id, post):
        arr = self.get_recurring_posts(fb_id)
        post_id_exists = False

        for existing_post in arr:
            if existing_post['postId'] == post['postId']:
                existing_post.update(post)
                post_id_exists = True
                break

        if not post_id_exists:
            arr.append(post)

        self.db.user_recurring_posts.update_one(
            {'fb_id': fb_id},
            {'$set': {'posts': arr}},
            upsert=True
        )

    # ======= WORKSPACE COLLECTIONS ============

    def add_workspace(self, workspace):
        result = self.db.workspaces.insert_one(workspace)
        return result.inserted_id

    def get_user_workspaces(self, user_id):
        """Fetch workspaces for the given user ID."""
        return list(self.db.workspaces.find({'user_id': user_id}))

    def get_workspace_by_id(self, workspace_id, user_id):
        """Fetches a specific workspace by ID and ensures it belongs to the given user."""
        try:
            workspace = self.db.workspaces.find_one({
                '_id': ObjectId(workspace_id),
                'user_id': user_id  # Ensure the workspace belongs to the user
            })
        except Exception as e:
            return None
        return workspace


mongo_client = MongoClientDB()
