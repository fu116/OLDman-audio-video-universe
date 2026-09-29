import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import (
    get_db_connection, create_user, get_user_by_username, save_user_interests,
    save_user_profile, get_user_profile, get_profile_stats, get_user_videos, save_user_video
)

app = Flask(__name__)

# Secret key now comes from an environment variable instead of being hardcoded.
# Set this before running, e.g.: export SECRET_KEY="some-long-random-string"
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-fallback-key-do-not-use-in-prod")


@app.route("/", methods=["GET"])
def home():
    connection = get_db_connection()

    if connection:
        connection.close()  # Always close the connection when done to save server resources
        status_message = "OLDMAN Server is running and MySQL Connected Successfully!"
    else:
        status_message = "OLDMAN Server is running, but MySQL Connection Failed!"

    kwargs = {
        "db_status": status_message
    }
    return render_template("index.html", **kwargs)

@app.route("/media_player", methods=["GET"])
def media_player_page():
    return render_template("media_player.html")














# Route to show the registration page
@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_user():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    # Securely hash the password
    hash_password = generate_password_hash(password)

    # Call the database function we created in database.py
    result = create_user(username, email, hash_password)
    print("DATABASE RESULT:", result)
    if result is True:
        flash("Account created successfully! You can now log in")
        return redirect(url_for("login"))
    else:
        flash(result)  # Flash the error message returned from database.py
        return redirect(url_for("register_page"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = get_user_by_username(username)
        print("DEBUG - Searched Username:", username)
        print("DEBUG - Database User Result:", user)

        if user and check_password_hash(user["password_hash"], password):
            session["username"] = user["username"]
            flash("Login successful! Welcome Back.", "success")

            # If they've already picked interests before, skip straight to the dashboard.
            connection = get_db_connection()
            has_interests = False
            if connection:
                try:
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(
                        "SELECT 1 FROM user_interests WHERE username = %s LIMIT 1",
                        (username,)
                    )
                    has_interests = cursor.fetchone() is not None
                except Exception as e:
                    print("Error checking existing interests:", e)
                finally:
                    if connection.is_connected():
                        cursor.close()
                        connection.close()

            if has_interests:
                return redirect(url_for("dashboard"))
            return redirect(url_for("interests"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You've been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/interests", methods=["GET", "POST"])
def interests():
    if "username" not in session:
        flash("please log in first .", "error")
        return redirect(url_for("login"))

    available_interests = [
        "Action movies",
        "sci-FI",
        "Podcast",
        "Lo-Fi beats",
        "Tech and Coding",
        "Documentaries",
        "Gaming Streams",
        "Acoustic Music",
        "History",
        "Sport"
    ]

    if request.method == "POST":
        selected_interests = request.form.getlist("interests")
        print("DEBUG: Raw form data received:", request.form)
        print("DEBUG: Selected interests list:", selected_interests)
        if not selected_interests:
            print("DEBUG: Selection list was empty!")
            flash("Please select at least one interest.", "error")
            return redirect(url_for("interests"))

        success = save_user_interests(session["username"], selected_interests)
        print("DEBUG: Save success status:", success)

        if success:
            flash("Interests saved successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Error saving  interests. Try again", "error")
            return redirect(url_for("interests"))

    return render_template("interests.html", interests=available_interests)


# --- 1. CREATOR DASHBOARD / STUDIO ROUTE ---
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    username = session["username"]

    # Handle content/video uploads from the dashboard studio
    if request.method == "POST":
        title = request.form.get("title")
        video_url = request.form.get("video_url")
        category = request.form.get("category", "Videos")

        if title and video_url:
            success = save_user_video(username, title, video_url, category)
            if success:
                flash("Content uploaded successfully!", "success")
            else:
                flash("Failed to upload content.", "error")
        return redirect(url_for("dashboard"))

    # Fetch user's saved interests
    connection = get_db_connection()
    user_interests = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT interest FROM user_interests WHERE username = %s", (username,))
            result = cursor.fetchall()
            user_interests = [row["interest"] for row in result]
        except Exception as e:
            print("Error fetching interests:", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    # Fetch profile details, dynamic stats, and uploaded videos
    profile = get_user_profile(username)
    stats = get_profile_stats(username)
    videos = get_user_videos(username)

    return render_template(
        "dashboard.html",
        username=username,
        interests=user_interests,
        profile=profile,
        stats=stats,
        videos=videos
    )


# --- 2. PUBLIC PROFILE ROUTE ---
@app.route("/profile/<username>")
def profile(username):
    user_profile = get_user_profile(username)

    if not user_profile:
        # Fallback default if profile isn't filled out yet
        user_profile = {
            "username": username,
            "full_name": username,
            "bio": "No bio added yet.",
            "profile_pic": "default_avatar.svg",
            "cover_pic": "default_cover.jpg",
            "is_verified": False,
            "monetization_enabled": False
        }

    stats = get_profile_stats(username)
    videos = get_user_videos(username)

    # Check if this profile belongs to the currently logged-in user
    is_own_profile = ("username" in session and session["username"] == username)

    return render_template(
        "profile.html",
        profile=user_profile,
        stats=stats,
        videos=videos,
        is_own_profile=is_own_profile
    )


# --- 3. EDIT PROFILE ROUTE ---
@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if "username" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    username = session["username"]

    if request.method == "POST":
        full_name = request.form.get("full_name")
        bio = request.form.get("bio")

        success = save_user_profile(username, full_name, bio)
        if success:
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile", username=username))
        else:
            flash("Failed to update profile.", "error")

    current_profile = get_user_profile(username)
    return render_template("edit_profile.html", profile=current_profile)


# --- 4. JSON API ENDPOINT FOR YOUR FRIEND'S REACT APP ---
@app.route("/api/profile/<username>", methods=["GET"])
def api_get_profile(username):
    user_profile = get_user_profile(username)
    if not user_profile:
        return jsonify({"status": "error", "message": "Profile not found"}), 404

    stats = get_profile_stats(username)
    videos = get_user_videos(username)

    return jsonify({
        "status": "success",
        "profile": user_profile,
        "stats": stats,
        "videos": videos
    })

if __name__ == '__main__':
    app.run(debug=True)