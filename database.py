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
        query="INSERT INTO users(username, email,password_hash) VALUES(%s,%s, %s)"
        cursor.execute(query, (username,email,hashed_password))
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



    