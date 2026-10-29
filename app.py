from flask import Flask, render_template, request, g, redirect, flash, url_for
import sqlite3
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

bcrypt = Bcrypt(app)

DATABASE = "users.db"

# =========================
# DATABASE CONNECTION
# =========================
def get_db():
    # Connect to database
    db = getattr(g, '_database', None)
    # Check to see if there is aleady a connection to db; if not, connect
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# =========================
# CLEANUP CONNECTION
# =========================
@app.teardown_appcontext
def close_connection(exception):
    # Close database connection if it exists in g
    db = getattr(g, '_database', None)
    # if database is connected; disconnect
    if db is not None:
        db.close()


# =========================
# INITIALIZE DATABASE
# =========================
def init_db():
    # TO-DO: create products table if not exists with columns: id, name, category, price, stock (DONE)
    conn = get_db()
    # Create table if it does not already exist
    conn.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,
            fullname TEXT, username TEXT, password TEXT, confirm_password TEXT)''')
    # Save changes
    conn.commit()
    return "Database table initialized!"

@app.route("/")
def home():
    conn = get_db()
    return redirect("/register")

# =========================
# REGISTER USER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
            fullname = request.form["fullname"].strip()  # strip extra spaces
            username = request.form["username"].strip().capitalize()  # strip extra spaces/capitalize
            password = request.form["password"].strip()  # strip extra spaces
            confirm_password = request.form["confirm_password"].strip()  # strip extra spaces

            #TODO Input validation
            # Validate fullname
            # Check if full name is empty; has a space between first and last. 
            if not fullname:
                return render_template("register.html",
                                       error="Name cannot be empty.", fullname=fullname, username=username)
            if " " not in fullname:
                return render_template("register.html",
                                       error="Please enter first name, space, last name (example: Britt James).", fullname=fullname, username=username)
            # Remove allowed characters (space); then validate remaining characters
            cleaned_name = fullname.replace(" ", "")
            if not cleaned_name.isalnum():
                return render_template("register.html",
                                       error="Name cannot contain special characters (except a space between first and last names).", fullname=fullname, username=username)

            # Validate username
            # Check if user name is empty; only letters and numbers accepted
            if not username:
                return render_template("register.html",
                                       error="Username cannot be empty.\nUsername must contain only letters, numbers, and underscores. No special characters are allowed", fullname=fullname, username=username)
            # Remove allowed characters (underscore); then validate remaining characters
            cleaned_username = username.replace("_", "")
            if not cleaned_username.isalnum():
                return render_template("register.html",
                                       error="Username must contain only letters, numbers, and underscores. No special characters are allowed.", fullname=fullname, username=username)

            # Validate password
            # Check if at least 8 characters long; must include at least 1 letter and 1 number.
            if len(password) < 8:
                return render_template("register.html",
                                       error="Password must be at least 8 characters long and include both letters and numbers.", fullname=fullname, username=username)
            
            # Check for at least one letter
            if not any(char.isalpha() for char in password):
                return render_template("register.html",
                                       error="Password must contain at least one letter.", fullname=fullname, username=username)
            # Check for at least one number
            if not any(char.isdigit() for char in password):
                return render_template("register.html",
                                       error="Password must contain at least one number.", fullname=fullname, username=username)

            # Once validated hash password
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            
            # Validate confirm password
            if not bcrypt.check_password_hash(hashed_password, confirm_password):
                return render_template("register.html",
                                       error="Password do not match.", fullname=fullname, username=username)
            
            
            # Once data is validated, write to the database
            conn = get_db()
            conn.execute("""
                INSERT INTO users (fullname, username, password, confirm_password)
                VALUES (?, ?, ?, ?)
                """, (fullname, username, hashed_password, confirm_password))
            conn.commit()
            # TODO Display success message
            # Display success message
            flash(f"Success! {fullname} ({username}) has been added to the database.")
            flash(f"Password hashed for privacy and security: {hashed_password}")
                  
            
            # Send user back to the Add Items page
            return redirect(url_for("register")) 

    return render_template("register.html")



# =========================
# MAIN BLOCK
# =========================

# run init_db() automatically in main block
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, port=5000) # Run app on port 5000