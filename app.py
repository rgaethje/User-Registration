from flask import Flask, render_template, request, g, redirect, flash, url_for
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

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

            # Once data is validated, write to the database
            conn = get_db()
            conn.execute("""
                INSERT INTO users (fullname, username, password, confirm_password)
                VALUES (?, ?, ?, ?)
                """, (fullname, username, password, confirm_password))
            conn.commit()
            # TODO Display success message
            
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