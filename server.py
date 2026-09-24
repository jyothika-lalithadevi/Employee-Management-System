from flask import Flask,render_template,request,redirect,session, make_response
import sqlite3
from werkzeug.security import generate_password_hash,check_password_hash
app=Flask(__name__)
app.secret_key="employee-management-secret-key"
def get_database_connection():
   connection=sqlite3.connect("users.db")
   connection.row_factory=sqlite3.Row
   return connection
def create_database(): 
 # connect to database
    connection=sqlite3.connect("users.db")
 # store database in some object
    cursor=connection.cursor()
 #write query using that object

      #=========== USERS-TABLE===========
    cursor.execute("""create table if not exists users(id integer primary key autoincrement,
    fullname text not null,username text unique not null,password text not null)""")


       #========== EMPLOYEE-TABLE =========
    cursor.execute("""CREATE TABLE IF NOT EXISTS employee (id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,name TEXT NOT NULL,
    email TEXT NOT NULL,phone TEXT NOT NULL,department TEXT NOT NULL,salary REAL NOT NULL,joiningdate TEXT NOT NULL,
    address TEXT NOT NULL)""")
    #commit query
    connection.commit()
    #close connection
    connection.close()


#============= LOGIN CHECK ============


def login_required():
    return "user_id" in session 


#=========== SET-THEME ===============


@app.route("/set-theme/<theme>") 
def set_theme(theme):
   if theme not in["light","dark"]:
       theme="light"
   previous_page=request.referrer or"/" 
   response=make_response(
      redirect(previous_page)
   )
   response.set_cookie(
       "theme",theme,
       max_age=60*60*24*365
      ) 
   return response


 #============  HOME PAGE  =================
@app.route("/" ,methods=["GET"]) 
def home_page():
   if not login_required():
      return redirect("/login")
   theme=request.cookies.get("theme","light")
   username=session.get("username")
   fullname=session.get("fullname")
   return render_template(
    "navbar.html",
    theme=theme,
    username=username,
    fullname=fullname
   )
@app.route("/register",methods=["GET"])
def register_page():
   theme=request.cookies.get(
       "theme","light"
   )
   return render_template("reg2.html", theme=theme)


#==============REGISTER-POST=============
    

@app.route("/register",methods=["POST"])
def register():
   fullname=request.form.get("fullname","").strip()
   username=request.form.get("username","").strip()
   password=request.form.get("password","")
   if not fullname:
      return render_template("reg2.html",theme=request.cookies.get("theme","light"),
      error="fullname is required")
   if not username:
      return render_template("reg2.html",theme=request.cookies.get("theme","light"),
      error="username is required")
   if not password:
      return render_template("reg2.html",theme=request.cookies.get("theme","light"),
      error="password is required") 
   #hash password
   hashed_password=generate_password_hash(password)
   #insert user
   connection=get_database_connection()
   cursor=connection.cursor()
   try:
         cursor.execute("""insert into users(fullname,username,password)values(?,?,?)""",(fullname,username,hashed_password))
         connection.commit()
   except sqlite3.IntegrityError:
            connection.close()
            return render_template (
                 "reg2.html",
                 theme=request.cookies.get("theme","light"),
                  error="username already existed")
   connection.close()
   return redirect("/login")


#============= LOGIN-GET =============


@app.route("/login", methods=["GET"])
def login_page():
    if "user_id" in session:
        return redirect("/")
    theme=request.cookies.get("theme","light")
    return render_template("login.html",theme=theme)



#================ LOGIN-POST==============


@app.route("/login",methods=["POST"])
def login():
   username=request.form.get("username","").strip()
   password=request.form.get("password","") 
   if not username or not password:
       return render_template("login.html",
                              theme=request.cookies.get("theme","light"),
                              error="username or password are required")
   
   connection=get_database_connection()
   cursor=connection.cursor()
   cursor.execute("""SELECT id,fullname,username,password FROM users
   WHERE username=? """,(username,))
   user=cursor.fetchone()
   connection.close()

   if user is None:
          return render_template("login.html",
                                 theme=request.cookies.get("theme","light"),
                                 error="username or password is incorrect")
   password_correct=check_password_hash(user["password"],password)

   if not password_correct:
      return render_template("login.html",
                             theme=request.cookies.get("theme","light"),
                              error="username or password is incorrect")
   session.clear()
   session["user_id"]=user["id"]
   session["username"]=user["username"]
   session["fullname"]=user["fullname"]
   return redirect("/")


#============  LOGOUT  ===============


@app.route("/logout")
def logout():
   session.clear()
   return redirect("/login")
   
   
#============  ADDEMPLOYEE-GET  ==============

 
@app.route("/add-employee",methods=["GET"])
def add_employee_page():
    if not login_required():
        return redirect("/login")
    theme=request.cookies.get("theme","light")
    return render_template("add-employee.html",theme=theme)


#===============  ADDEMPLOYEE-POST  ==============


@app.route("/add-employee",methods=["POST"])
def add_employee():
      if not login_required():
         return redirect("/login")
         
      name=request.form.get("name","").strip()
      email=request.form.get("email","").strip()
      phone=request.form.get("phone","").strip()
      department=request.form.get("department","").strip()
      salary=request.form.get("salary","").strip()
      joiningdate=request.form.get("joiningdate","").strip()
      address=request.form.get("address","").strip()
      
      #validation

      if not name:
         return "name is required!"
      if not email:
         return "email is required"
      if not phone:
         return "phone is required"
      if not department:
         return "department is required"
      if not salary:
         return "salary is required"
      if not joiningdate:
         return "joiningdate is required"
      if not address:
         return "address is required"
      connection=get_database_connection()
      cursor=connection.cursor()
      cursor.execute("""insert into employee(user_id,name,email,phone,department,salary,joiningdate,address)
      VALUES(?,?,?,?,?,?,?,?)""",(session["user_id"],name,email,phone,department,salary,joiningdate,address))
      connection.commit()
      connection.close()
      return redirect("/employees")
         

#=============== EMPLOYEE =============

      
@app.route("/employees", methods=["GET", "POST"])
def employees():
      if not login_required():
        return redirect("/login")


      connection = get_database_connection()
      cursor = connection.cursor()
      cursor.execute("SELECT * FROM employee WHERE user_id = ? ORDER BY id ASC",
               (session["user_id"],))
      employees = cursor.fetchall()
      connection.close()
      theme=request.cookies.get("theme","light")
      return render_template(
               "employees.html",
               employees=employees,
               theme=theme)


#=========== EDIT EMPLOYEE PAGE ===========


@app.route("/edit-employee/<int:id>")
def edit_employee_page(id):
   if not login_required():
      return redirect("/login")
   theme = request.cookies.get("theme", "light")

   connection = get_database_connection()
   cursor = connection.cursor()

   cursor.execute(
    """SELECT * FROM employee
       WHERE id=? AND user_id=?""",
    (id, session["user_id"]))
   employee = cursor.fetchone()
   connection.close()

   if employee is None:
        return """
        <h2>Employee not found</h2>
        <a href="/employees">Back to employees</a>
        """

   return render_template(
        "edit-employee.html",
        employee=employee,
        theme=theme
     )


#============= EDIT EMPLOYEE UPDATE(POST) ===========


@app.route("/edit-employee/<int:id>",methods=["POST"])
def edit_employee(id):
    if not login_required():
        return redirect("/login")

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    department = request.form["department"]
    salary = request.form["salary"]
    joiningdate = request.form["joiningdate"]
    address = request.form["address"]

    connection=get_database_connection()
    cursor=connection.cursor()

    cursor.execute(
    """UPDATE employee
       SET name=?, email=?, phone=?, department=?,
           salary=?, joiningdate=?, address=?
       WHERE id=? AND user_id=?""",
    (name, email, phone, department, salary,
     joiningdate, address, id, session["user_id"]))
    connection.commit()
    connection.close()
    return redirect("/employees")

#=========== DELETE ==========


@app.route("/delete-employee/<int:id>")
def delete_employee(id):
   if not login_required():
      return redirect("/login")
   
   connection=get_database_connection()
   cursor = connection.cursor()

   cursor.execute(
    "DELETE FROM employee WHERE id=? AND user_id=?",
    (id, session["user_id"]))
   
   connection.commit()
   connection.close()
   return redirect("/employees")


# ============ SEARCH EMPLOYEE ============

@app.route("/search", methods=["GET", "POST"])
def search_employee():

    if not login_required():
        return redirect("/login")

    search_name = ""

    if request.method == "POST":
        search_name = request.form.get("search_name", "").strip()

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """SELECT * FROM employee
           WHERE user_id = ? AND name LIKE ?
           ORDER BY id ASC""",
        (session["user_id"], "%" + search_name + "%")
    )

    employees = cursor.fetchall()
    connection.close()

    theme = request.cookies.get("theme", "light")

    return render_template(
        "search.html",
        employees=employees,
        search_name=search_name,
        theme=theme
    )


#=========== HOME =========


@app.route("/home" ,methods=["GET"]) 
def home():
   if not login_required():
      return redirect("/login")

   theme = request.cookies.get("theme", "light")
   return render_template(
        "home.html",
        theme=theme)




#========= MAIN FUNCTION ==========


if __name__=="__main__":
    create_database()
    app.run(host="0.0.0.0", port=5000)
