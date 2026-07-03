from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import joblib
import sqlite3
import plotly.express as px
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
app.secret_key = "eduinsight123"

# -----------------------------
# Load AI Model
# -----------------------------
model = joblib.load("model.pkl")

# -----------------------------
# Load Dataset
# -----------------------------
data = pd.read_csv("student_performance_dataset.csv")

# -----------------------------
# Label Encoders
# -----------------------------
gender_encoder = LabelEncoder()
department_encoder = LabelEncoder()

gender_encoder.fit(data["Gender"])
department_encoder.fit(data["Department"])


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        if username=="admin" and password=="admin123":

            session["user"]=username

            return redirect("/dashboard")

        else:

            return render_template(
                "login.html",
                error="Invalid Username or Password"
            )

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():

    if "user" not in session:

        return redirect("/login")

    return render_template("index.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:

        return redirect("/login")
    conn = sqlite3.connect("students.db")

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM students WHERE prediction='PASS ✅'")
    pass_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM students WHERE prediction='FAIL ❌'")
    fail_count = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(confidence) FROM students")
    avg = cursor.fetchone()[0]

    if avg is None:
        avg = 0

    avg_confidence = round(avg, 2)

    cursor.execute("SELECT * FROM students ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total=total,
        pass_count=pass_count,
        fail_count=fail_count,
        avg_confidence=avg_confidence,
        rows=rows
    )


@app.route("/analytics")
def analytics():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("students.db")

    df = pd.read_sql_query("SELECT * FROM students", conn)

    conn.close()

    if df.empty:
        return render_template("analytics.html", nodata=True)

    # PASS vs FAIL
    pie = px.pie(
        df,
        names="prediction",
        title="PASS vs FAIL"
    )

    # Department Performance
    bar = px.bar(
        df,
        x="department",
        color="prediction",
        title="Department Performance"
    )

    # Grade Distribution
    grade = px.histogram(
        df,
        x="grade",
        color="grade",
        title="Grade Distribution"
    )

    # Attendance vs Final Marks
    attendance = px.scatter(
        df,
        x="attendance",
        y="finalexammarks",
        color="prediction",
        title="Attendance vs Final Marks"
    )

    # Study Hours vs Final Marks
    study = px.scatter(
        df,
        x="studyhours",
        y="finalexammarks",
        color="grade",
        title="Study Hours vs Final Marks"
    )

    # Confidence Distribution
    confidence = px.histogram(
        df,
        x="confidence",
        title="Prediction Confidence"
    )

    return render_template(
        "analytics.html",
        nodata=False,
        pie=pie.to_html(full_html=False),
        bar=bar.to_html(full_html=False),
        grade=grade.to_html(full_html=False),
        attendance=attendance.to_html(full_html=False),
        study=study.to_html(full_html=False),
        confidence=confidence.to_html(full_html=False)
    )
# -----------------------------
# History Page
# -----------------------------
@app.route("/history")
def history():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT studentid,
               studentname,
               gender,
               department,
               attendance,
               studyhours,
               prediction,
               confidence,
               grade
        FROM students
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return render_template("history.html", rows=rows)

@app.route("/profile/<studentid>")
def profile(studentid):

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE studentid=?",
        (studentid,)
    )

    student = cursor.fetchone()

    conn.close()

    if student is None:
        return "Student not found!"

    return render_template(
        "profile.html",
        student=student
    )
@app.route("/search", methods=["GET", "POST"])
def search():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    rows = []

    if request.method == "POST":

        keyword = request.form["keyword"].strip()

        cursor.execute("""
            SELECT * FROM students
            WHERE studentid LIKE ?
               OR studentname LIKE ?
        """, ('%' + keyword + '%', '%' + keyword + '%'))

        rows = cursor.fetchall()

        print("Keyword:", keyword)
        print("Rows:", rows)

    conn.close()

    return render_template("search.html", rows=rows)
# -----------------------------
# Predict Student Performance
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():

    # Student Details
    studentid = request.form["studentid"]
    studentname = request.form["studentname"]

    gender_text = request.form["gender"]
    department_text = request.form["department"]

    # Convert text to numbers
    gender = gender_encoder.transform([gender_text])[0]
    department = department_encoder.transform([department_text])[0]

    attendance = float(request.form["attendance"])
    studyhours = float(request.form["studyhours"])
    internal = float(request.form["internal"])
    assignment = float(request.form["assignment"])
    finalexam = float(request.form["finalexam"])

    # Features for AI Model
    features = [[
        gender,
        department,
        attendance,
        studyhours,
        internal,
        assignment,
        finalexam
    ]]

    # AI Prediction
    prediction = model.predict(features)[0]

    # Prediction Confidence
    probability = model.predict_proba(features)
    confidence = round(max(probability[0]) * 100, 2)

    # Pass / Fail
    if prediction == 1:
        result = "PASS ✅"
    else:
        result = "FAIL ❌"

    # Grade Prediction
    if finalexam >= 90:
        grade = "A+"
    elif finalexam >= 80:
        grade = "A"
    elif finalexam >= 70:
        grade = "B"
    elif finalexam >= 60:
        grade = "C"
    else:
        grade = "D"

    # AI Suggestions
    suggestions = []

    if attendance < 75:
        suggestions.append("Improve your attendance.")

    if studyhours < 4:
        suggestions.append("Increase your daily study hours.")

    if assignment < 60:
        suggestions.append("Complete more assignments.")

    if finalexam < 60:
        suggestions.append("Focus on exam preparation.")

    if len(suggestions) == 0:
        suggestions.append("Excellent performance! Keep up the good work.")

    suggestion = " ".join(suggestions)

    # Save Prediction to Database
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students(
            studentid,
            studentname,
            gender,
            department,
            attendance,
            studyhours,
            internalmarks,
            assignmentmarks,
            finalexammarks,
            prediction,
            confidence,
            grade
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        studentid,
        studentname,
        gender_text,
        department_text,
        attendance,
        studyhours,
        internal,
        assignment,
        finalexam,
        result,
        confidence,
        grade
    ))

    conn.commit()
    conn.close()

    return render_template(
        "index.html",
        prediction=result,
        confidence=confidence,
        grade=grade,
        suggestion=suggestion,
        studentid=studentid,
        studentname=studentname
    )


# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)