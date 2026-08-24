import datetime
from flask import Flask, render_template,request,redirect ,url_for ,flash
from werkzeug.security import generate_password_hash
from database import get_db_connection,create_user



app = Flask(__name__)
app.secret_key = "super-secret-key-12345"
@app.route("/" ,methods=["GET"])
def home():
     connection=get_db_connection()   

     if connection:
        connection.close() # Always close the connection when done to save server resources
        status_message= "OLDMAN Server is running and MySQL Connected Successfully!"
     
     else:
        status_message ="OLDMAN Server is running, but MySQL Connection Failed!"   


     kwargs={
       "db_status":status_message 
    }
     return render_template("index.html", **kwargs)



if __name__== '__main__':
    app.run(debug=True)       

# Route to show the registration page
@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")



@app.route("/register", methods=["POST"])
def register_user():
    username=request.form.get("username")
    email=request.form.get("email")
    password=request.form.get("password")

    #Securly hash the password
    hash_password=generate_password_hash(password)

    #Call the database function we created in database.py
    result= create_user(username, email, hash_password)
    print("DATABASE RESULT:", result)
    if result is True:
        flash("Account created successfully! You can now log in")
    else:
        flash(result) #Flash the error message returnd from database.py   

    return redirect(url_for("register_page"))
