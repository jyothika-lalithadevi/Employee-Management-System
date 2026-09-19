from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_database_connection():
    connection = sqlite3.connect("users.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            salary TEXT NOT NULL,
            joiningdate TEXT NOT NULL,
            address TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ================= HOME / NAVBAR =================

@app.route("/")
def home_page():
    return render_template("navbar.html")





# ================= HOME PAGE =================

@app.route("/home")
def home():
    return render_template("home.html")


# ================= REGISTER =================

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("reg2.html")


@app.route("/register", methods=["POST"])
def register():
    fullname = request.form["fullname"]
    username = request.form["username"]
    password = request.form["password"]

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users(fullname, username, password)
        VALUES(?, ?, ?)
    """, (fullname, username, password))

    connection.commit()
    connection.close()

    return redirect("/login")


# ================= LOGIN =================

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username=? AND password=?
    """, (username, password))

    user = cursor.fetchone()
    connection.close()

    if user:
        return "<h2>Login Successful</h2><p>Welcome, " + username + "!</p>"
    else:
        return "<h2>Login Failed</h2><p>Username or password is incorrect</p>"


# ================= ADD EMPLOYEE =================

@app.route("/add-employee", methods=["GET"])
def add_employee_page():
    return render_template("add-employee.html")


@app.route("/add-employee", methods=["POST"])
def add_employee():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    department = request.form["department"]
    salary = request.form["salary"]
    joiningdate = request.form["joiningdate"]
    address = request.form["address"]

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO employee(
            name, email, phone, department,
            salary, joiningdate, address
        )
        VALUES(?, ?, ?, ?, ?, ?, ?)
    """, (name, email, phone, department, salary, joiningdate, address))

    connection.commit()
    connection.close()

    return redirect("/employees")


# ================= EMPLOYEES =================

@app.route("/employees")
def employees():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM employee
        ORDER BY id ASC
    """)

    employees = cursor.fetchall()
    connection.close()

    return render_template("employees.html", employees=employees)


# ================= EDIT EMPLOYEE =================

@app.route("/edit-employee/<int:id>")
def edit_employee_page(id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM employee
        WHERE id=?
    """, (id,))

    employee = cursor.fetchone()
    connection.close()

    if employee is None:
        return """
            <h2>Employee not found</h2>
            <a href="/employees">Back to employees</a>
        """

    return render_template("edit-employee.html", employee=employee)


@app.route("/edit-employee/<int:id>", methods=["POST"])
def edit_employee(id):
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    department = request.form["department"]
    salary = request.form["salary"]
    joiningdate = request.form["joiningdate"]
    address = request.form["address"]

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE employee
        SET name=?,
            email=?,
            phone=?,
            department=?,
            salary=?,
            joiningdate=?,
            address=?
        WHERE id=?
    """, (
        name,
        email,
        phone,
        department,
        salary,
        joiningdate,
        address,
        id
    ))

    connection.commit()
    connection.close()

    return redirect("/employees")


# ================= DELETE EMPLOYEE =================

@app.route("/delete-employee/<int:id>")
def delete_employee(id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM employee
        WHERE id=?
    """, (id,))

    connection.commit()
    connection.close()

    return redirect("/employees")

# =================  SEARCH =================

@app.route("/search", methods=["GET", "POST"])
def search():
    search_name = ""
    employees = []

    if request.method == "POST":
        search_name = request.form["search_name"]

        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM employee WHERE name LIKE ?",
            ("%" + search_name + "%",)
        )

        employees = cursor.fetchall()
        connection.close()

    return render_template(
        "search.html",
        employees=employees,
        search_name=search_name
    )


# ================= RUN APPLICATION =================

if __name__ == "__main__":
    create_database()
    app.run(debug=True)
