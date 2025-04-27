from flask import Flask, jsonify, redirect, request
import requests
from urllib.parse import urlencode
import psycopg2
 
app = Flask(__name__)
 
# Auth0 Config
AUTH0_DOMAIN = "dev-30zef58g61y2pcd5.us.auth0.com"
CLIENT_ID = "OS4rYWsXkn41htGV1nmPAL4avOdvwZKp"
CLIENT_SECRET = "ZFOacInsgqWta60RcK6xz6YQsJMUjW3wW4duiEeUpDPi_CUrY-d1Vk7kNEKO7mkL"
REDIRECT_URI = "http://localhost:8000"
AUDIENCE = "https://dev-30zef58g61y2pcd5.us.auth0.com/api/v2/"
SCOPES = ["openid", "profile", "email", "offline_access"]

def connect_db():
        try:
            conn = psycopg2.connect(
                dbname="design_time",
                user="postgres",
                password="postgres",
                host='10.26.1.52',
                port="5432"
            )
            print("? Database connection successful.")
            return conn
        except psycopg2.Error as e:
            print("? Database connection failed!")
            print("Error:", e)
            return None
connect_db()
def generate_authorization_url():
    base_url = f"https://{AUTH0_DOMAIN}/authorize"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "audience": AUDIENCE,
        "prompt": "login"
    }
    return f"{base_url}?{urlencode(params)}"
 
 
@app.route('/generate-login-url', methods=['GET'])
def generate_login_url():
    try:
        authorization_url = generate_authorization_url()
        return jsonify({
            "statusCode": 200,
            "message": "Login URL Generated Successfully",
            "result": authorization_url
        })
    except Exception as e:
        app.logger.error(f"Error generating login URL: {e}")
        return jsonify({"statusCode": 500, "message": "Error generating login URL"}), 500
 
 
@app.route('/', methods=['GET'])
def callback():
    try:
        # Step 1: Get the code from query params
        code = request.args.get('code')
        if not code:
            return jsonify({"statusCode": 400, "message": "Missing authorization code"}), 400

        # Step 2: Exchange code for tokens
        token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI
        }

        token_response = requests.post(token_url, headers=headers, data=data)
        token_response.raise_for_status()
        token_data = token_response.json()

        # Step 3: Use access token to fetch user info
        access_token = token_data.get("access_token")
        if not access_token:
            return jsonify({"statusCode": 401, "message": "Access token not found"}), 401

        userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"
        userinfo_headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = requests.get(userinfo_url, headers=userinfo_headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()
        print("user_info", user_info)
        return jsonify({
            "statusCode": 200,
            "message": "Token and user info fetched successfully",
            "token_data": token_data,
            "user_info": user_info
        })

    except Exception as e:
        app.logger.error(f"Callback failed: {e}")
        return jsonify({"statusCode": 500, "message": "Error during callback"}), 500


 
if __name__ == '__main__':
    app.run(debug=True, port=8000)
 