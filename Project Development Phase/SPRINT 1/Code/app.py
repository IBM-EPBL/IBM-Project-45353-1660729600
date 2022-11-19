from flask import Flask, render_template, request, redirect, url_for, session, flash
from data import *
import ibm_db

app = Flask(__name__)
app.secret_key = "NPp82dqYbS1i9VoaVHv7cPr6bVU6zsz2"

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=3883e7e4-18f5-4afe-be8c-fa31c41761d2.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31498;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=kpr61031;PWD=bV1wp04ZQjiJ5UG4", '', '')

# Home Route


@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html', title="JOBX || Home")

# Recommendation Route


@app.route("/recommendation")
def recommendation():

    if "name" in session and 'interest' in session:
        name = session["name"]
        interest = session['interest']

        return render_template('recommendation.html', title="JOBX || Recommendation for you.", name=name, user_interest=interest, job=job)
    else:
        flash("You are not Logged In!")
        return redirect(url_for("joinus"))

# Joinus Route


@app.route("/joinus")
def joinus():
    if "name" in session:
        flash("Already Logged In!")
        return redirect(url_for('recommendation'))
    return render_template('joinus.html', title="Join JOBX")

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
                    name = dictionary['NAME']
                    session["name"] = name

                    session.pop("interest", None)
                    interest = dictionary['INTERESTS']
                    session["interest"] = interest
                    return redirect(url_for('recommendation'))
                else:
                    name = dictionary['NAME']
                    session["name"] = name

                    interest = dictionary['INTERESTS']
                    session["interest"] = interest

                    return redirect(url_for('  '))
            else:
                error = "Invalid Password"
                return render_template("joinus.html", error=error)
        else:
            error = "Invalid Email"
            return render_template("joinus.html", error=error)

    else:
        if "name" in session:
            flash("Already Logged In!")
            return redirect(url_for('recommendation'))
        return redirect(url_for("joinus"))


# Register Route
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        interest = request.form["interest"]

        # Initializing Session
        session["name"] = name
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
        else:
            error = "User Already Exists!"
            return render_template("joinus.html", error=error)

    return redirect(url_for('recommendation'))


# Upload
@app.route("/upload")
def upload():
    return render_template("upload.html", title="JOBX || Admin Panel")

# Logout


@app.route("/logout")
def logout():
    if "name" in session and "interest" in session:
        name = session["name"]
        flash(f"You have been logged out, {name}")
        session.pop("name", None)
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
    return render_template('404.html', title="Page Not Found!"), 404


# Running the App
if __name__ == "__main__":
    app.run(debug=True)
