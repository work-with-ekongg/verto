from flask import Flask, render_template, url_for, request, redirect, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "127.0.0.1"

# =========================
# Upload Folder Setup
# =========================

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# Database Initialization
# =========================

def init_db():
    conn = sqlite3.connect("verto.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS USERS(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password TEXT,
            skill TEXT,
            bio TEXT
        )
    """)

    # Add role column if missing
    try:
        cursor.execute("ALTER TABLE USERS ADD COLUMN role TEXT")
    except sqlite3.OperationalError:
        pass

    # Add profile picture column if missing
    try:
        cursor.execute("ALTER TABLE USERS ADD COLUMN profile_pic TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


init_db()


# =========================
# Routes
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# Signup
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        conn = sqlite3.connect("verto.db")
        cursor = conn.cursor()

        # Handle file upload
        file = request.files.get("profile_pic")
        filename = None

        if file and file.filename != "":
            filename = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        cursor.execute("""
            INSERT INTO USERS
            (username, email, password, skill, bio, role, profile_pic)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["username"],
            request.form["email"],
            request.form["password"],
            request.form["skill"],
            request.form["bio"],
            request.form["role"],
            filename
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html")


# =========================
# Login
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        conn = sqlite3.connect("verto.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM USERS
            WHERE email = ? AND password = ?
        """, (
            request.form["email"],
            request.form["password"]
        ))

        user = cursor.fetchone()
        conn.close()

        if user:

            session["user_id"] = user[0]
            session["username"] = user[1]
            session["skill"] = user[4]
            session["bio"] = user[5]
            session["role"] = user[6]
            session["profile_pic"] = user[7]

            return redirect(url_for("dashboard"))

        return "Invalid credentials", 401

    return render_template("login.html")


# =========================
# Dashboard
# =========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        user=session.get("username"),
        role=session.get("role"),
        skill=session.get("skill"),
        bio=session.get("bio"),
        profile_pic=session.get("profile_pic")
    )


# =========================
# Logout
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================
# Run App
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)