import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime # Added for timestamp
import re # Added for regular expressions in password complexity checks

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():

    # Display a table with all of the current user's stocks, the number of shares of each, the current price of each stock, and the total value of each holding.
    # Display the user's current cash balance.

    # Create a new "portfolio" table in the db if it doesn't exist
    db.execute("CREATE TABLE IF NOT EXISTS portfolio ('id' INTEGER PRIMARY KEY, 'user_id' INTEGER NOT NULL, 'stock' VARCHAR(255) NOT NULL, 'name' VARCHAR(255) NOT NULL, 'shares' INTEGER NOT NULL, 'av_price' NUMERIC NOT NULL, 'total_price' NUMERIC NOT NULL)")

    # Create a new "history" table in the db if it doesn't exist
    db.execute("CREATE TABLE IF NOT EXISTS history ('id' INTEGER PRIMARY KEY, 'user_id' INTEGER NOT NULL, 'stock' VARCHAR(255) NOT NULL, 'price' NUMERIC NOT NULL, 'total_price' NUMERIC NOT NULL, 'shares' INTEGER NOT NULL, 'transaction_type' VARCHAR(255) NOT NULL, 'date' VARCHAR(255) NOT NULL)")

    # Extract the parameters from the user's portfolio
    rows = db.execute("SELECT * FROM portfolio WHERE user_id = :u_id", u_id=session["user_id"])

    # Calculate the total value of portfolio
    # Start by extracting "CASH" value
    user_money = db.execute("SELECT cash FROM users WHERE id = :u_id", u_id=session["user_id"])[0]["cash"]
    grand_total = user_money

    # Add each total price. However, should we really be adding the current price?
    for row in rows:
        grand_total = grand_total + row['total_price']

    return render_template('index.html', user_money=user_money, rows=rows, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    # When the form is submited via POST, purchase the stock so long as the user can afford it. -> add 1 or more extra table(s). (CREATE TABLE) Stock that was bough, how many. (see history)
    if request.method == "POST":

        symbol = request.form.get("symbol").upper()
        if request.form.get("shares"):
            shares = int(request.form.get("shares"))
        quote = lookup(symbol)

        # If the stock field was left blank, make sure to print an apology.
        if not symbol:
            return apology("Enter a stock.")

        # If the stock doesnt exist, make sure to print an apology.
        if not quote:
            return apology("Symbol not found.")

        # If # of shares is blank or less than 1, make sure to print an apology.
        if (not shares) or (shares < 1):
            return apology("Invalid number of shares.")

        # Extract how much CASH user has on hand.
        user_money = db.execute("SELECT cash FROM users WHERE id = :u_id", u_id=session["user_id"])[0]["cash"]
        purchase = quote['price'] * shares

        # Check that the user can afford it
        if purchase > user_money:
            return apology("Insufficient funds.")

        # Insert transaction to the "history" table.
        db.execute("INSERT INTO history (user_id, stock, price, total_price, shares, transaction_type, date) VALUES(:user_id, :stock, :price, :total_price, :shares, :transaction_type, :date)",
                   user_id=session["user_id"], stock=symbol, price=quote['price'], total_price=purchase, shares=shares, transaction_type="Buy", date=datetime.datetime.now())

        # Update the user's cash reserve.
        db.execute("UPDATE users SET cash=:cash WHERE id=:u_id", u_id=session["user_id"], cash=(user_money - purchase))

       # # Update the user's portfolio
       # # Check if already owns stock
        exist = db.execute("SELECT shares, total_price FROM portfolio WHERE user_id=:user_id AND stock=:stock",
                           user_id=session["user_id"], stock=symbol)

       # If not, create it
        if not exist:
            db.execute("INSERT INTO portfolio (user_id, stock, name, shares, av_price, total_price) VALUES(:user_id, :stock, :name, :shares, :av_price, :total_price)",
                       user_id=session["user_id"], stock=symbol, name=quote['name'], shares=shares, av_price=quote['price'], total_price=purchase)
        # If so, update the shares, average price and total price.
        else:
            new_total_shares = exist[0]['shares']+shares
            new_total_price = exist[0]['total_price']+purchase
            db.execute("UPDATE portfolio SET av_price=:av_price, total_price=:total, shares=:shares WHERE user_id=:user_id AND stock=:stock", user_id=session["user_id"], stock=symbol,
                       shares=new_total_shares, av_price=new_total_price/new_total_shares, total=new_total_price)

        # Redirect to index page
        return redirect("/")

    # When requested via GET, should display a form to buy a stock.
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():

    # Can do by only quarrying the table for history - Similar to the index table.
    rows = db.execute("SELECT * FROM history WHERE  user_id = :u_id", u_id=session["user_id"])

    # Redirect to history page
    return render_template('history.html', rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    # When form is submitted via POST, lookup the stock symbol by calling the lookup function, and display the result.
    if request.method == "POST":

        symbol = request.form.get("symbol")
        lookup_output = lookup(symbol)

        # If the stock doesnt exist, make sure to print an apology.
        if not lookup_output:
            return apology("Symbol not found")

        # Redirect to quoted page
        return render_template('quoted.html', lookup_output=lookup_output)

    # When requested via GET, should display form to request a stock quote. (print out the python dictionary)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    # When form is submitted via POST, insert new user ino table
    # Be sure to check for invalid inputs (duplicated user, invalid password confirmation -> display apology), and to hash the user's password.
    if request.method == "POST":

        username = request.form.get("username")
        password_hash = generate_password_hash(request.form.get("password"))
        user_exists = len(db.execute("SELECT * FROM users WHERE username = :username",
                                     username=request.form.get("username"))) > 0

        # Verify the strength of 'password'
        # Password requirements are :
        # 8 characters length or more
        # 1 digit or more
        # Check for length
        pw_l_invalid = len(request.form.get("password")) < 8
        # searching for digits
        pw_d_invalid = re.search(r"\d", request.form.get("password")) is None
        # Result
        password_valid = not (pw_l_invalid or pw_d_invalid)

        # Ensure username was submitted
        if not username:
            return apology("must enter username")

        # Ensure username doesn't exist already
        elif (user_exists):
            return apology("Username already exists")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must enter password")

        # Ensure same passwords were submitted
        elif not (request.form.get("password") == request.form.get("confirmation")):
            return apology("Passwords do not match")

        # Add password complexity requirements
        elif not password_valid:
            return apology("Passwords does not meet complexity requirements.")

        # Insert user into the database
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=username, hash=password_hash)

        # Redirect user to home page
        return redirect("/")

    # When requested via GET, should display registration form (similar to login html)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    # Opposite of buy. When the form is submitted via POST, sell the specified number of shares of stock, and update the user's cash.
    if request.method == "POST":

        symbol = request.form.get("symbol")
        if request.form.get("shares"):
            shares = int(request.form.get("shares"))

        # If the stock field was left blank, make sure to print an apology.
        if not symbol:
            return apology("Select a symbol.")

        quote = lookup(symbol)

       # Extract data from user portolio
        exist = db.execute("SELECT shares, total_price FROM portfolio WHERE user_id=:user_id AND stock=:symbol",
                           user_id=session["user_id"], symbol=symbol)

        # If # of shares is blank or less than 1, or more than user owns, make sure to print an apology.
        if (not shares) or (shares < 1) or (exist[0]["shares"] < shares):
            return apology("Number of shares is invalid.")

        # Extract cash from user db
        user_money = db.execute("SELECT cash FROM users WHERE id = :u_id", u_id=session["user_id"])[0]["cash"]
        sale = quote['price'] * shares

        # Insert transaction to the "history" table.
        db.execute("INSERT INTO history (user_id, stock, price, total_price, shares, transaction_type, date) VALUES(:user_id, :stock, :price, :total_price, :shares, :transaction_type, :date)",
                   user_id=session["user_id"], stock=symbol, price=quote['price'], total_price=sale, shares=shares, transaction_type="Sell", date=datetime.datetime.now())

        # Update the user's cash reserve.
        db.execute("UPDATE users SET cash=:cash WHERE id=:u_id", u_id=session["user_id"], cash=(user_money + sale))

        if (exist[0]["shares"] == shares):
            db.execute("DELETE FROM portfolio WHERE user_id=:user_id AND stock=:stock", user_id=session["user_id"], stock=symbol)
        # Update the user's portfolio
        else:
            new_total_shares = exist[0]['shares']-shares
            new_total_price = exist[0]['total_price']-sale
            db.execute("UPDATE portfolio SET av_price=:av_price, total_price=:total, shares=:shares WHERE user_id=:user_id AND stock=:stock",
                       user_id=session["user_id"], stock=symbol, shares=new_total_shares, av_price=new_total_price/new_total_shares, total=new_total_price)

        # Redirect to index page
        return redirect("/")

    # When requested via GET, should display a form to sell a stock. (+ error check)
    else:
        rows = db.execute("SELECT stock FROM portfolio WHERE user_id=:u_id", u_id=session["user_id"])
        return render_template("sell.html", rows=rows)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
