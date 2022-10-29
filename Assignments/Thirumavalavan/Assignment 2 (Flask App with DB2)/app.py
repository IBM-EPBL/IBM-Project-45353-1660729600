from flask import Flask, render_template, url_for, request, redirect
import ibm_db

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31198;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=jrl43783;PWD=peHIvwMpj3I5zRLs", '', '')


app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/joinus")
def joinus():
    return render_template("joinus.html")


@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM NARIKOOTAM WHERE email=?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, email)
        ibm_db.execute(prep_stmt)
        dictionary = ibm_db.fetch_assoc(prep_stmt)

        if password == dictionary['PASSWORD']:
            return redirect(url_for('home'))
        else:
            return redirect(url_for('signin'))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]

        sql = "INSERT INTO NARIKOOTAM VALUES (?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, name)
        ibm_db.bind_param(prep_stmt, 2, email)
        ibm_db.bind_param(prep_stmt, 3, password)
        ibm_db.bind_param(prep_stmt, 4, username)
        ibm_db.execute(prep_stmt)
        print("Inserted Successfully")

    return redirect(url_for('home'))


@app.route("/members")
def members():
    members = []
    sql = "SELECT * FROM NARIKOOTAM"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_assoc(stmt)

    while dictionary != False:
        members.append(dictionary)
        dictionary = ibm_db.fetch_assoc(stmt)

    if members:
        return render_template("members.html", members=members)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
