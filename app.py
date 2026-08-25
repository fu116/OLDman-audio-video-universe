import datetime
from flask import Flask, render_template,request,redirect ,url_for ,flash,session
from werkzeug.security import generate_password_hash,check_password_hash
from database import get_db_connection,create_user,get_user_by_username,save_user_interests



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
    result=create_user(username, email, hash_password)
    print("DATABASE RESULT:", result)
    if result is True:
        flash("Account created successfully! You can now log in")
        return redirect(url_for("login"))
    else:
        flash(result) #Flash the error message returnd from database.py   
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
            
            # Redirect straight to your interests page (Step 4)
            return redirect(url_for("interests"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))
            
    return render_template("login.html")



@app.route("/interests", methods=["GET","POST"])
def interests():
    if "username" not in session:
        flash("please log in first ." , "error")
        return redirect(url_for("login"))

    available_interests=[
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

    if request.method=="POST":
       selected_interests=request.form.getlist("interests")
       print("DEBUG: Raw form data received:", request.form)
       print("DEBUG: Selected interests list:", selected_interests)
       if not selected_interests:
          print("DEBUG: Selection list was empty!")
          flash("Please select at least one interest.", "error")
          return redirect(url_for("interests")) 

       
       success=save_user_interests(session["username"],selected_interests)
       print("DEBUG: Save success status:", success)

       if success :
          flash("Interests saved successfully!", "success")
          return redirect(url_for("dashboard"))
       else:
           flash("Error saving  interests. Try again", "error")
           return redirect(url_for("interests"))


    return render_template("interests.html", interests=available_interests)















