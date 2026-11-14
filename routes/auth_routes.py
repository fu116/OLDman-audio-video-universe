from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db.auth_db import create_user, get_user_by_username, save_user_interests

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("auth.register"))
            
        password_hash = generate_password_hash(password)
        result = create_user(username, email, password_hash)
        
        if result is True:
            session["username"] = username
            flash("Registration successful! Please select your interests.", "success")
            return redirect(url_for("auth.interests"))
        else:
            flash(result, "error")
            
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session["username"] = user["username"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("content.feed"))
        else:
            flash("Invalid username or password.", "error")
            
    return render_template("login.html")

@auth_bp.route("/interests", methods=["GET", "POST"])
def interests():
    if "username" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
        
    if request.method == "POST":
        selected_interests = request.form.getlist("interests")
        if selected_interests:
            save_user_interests(session["username"], selected_interests)
            flash("Interests saved successfully!", "success")
            return redirect(url_for("content.feed"))
        else:
            flash("Please select at least one interest.", "error")
            
    # Sample categories to display in the template loop
    available_interests = ["Music & Audio", "Tech & Coding", "Podcasts", "Gaming", "Vlogs & Life", "Art & Design"]
    return render_template("interests.html", interests=available_interests)

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))