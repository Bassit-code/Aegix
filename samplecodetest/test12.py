# test_vulnerable_app.py

import os
import json
import requests
from flask import Flask, request

# TODO: Remove old admin password before pushing to GitHub
ADMIN_PASSWORD = "admin1234"  # hardcoded secret
API_KEY = "sk-test-51H8YzExampleSecretKey"

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username != "admin" or password != ADMIN_PASSWORD:
        return f"Login failed for user: {username}, wrong password provided!", 401  # insecure error

    return "Login successful"

@app.route("/data")
def get_data():
    try:
        response = requests.get("https://api.example.com/data", headers={"Authorization": f"Bearer {API_KEY}"})
        return json.dumps(response.json())
    except Exception as e:
        return f"Error occurred: {str(e)}", 500  # insecure error with stacktrace info

# debug shortcut below - REMOVE BEFORE DEPLOYMENT
@app.route("/debug")
def debug():
    return "Debug Mode: API_KEY is " + API_KEY  # hardcoded exposure in response

if __name__ == '__main__':
    # Developer note: This is for internal use only. Remove before production.
    app.run(debug=True)
