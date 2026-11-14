from db import get_db_connection

def create_user(username, email, password_hash):
    """Creates a new user in the database."""
    connection = get_db_connection()
    if not connection:
        return "Database connection failed."
    try:
        cursor = connection.cursor()
        query = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, password_hash))
        connection.commit()
        return True
    except mysql.connector.Error as err:
        if err.errno == 1062:  # Duplicate entry error code for MySQL
            return "Username or email already exists."
        return f"Database error: {err}"
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_by_username(username):
    """Fetches a user record by username."""
    connection = get_db_connection()
    if not connection:
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print("Error fetching user:", e)
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_user_interests(username, interests):
    """Saves selected user interests to the database."""
    connection = get_db_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        # Optional: clear old interests first if updating
        cursor.execute("DELETE FROM user_interests WHERE username = %s", (username,))
        
        query = "INSERT INTO user_interests (username, interest) VALUES (%s, %s)"
        for interest in interests:
            cursor.execute(query, (username, interest))
        
        connection.commit()
        return True
    except Exception as e:
        print("Error saving interests:", e)
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()