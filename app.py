from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)
import sqlite3
import os
import qrcode

app = Flask(__name__)
app.secret_key = "library_secret_key"

@app.route("/")
def home():
     return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
     
     if request.method == "POST":
          
          matric_no = request.form["matric_no"]
          password = request.form["password"]

          connection = sqlite3.connect("library.db")
          cursor = connection.cursor()

          cursor.execute(
               "SELECT * FROM students WHERE matric_no = ?",
               (matric_no,)
          )

          student = cursor.fetchone()

          connection.close()

          if student and student[7] == password:
               session["student_id"] = student[0]

               return redirect("/dashboard")
          return "Invalid Matric Number or Password!"
     return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect("library.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    )

    student = cursor.fetchone()

    connection.close()

    return render_template(
        "dashboard.html",
        student=student
    )

@app.route("/logout")
def logout():

    session.pop("student_id", None)

    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        surname = request.form["surname"]
        other_names = request.form["other_names"]
        faculty = request.form["faculty"]
        department = request.form["department"]
        year_of_entry = request.form["year_of_entry"]
        matric_no = request.form["matric_no"]
        passport = request.files["passport"]
        filename = passport.filename

        passport.save(
            os.path.join(
                "static/uploads",
                filename
            )
        )
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        connection = sqlite3.connect("library.db")
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO students
        (surname, other_names, faculty, department,
         year_of_entry, matric_no, password, passport_photo)

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            surname,
            other_names,
            faculty,
            department,
            year_of_entry,
            matric_no,
            password,
            filename
        ))

        connection.commit()
        connection.close()

        return """
        <h2>Application Submitted Successfully!</h2>
        """

    return render_template("submit.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "librarian" and password == "admin123":

            session["admin"] = True

            return redirect("/admin")

        return "Invalid Admin Credentials!"

    return render_template("admin_login.html")

@app.route("/admin")
def admin():

    if "admin" not in session:
        return redirect("/admin/login")

    search = request.args.get("search")

    connection = sqlite3.connect("library.db")
    cursor = connection.cursor()

    # Statistics

    cursor.execute(
        "SELECT COUNT(*) FROM students"
    )
    total_students = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM students WHERE card_status='Pending'"
    )
    pending_cards = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM students WHERE card_status='Generated'"
    )
    generated_cards = cursor.fetchone()[0]

    # Student Records

    if search:

        cursor.execute(
            """
            SELECT * FROM students
            WHERE matric_no LIKE ?
            """,
            ('%' + search + '%',)
        )

    else:

        cursor.execute(
            "SELECT * FROM students"
        )

    students = cursor.fetchall()

    connection.close()

    return render_template(
        "admin.html",
        students=students,
        total_students=total_students,
        pending_cards=pending_cards,
        generated_cards=generated_cards
    )

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin/login")

@app.route("/generate_card/<int:id>")
def generate_card(id):

    if "admin" not in session:
        return redirect("/admin/login")

    card_number = f"LCU-LIB-{id:04d}"
    qr_filename = f"qr_{id}.png"

    qr_link = f"http://127.0.0.1:5000/verify/{id}"

    qr = qrcode.make(qr_link)

    qr.save(
        os.path.join(
            "static/qrcodes",
            qr_filename
        )
    )

    connection = sqlite3.connect("library.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE students
        SET
            card_status = 'Generated',
            card_number = ?,
            qr_code = ?
        WHERE id = ?
        """,
        (
            card_number,
            qr_filename,
            id
        )
    )

    connection.commit()
    connection.close()

    return redirect("/admin")

@app.route("/card/<int:id>")
def card(id):

        connection = sqlite3.connect("library.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE id = ?",
            (id,)
        )

        student = cursor.fetchone()

        connection.close()

        return render_template(
            "card.html",
            student=student
        )

@app.route("/my_card")
def my_card():

        if "student_id" not in session:
            return redirect("/login")

        connection = sqlite3.connect("library.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE id = ?",
            (session["student_id"],)
        )

        student = cursor.fetchone()

        connection.close()

        return render_template(
            "my_card.html",
            student=student
        )
        
@app.route("/verify/<int:id>")
def verify(id):

    connection = sqlite3.connect("library.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    )

    student = cursor.fetchone()

    connection.close()

    return render_template(
        "verify.html",
        student=student
    )

@app.route("/student/<int:id>")
def view_student(id):

    if "admin" not in session:
        return redirect("/admin/login")

    connection = sqlite3.connect("library.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    )

    student = cursor.fetchone()

    connection.close()

    return render_template(
        "view_student.html",
        student=student
    )


if __name__ == "__main__":
    app.run(debug=True)