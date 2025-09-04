# Flask: Core web framework to create the API
from flask import Flask, request, jsonify

# Flask-CORS: Enables Cross-Origin Resource Sharing so frontend (on different port/domain) can call this backend
from flask_cors import CORS

# Flask-JWT-Extended: Adds JSON Web Token (JWT) authentication for secure access to protected routes
from flask_jwt_extended import (
    JWTManager,           # Manages JWT setup
    create_access_token,  # Creates JWT token after login
    jwt_required,         # Decorator to protect routes (only allow if token is valid)
    get_jwt_identity      # Gets user ID from the JWT token
)

# Flask-Bcrypt: Securely hashes passwords (never store plain text passwords!)
from flask_bcrypt import Bcrypt

# sqlite3: Built-in Python module to interact with SQLite database (lightweight, file-based)
import sqlite3

# os: To read environment variables (like PORT) when deploying
import os


# ======================================
# 🛠️ CREATE FLASK APP
# ======================================
# Initialize the Flask app
app = Flask(__name__)

# Enable CORS so frontend (e.g., http://localhost:5500) can make requests to this backend
CORS(app)

======================================



# ======================================
# 🏠 BASE ROUTE
# ======================================
@app.route("/")
def home():
    """
    Base route to confirm the backend is running.
    Access via: GET http://localhost:5000/
    """
    return {"message": "Welcome to Check TodoList App Backend API"}




# ======================================
# 🚀 RUN THE APP
# ======================================
if __name__ == "__main__":
    """
    Start the Flask development server.
    - debug=True: Auto-reload when code changes (good for development)
    - host="0.0.0.0": Allows external access (needed for deployment)
    - port: Uses PORT environment variable or defaults to 5000
    """
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)



