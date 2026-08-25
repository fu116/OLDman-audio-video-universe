import mysql.connector 
from mysql.connector import Error

def get_db_connection():
    try:
        connection=mysql.connector.connect(
            host="localhost",
            database="oldman_db",
            user='root',
            password="123@@@###fuad"
        )
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

            


