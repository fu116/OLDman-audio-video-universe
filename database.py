import mysql.connector 
from mysql.connector import Error

def get_db_connection():
    try:

        if connection.is_connected():
            print("Sucessfully connected to Mysql database")
            return connection
    except Error as e :
        print(f"Error while connecting to Mysql: {e}")    
        return None 

def create_user(username, email, hashed_password):
    """Takes user details and inserts a new row into the users table.
    Returns True if successful, or an error message string if it fails.
    """
    connection=get_db_connection()
    if not connection:
        return "Database connection faild."
    cursor=connection.cursor()
    try:
        cursor.execute("INSERT INTO users(username, email,password_hash) VALUES(%s,%s, %s)", (username,email,hashed_password))
        connection.commit()
        connection.commit()

        return True
    except Exception as e:
         print("REAL DATABASE ERROR:", e)  
         return f"Error: {e}"
    finally:
          # Always clean up cursor and connection resources
          cursor.close()
          connection.close()

def get_user_by_username(username):
    connection=get_db_connection()
    if not connection:
        return None
    try:
        cursor=connection.cursor(dictionary=True)
        print(f"DEBUG DB: Searching for username exact value -> [{username}]")
        cursor.execute("SELECT username FROM users")
        print("DEBUG DB: All usernames currently in MySQL:", cursor.fetchall())


        cursor.execute("SELECT * FROM users WHERE username = %s",(username,)) 
        user=cursor.fetchone()
        return user
    except Exception as e:
        print("DATABASE ERROR:", e)
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_user_interests(username,interests):
    connection=get_db_connection()
    if not connection:
       return False
    try:
        cursor=connection.cursor()
        cursor.execute("DELETE FROM user_interests WHERE username = %s", (username,))
        for interest in interests:
            cursor.execute("INSERT INTO user_interests(username,interest) VALUES (%s, %s)", (username, interest))
        connection.commit()
        return True
    except Exception as e:
          print("DATABASE ERORR:", e)
          return False 
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

            

from database import get_db_connection  # Keep your connection importer

def save_user_profile(username, full_name, bio, profile_pic=None):
    connection = get_db_connection()
    if connection:
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
    return False

def get_user_profile(username):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT username, full_name, bio, profile_pic, cover_pic, is_verified, monetization_enabled, social_github, social_twitter 
                FROM user_profiles 
                WHERE username = %s
            """, (username,))
            result = cursor.fetchone()
            return result
        except Exception as e:
            print("Error fetching profile:", e)
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return None

def get_user_videos(username):
    """Fetches all videos/content uploaded by a specific user."""
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
            print("Error fetching videos:", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return videos
def get_profile_stats(username):
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

def save_user_video(username, title, video_url, category="Videos"):
    """Saves a new video upload to the database."""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO user_videos (username, title, video_url, category) 
                VALUES (%s, %s, %s, %s)
            """, (username, title, video_url, category))
            connection.commit()
            return True
        except Exception as e:
            print("Error saving video:", e)
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False