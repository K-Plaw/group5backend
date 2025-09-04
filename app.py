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

@app.route("/tasks", methods=["POST"])
@jwt_required()
def add_task():
    """
    Add a new task for the logged-in user.
    Expects JSON: { "title": "...", "description": "", "category": "", "priority": "", "status": 0 }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Extract task data
    title = data.get("title")
    description = data.get("description", "")
    category = data.get("category", "Personal")
    priority = data.get("priority", "Medium")
    status = int(data.get("status", 0))

    # Validate required field
    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required and must be a non-empty string"}), 400

    # Validate category and priority
    valid_categories = ["Work", "Personal", "Study", "Shopping", "Other"]
    valid_priorities = ["Low", "Medium", "High"]

    if category not in valid_categories:
        return jsonify({"error": "Invalid category"}), 400
    if priority not in valid_priorities:
        return jsonify({"error": "Invalid priority"}), 400

    try:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO tasks (user_id, title, description, category, priority, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, title, description, category, priority, status))
        conn.commit()
        task_id = c.lastrowid  # Get the ID of the new task
        conn.close()

        return jsonify({"message": "Task added", "id": task_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    """
    Update an existing task.
    Only allows updating if the task belongs to the logged-in user.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    title = data.get("title")
    description = data.get("description", "")
    category = data.get("category", "Personal")
    priority = data.get("priority", "Medium")
    status = int(data.get("status", 0))

    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required and must be a string"}), 400

    valid_categories = ["Work", "Personal", "Study", "Shopping", "Other"]
    valid_priorities = ["Low", "Medium", "High"]

    if category not in valid_categories:
        return jsonify({"error": "Invalid category"}), 400
    if priority not in valid_priorities:
        return jsonify({"error": "Invalid priority"}), 400

    try:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("""
            UPDATE tasks
            SET title = ?, description = ?, category = ?, priority = ?, status = ?
            WHERE id = ? AND user_id = ?
        """, (title, description, category, priority, status, task_id, user_id))
        conn.commit()
        conn.close()

        # Check if any row was updated (ensures task exists and belongs to user)
        if c.rowcount == 0:
            return jsonify({"error": "Task not found or unauthorized"}), 404

        return jsonify({"message": "Task updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def delete_task(task_id):
    """
    Delete a task by ID.
    Only succeeds if the task belongs to the logged-in user.
    """
    user_id = get_jwt_identity()

    try:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        conn.commit()
        conn.close()

        if c.rowcount == 0:
            return jsonify({"error": "Task not found or unauthorized"}), 404

        return jsonify({"message": "Task deleted"}), 200

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







