from db import get_db_connection
def save_user_video(username, title, description, visibility, media_file, thumbnail, category):
    """Saves uploaded video metadata to the database."""
    connection = get_db_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO user_videos 
            (username, title, description, visibility, video_url, thumbnail_url, category) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (username, title, description, visibility, media_file, thumbnail, category))
        connection.commit()
        return True
    except Exception as e:
        print("DATABASE ERROR saving video:", e)
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_all_videos(limit=20):
    """Fetches a list of recent videos for the main feed."""
    connection = get_db_connection()
    videos = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username, title, description, video_url, thumbnail_url, category, views_count, created_at 
                FROM user_videos 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            videos = cursor.fetchall()
        except Exception as e:
            print("Error fetching feed videos:", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return videos

def get_user_videos(username):
    """Fetches all videos uploaded by a specific user."""
    connection = get_db_connection()
    videos = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, title, video_url, thumbnail_url, category, views_count, created_at 
                FROM user_videos 
                WHERE username = %s 
                ORDER BY created_at DESC
            """, (username,))
            videos = cursor.fetchall()
        except Exception as e:
            print("Error fetching user videos:", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return videos

def save_user_profile(username, full_name, bio, profile_pic=None):
    """Saves or updates a user's profile details."""
    connection = get_db_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        if profile_pic:
            query = """
                INSERT INTO user_profiles (username, full_name, bio, profile_pic) 
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE full_name = %s, bio = %s, profile_pic = %s
            """
            cursor.execute(query, (username, full_name, bio, profile_pic, full_name, bio, profile_pic))
        else:
            query = """
                INSERT INTO user_profiles (username, full_name, bio) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE full_name = %s, bio = %s
            """
            cursor.execute(query, (username, full_name, bio, full_name, bio))
            
        connection.commit()
        return True
    except Exception as e:
        print("Error saving profile:", e)
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_profile(username):
    """Fetches user profile details by username."""
    connection = get_db_connection()
    if not connection:
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT username, full_name, bio, profile_pic, cover_pic, is_verified, monetization_enabled, social_github, social_twitter 
            FROM user_profiles 
            WHERE username = %s
        """, (username,))
        return cursor.fetchone()
    except Exception as e:
        print("Error fetching profile:", e)
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_profile_stats(username):
    """Fetches follower, following, and post count stats for a user."""
    connection = get_db_connection()
    stats = {"followers_count": 0, "following_count": 0, "content_count": 0}
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT COUNT(*) as count FROM user_follows WHERE following_username = %s", (username,))
            res = cursor.fetchone()
            if res: stats["followers_count"] = res["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM user_follows WHERE follower_username = %s", (username,))
            res = cursor.fetchone()
            if res: stats["following_count"] = res["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM user_videos WHERE username = %s", (username,))
            res = cursor.fetchone()
            if res: stats["content_count"] = res["count"]
            
        except Exception as e:
            print("Error fetching profile stats:", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return stats


def get_video_by_id(video_id):
    """Fetches a specific video record by ID."""
    connection = get_db_connection()
    if not connection:
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_videos WHERE id = %s", (video_id,))
        return cursor.fetchone()
    except Exception as e:
        print("Error fetching video:", e)
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_user_video(video_id, username):
    """Deletes a video owned by the specified user."""
    connection = get_db_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM user_videos WHERE id = %s AND username = %s", (video_id, username))
        connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("Error deleting video:", e)
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_random_feed_videos(current_username=None, limit=50):
    """Fetches random public videos for the discovery feed."""
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor(dictionary=True)
        # If you want to see your own uploads too during testing, remove the username exclusion:
        query = """
            SELECT * FROM user_videos 
            WHERE visibility = 'public'
            ORDER BY RAND() 
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching random feed videos:", e)
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



def create_follows_table():
    """Ensures the user follows table exists."""
    connection = get_db_connection()
    if not connection:
        return
    try:
        cursor = connection.cursor()
        query = """
            CREATE TABLE IF NOT EXISTS user_follows (
                id INT AUTO_INCREMENT PRIMARY KEY,
                follower_username VARCHAR(255) NOT NULL,
                followed_username VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_follow (follower_username, followed_username)
            )
        """
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        print("Error creating follows table:", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def follow_toggle(follower, target_user):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            if is_user_following(follower, target_user):
                # Unfollow
                query = "DELETE FROM user_follows WHERE follower_username = %s AND following_username = %s"
            else:
                # Follow
                query = "INSERT INTO user_follows (follower_username, following_username) VALUES (%s, %s)"
            
            cursor.execute(query, (follower, target_user))
            connection.commit()
            return True
        except Exception as e:
            print("Error toggling follow status:", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False

def get_follow_counts(username):
    connection = get_db_connection()
    followers_count = 0
    following_count = 0
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Followers = people who follow 'username' (where following_username = username)
            query_followers = "SELECT COUNT(*) as count FROM user_follows WHERE following_username = %s"
            cursor.execute(query_followers, (username,))
            res1 = cursor.fetchone()
            if res1:
                followers_count = res1["count"]
                
            # Following = people 'username' follows (where follower_username = username)
            query_following = "SELECT COUNT(*) as count FROM user_follows WHERE follower_username = %s"
            cursor.execute(query_following, (username,))
            res2 = cursor.fetchone()
            if res2:
                following_count = res2["count"]
                
        except Exception as e:
            print("Error getting follow counts:", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return followers_count, following_count

def is_user_following(follower, target_user):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            # CHANGED: followed_username -> following_username
            query = """
                SELECT 1 FROM user_follows 
                WHERE follower_username = %s AND following_username = %s
            """
            cursor.execute(query, (follower, target_user))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print("Error checking follow status:", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False

def get_user_by_username(username):
    """Fetches user account details by username."""
    connection = get_db_connection()
    if not connection:
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()
    except Exception as e:
        print("Error fetching user by username:", e)
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_videos_by_username(username):
    """Fetches all media uploads associated with a specific username."""
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_videos WHERE username = %s ORDER BY created_at DESC", (username,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching user videos by username:", e)
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()