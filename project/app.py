import sqlite3
import os
from flask import Flask, render_template, request, redirect, session, send_from_directory

app = Flask(__name__)
app.secret_key = "secretkey123"

# Folder for uploaded permission letters
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "permissions")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Database connection
def db():
    return sqlite3.connect("database.db")

# Route to serve uploaded files
@app.route("/uploads/permissions/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        con = db()
        cur = con.cursor()
        cur.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        res = cur.fetchone()
        con.close()

        if res:
            session["user"] = username
            session["role"] = res[0]
            return redirect(f"/{res[0]}")
    return render_template("login.html")

# Student dashboard
@app.route("/student", methods=["GET", "POST"])
def student():
    if session.get("role") != "student":
        return redirect("/")

    con = db()
    cur = con.cursor()

    if request.method == "POST":
        reason = request.form["reason"]
        attendance = request.form["attendance"]
        file = request.files["file"]

        if file.filename != "":
            filename = file.filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            cur.execute("""
                INSERT INTO leave_requests (student, reason, file, attendance, instructor_status, hod_status)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (session["user"], reason, filename, attendance, "Pending", "Pending")
            )
            con.commit()

    cur.execute("SELECT * FROM leave_requests WHERE student=?", (session["user"],))
    data = cur.fetchall()
    con.close()
    return render_template("student_dashboard.html", data=data)

# Instructor dashboard
@app.route("/instructor", methods=["GET", "POST"])
def instructor():
    if session.get("role") != "instructor":
        return redirect("/")

    con = db()
    cur = con.cursor()

    if request.method == "POST":
        rid = request.form["id"]
        status = request.form["status"]
        cur.execute("UPDATE leave_requests SET instructor_status=? WHERE id=?", (status, rid))
        con.commit()

    # Pending requests
    cur.execute("SELECT * FROM leave_requests WHERE instructor_status='Pending'")
    pending = cur.fetchall()

    # History
    cur.execute("SELECT * FROM leave_requests WHERE instructor_status!='Pending'")
    history = cur.fetchall()

    con.close()
    return render_template("instructor_dashboard.html", pending=pending, history=history)

# HOD dashboard
@app.route("/hod", methods=["GET", "POST"])
def hod():
    if session.get("role") != "hod":
        return redirect("/")

    con = db()
    cur = con.cursor()

    if request.method == "POST":
        rid = request.form["id"]
        status = request.form["status"]
        cur.execute("UPDATE leave_requests SET hod_status=? WHERE id=?", (status, rid))
        con.commit()

    # Pending requests = instructor approved only
    cur.execute("SELECT * FROM leave_requests WHERE instructor_status='Approved' AND hod_status='Pending'")
    pending = cur.fetchall()

    # History = all requests where HOD already made a decision
    cur.execute("SELECT * FROM leave_requests WHERE hod_status!='Pending'")
    history = cur.fetchall()

    con.close()
    return render_template("hod_dashboard.html", pending=pending, history=history)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
