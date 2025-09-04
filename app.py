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
# 🔐 CONFIGURATION
# ======================================
# Secret keys used for signing JWTs and sessions (should be long & random in production)
app.config["SECRET_KEY"] = "supersecretkey"           # Used by Flask for session security
app.config["JWT_SECRET_KEY"] = "jwtsecretkey"         # Used by JWT to sign tokens

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Initialize JWT Manager
jwt = JWTManager(app)


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


    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row  # Allows dict-like access
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    # Check if user exists and password matches
    if user and bcrypt.check_password_hash(user["password"], password):
        # Create JWT token with user ID as identity
        token = create_access_token(identity=user["id"])
        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


# ======================================
# 📝 TASK MANAGEMENT ROUTES
# ======================================

@app.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    """
    Get all tasks for the logged-in user.
    Requires JWT token in Authorization header.
    Returns list of tasks as JSON.
    """
    # Get user ID from JWT token
    user_id = get_jwt_identity()

    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row  # So we can use row['title'] instead of row[0]
        c = conn.cursor()

        # Fetch only tasks belonging to this user
        c.execute("""
            SELECT id, title, description, category, priority, status
            FROM tasks
            WHERE user_id = ?
        """, (user_id,))
        rows = c.fetchall()
        conn.close()

        # Convert rows to list of dictionaries
        tasks = [dict(row) for row in rows]

        return jsonify(tasks), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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






