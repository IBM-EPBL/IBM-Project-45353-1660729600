from flask import Flask, render_template, request, redirect, url_for, session, flash
import ibm_db
import random
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail 
from dotenv import load_dotenv
from data import *
from mailtemplate import *

app = Flask(__name__)

load_dotenv()
# Environment Variables
FROM_EMAIL = os.getenv('FROM_EMAIL')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
IBM_DB_URL = os.getenv('IBM_DB_URL')
SECRET_KEY = os.getenv('SECRET_KEY')

# Setting Secret Key for Sessions
app.secret_key = SECRET_KEY

# Creating IBM DB Connection
conn = ibm_db.connect(IBM_DB_URL,'','')



# Home Route
@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html', title= "JOBX || Home")

# Recommendation Route
@app.route("/recommendation")
def recommendation():

    if "name" in session and 'interest' in session:
        name = session["name"]
        interest = session['interest']

        

        return render_template('recommendation.html', title="JOBX || Recommendation for you.", name = name, user_interest = interest, random = random,job=job)
    else:
        flash("You are not Logged In!")
        return redirect(url_for("joinus"))

# Joinus Route
@app.route("/joinus")
def joinus():
    if "name" in session:
        flash("Already Logged In!")
        return redirect(url_for('recommendation'))
    return render_template('joinus.html', title = "Join JOBX")

# Login Route
@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        sql = "SELECT * FROM USERS WHERE email=?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, email)
        ibm_db.execute(prep_stmt)

        # Checking if we are getting rows or not
        noData = False
        try:
            # Getting the Row as dictionary   
            dictionary = ibm_db.fetch_assoc(prep_stmt)
        except:
            pass
        
        if dictionary is False:
            noData = True
        else:
            noData = False

        if noData is False:
            if password == dictionary['PASSWORD']:      
                session['logged_in'] = True
                if "name" in session:
                    session.pop("name", None)
                    session.pop("email", None)
                    session.pop("interest", None)

                    name = dictionary['NAME']
                    session["name"] = name

                    email = dictionary['EMAIL']
                    session["email"] = email

                    interest = dictionary['INTERESTS']
                    session["interest"] = interest

                    return redirect(url_for('recommendation'))
                else:
                    name = dictionary['NAME']
                    session["name"] = name

                    interest = dictionary['INTERESTS']
                    session["interest"] = interest

                    email = dictionary['EMAIL']
                    session["email"] = email

                    return redirect(url_for('recommendation')) 
            else:
                error = "Invalid Password"
                return render_template("joinus.html",error= error)
        else:
            error = "Invalid Email"
            return render_template("joinus.html",error= error)
        
    else: 
        if "name" in session:
            flash("Already Logged In!")
            return redirect(url_for('recommendation')) 
        return redirect(url_for("joinus"))
        

# Register Route
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        interest = request.form["interest"]

        if uname[0].isupper():
            name = uname
        else:
            name = uname.capitalize()

        # Initializing Session
        session["name"] = name 
        session["email"] = email 
        session["interest"] = interest
        session['logged_in'] = True

        # Checking If User Email Already Exists
        sql = "SELECT * FROM USERS WHERE email=?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, email)
        ibm_db.execute(prep_stmt)

        # Checking if we are getting rows or not
        noData = False
        try:
            # Getting the Row as dictionary   
            dictionary = ibm_db.fetch_assoc(prep_stmt)
        except:
            pass
        
        if dictionary is False:
            noData = True
        else:
            noData = False

        if noData is True:
            sql = "INSERT INTO USERS VALUES (?,?,?,?)"
            try:
                prep_stmt = ibm_db.prepare(conn, sql)
            except:
                pass
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.bind_param(prep_stmt, 4, interest)
            try:
                ibm_db.execute(prep_stmt)
            except:
                pass

            # Sending Register Successful Mail to the user
            message = Mail(
            from_email= FROM_EMAIL,
            to_emails= email,
            subject='Welcome to JOBX',
            html_content= mailtemplate )

            sg = SendGridAPIClient(
            api_key= SENDGRID_API_KEY)
            try:
                response = sg.send(message)
            except Exception:
                pass
            print("Mail Sent and response code is ",response.status_code)

        else:
            error = "User Already Exists!"
            return render_template("joinus.html",error= error)

    return redirect(url_for('recommendation'))


#Upload
@app.route("/upload")
def upload():
    return render_template("upload.html", title= "JOBX || Admin Panel")

#Profile
@app.route("/profile")
def profile():
    if session['logged_in'] == True:
        email = session['email']
        sql = "SELECT * FROM USERS WHERE email=?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, email)
        ibm_db.execute(prep_stmt)
        # Checking if we are getting rows or not
        try:
            # Getting the Row as dictionary   
            dictionary = ibm_db.fetch_assoc(prep_stmt)
        except:
            pass
    else:
        flash("Please Login")
        return redirect(url_for("joinus"))


    return render_template("profile.html", title = "JOBX Profile", data = dictionary)

#Edit Profile
@app.route('/profile/edit')
def edit():
    if session['logged_in'] == True:
        email = session['email']
        # Fetching Data from DB
        sql = "SELECT * FROM USERS WHERE email=?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, email)
        ibm_db.execute(prep_stmt)
        try:
            # Getting the Row as dictionary   
            dictionary = ibm_db.fetch_assoc(prep_stmt)
        except:
            pass

        return render_template('edit.html', title = "JOBX || Edit Profile", dictionary = dictionary)

#Update Profile
@app.route("/update", methods=['GET', 'POST'])
def update():
    email = session['email']
    # Getting Data From Update Form
    if request.method == 'POST':
        u_uname = request.form["name"]
        u_email = request.form["email"]
        u_password = request.form["password"]
        u_interest = request.form["interest"]
        if u_uname[0].isupper():
            u_name = u_uname
        else:
            u_name = u_uname.capitalize()

        # Checking if data is update or not
        sql = "SELECT * FROM USERS WHERE email=?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, email)
        ibm_db.execute(prep_stmt)
        try:
            # Getting the Row as dictionary   
            acnt = ibm_db.fetch_assoc(prep_stmt)
        except:
            pass

        if acnt['NAME'] == u_uname and acnt['EMAIL'] == u_email and acnt['PASSWORD'] == u_password and acnt['INTERESTS'] == u_interest:
            flash("Nothing Updated")
            return redirect(url_for('home'))
        else:  
            # Updating Database
            sql = "UPDATE USERS SET NAME = ?, EMAIL= ?, PASSWORD= ?, INTERESTS= ? WHERE EMAIL = ?;"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, u_name)
            ibm_db.bind_param(prep_stmt, 2, u_email)
            ibm_db.bind_param(prep_stmt, 3, u_password)
            ibm_db.bind_param(prep_stmt, 4, u_interest)
            ibm_db.bind_param(prep_stmt, 5, email)
            try:
                ibm_db.execute(prep_stmt)
            except Exception as e:
                pass

        # Sending Register Successful Mail to the user
        message = Mail(
        from_email= FROM_EMAIL,
        to_emails= u_email,
        subject='JOBX Profile Updated',
        html_content= f"<h3 style='background-color: rgb(28, 28, 28);color:aliceblue;font-family: Verdana, Geneva, Tahoma, sans-serif;'>PROFILE UPDATED</h3><table style='width:100%;margin:0 auto'><tr><td>Name </td><td>{u_name}</td></tr><tr><td>Email </td><td>{u_email}</td></tr><tr><td>Password </td><td>{u_password}</td></tr><tr><td>Interests </td><td>{u_interest.upper()}</td></tr></table>" )
        sg = SendGridAPIClient(
        api_key= SENDGRID_API_KEY)
        try:
            response = sg.send(message)
        except Exception:
            pass
        print("Mail Sent and response code is ",response.status_code)
        
        # Loggin out user to login again with new details
        flash(f"Login with your updated details, {u_uname}")
        session.pop("name", None)
        session.pop("email", None)
        session.pop("interest", None)
        session['logged_in'] = False
        return redirect(url_for("home"))
 

# Logout
@app.route("/logout")
def logout():
    if "name" in session and "interest" in session:
        name = session["name"]
        flash(f"You have been logged out, {name}")
        session.pop("name", None)
        session.pop("email", None)
        session.pop("interest", None)
        session['logged_in'] = False
        return redirect(url_for("home"))
    else:
        flash(f"You are not Logged In!")
        return redirect(url_for("home"))

# About Route
@app.route("/about")
def about():
    return render_template('about.html', title="About JOBX")

# Handling Errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',title = "Page Not Found!"), 404

# Running the App
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)