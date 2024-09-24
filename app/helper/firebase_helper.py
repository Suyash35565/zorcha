import requests

def verify_id_token(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}"
    payload = {"idToken": id_token}
    response = requests.post(url, json=payload)
    return response.json()
