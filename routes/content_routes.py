import os
from flask import (
    Blueprint, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    session, 
    flash, 
    current_app
)
from werkzeug.utils import secure_filename

# Import all database helper functions required for content management and social interactions
from db.content_db import (
    save_user_video, 
    get_all_videos, 
    get_user_videos, 
    save_user_profile, 
    get_user_profile, 
    get_profile_stats,
    get_random_feed_videos,
    get_video_by_id,
    delete_user_video,
    get_user_by_username,
    get_user_videos_by_username,
    get_follow_counts,
    is_user_following,
    follow_toggle
)

# Initialize the Content Blueprint for modular route management
content_bp = Blueprint("content", __name__)


# =========================================================================
# 1. LANDING & HOME ROUTE
# =========================================================================
@content_bp.route("/")
def landing():
    """
    Renders the public landing page (welcome screen) for visitors.
    Passes `is_landing=True` so templates can render custom landing styles if needed.
    """
    return render_template("index.html", is_landing=True)


# =========================================================================
# 2. MEDIA UPLOAD ROUTE
# =========================================================================
@content_bp.route("/upload", methods=["GET", "POST"])
def upload():
    """
    Handles media (video/audio/shorts) and thumbnail uploads by authenticated users.
    """
    # Guard clause: Ensure only logged-in users can upload
    if "username" not in session:
        flash("Please log in to upload content.", "error")
        return redirect(url_for("auth.login"))
        
    if request.method == "POST":
        # Extract metadata submitted from the upload HTML form
        title = request.form.get("title")
        description = request.form.get("description")
        visibility = request.form.get("visibility", "public")
        category = request.form.get("category", "General")
        
        # Retrieve uploaded file objects from the form request
        file = request.files.get("media_file")
        thumbnail_file = request.files.get("thumbnail")
        
        # Validation: Ensure a primary media file was actually uploaded
        if not file or file.filename == "":
            flash("No media file selected.", "error")
            return redirect(request.url)
            
        if file:
            # Sanitize filenames to prevent path traversal security vulnerabilities
            filename = secure_filename(file.filename)
            thumbnail_name = secure_filename(thumbnail_file.filename) if thumbnail_file else None
            
            # 1. Save Primary Media File to static/uploads/media/
            upload_folder = os.path.join(current_app.root_path, "static", "uploads", "media")
            os.makedirs(upload_folder, exist_ok=True)  # Create directory if it doesn't exist
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # 2. Save Optional Thumbnail File to static/uploads/thumbnails/
            if thumbnail_file and thumbnail_name:
                thumb_folder = os.path.join(current_app.root_path, "static", "uploads", "thumbnails")
                os.makedirs(thumb_folder, exist_ok=True)
                thumbnail_file.save(os.path.join(thumb_folder, thumbnail_name))
            else:
                thumbnail_name = None
                
            # 3. Save Metadata & File References into MySQL Database
            success = save_user_video(
                username=session["username"],
                title=title,
                description=description,
                visibility=visibility,
                media_file=filename,
                thumbnail=thumbnail_name,
                category=category
            )
            
            if success:
                flash("Video uploaded successfully!", "success")
                return redirect(url_for("content.feed"))
            else:
                flash("Database error while saving video.", "error")
                
    return render_template("upload.html")


# =========================================================================
# 3. MEDIA PLAYER & DELETE ROUTES
# =========================================================================
@content_bp.route("/player/<int:video_id>")
def play_video(video_id):
    """
    Renders the dedicated media player page for a selected content ID.
    Also fetches a list of videos to display on the side recommended sidebar.
    """
    video = get_video_by_id(video_id)
    all_videos = get_all_videos()
    return render_template("media_player.html", current_video=video, videos=all_videos)


@content_bp.route("/video/delete/<int:video_id>", methods=["POST"])
def delete_video(video_id):
    """
    Deletes a user's upload from the database and feed.
    Restricted to logged-in users who own the content.
    """
    if "username" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))

    success = delete_user_video(video_id, session["username"])
    if success:
        flash("Video deleted successfully.", "success")
    else:
        flash("Unable to delete video or unauthorized.", "error")

    return redirect(url_for("content.feed"))


# =========================================================================
# 4. COMMUNITY DISCOVERY FEED ROUTE
# =========================================================================
@content_bp.route("/feed")
def feed():
    """
    Renders the community discover feed showcasing randomized public content.
    Passes current user info to maintain navbar session awareness.
    """
    current_username = session.get("username")
    
    # Fetch random public videos from other creators
    videos = get_random_feed_videos(current_username)
    
    # Fetch logged-in user profile details for navigation rendering
    user = get_user_by_username(current_username) if current_username else None
    
    return render_template("feeds.html", videos=videos, user=user)


# =========================================================================
# 5. USER PROFILE ROUTE (SELF & OTHER CREATORS)
# =========================================================================
@content_bp.route("/profile")
def my_profile():
    """Redirects logged-in user to their specific /profile/<username> URL."""
    current_username = session.get("username")
    if not current_username:
        flash("Please log in to view your profile.", "error")
        return redirect(url_for("auth.login"))
    
    return redirect(url_for("content.user_profile", username=current_username))

@content_bp.route("/profile/<username>")
def user_profile(username):
    """Renders the profile template for a given username."""
    current_username = session.get("username")
    
    user = get_user_by_username(username)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("content.feed"))

    is_own_profile = (current_username == username)
    is_following = is_user_following(current_username, username) if current_username else False

    followers_count, following_count = get_follow_counts(username)

    all_uploads = get_user_videos_by_username(username)
    posts_count = len(all_uploads)

    user_videos = [u for u in all_uploads if u.get("media_type", "video") == "video"]
    user_shorts = [u for u in all_uploads if u.get("media_type") == "short"]
    user_audios = [u for u in all_uploads if u.get("media_type") == "audio"]

    # Pack stats into a dictionary matching template expectations
    stats = {
        "followers_count": followers_count,
        "following_count": following_count,
        "posts_count": posts_count
    }

    return render_template(
        "profile.html",
        profile=user,
        user=user,
        stats=stats,  # <-- Pass the stats dictionary here
        is_own_profile=is_own_profile,
        is_following=is_following,
        followers_count=followers_count,
        following_count=following_count,
        posts_count=posts_count,
        user_videos=user_videos,
        user_shorts=user_shorts,
        user_audios=user_audios
    )
# =========================================================================
# 6. FOLLOW / UNFOLLOW TOGGLE ACTION
# =========================================================================
@content_bp.route("/follow/<username>", methods=["POST"])
def follow_user(username):
    """
    Handles follow/unfollow toggle actions submitted from profile action buttons.
    """
    current_username = session.get("username")
    if not current_username:
        flash("Please log in to follow users.", "error")
        return redirect(url_for("auth.login"))
    
    # Prevent users from following themselves
    if current_username != username:
        follow_toggle(current_username, username)

    # Redirect back to the target user's specific profile route
    return redirect(url_for("content.user_profile", username=username))


# =========================================================================
# 7. EDIT PROFILE ROUTE
# =========================================================================
@content_bp.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    """Temporary route for editing user profile."""
    current_username = session.get("username")
    if not current_username:
        flash("Please log in to edit your profile.", "error")
        return redirect(url_for("auth.login"))
        
    return "<h1>Edit Profile Page (Under Construction)</h1>"