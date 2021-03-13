import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

from datetime import datetime  # Added for timestamp
import re  # Added for regular expressions in password complexity checks
import requests  # Added for Reddit interaction
import json  # Added for Reddit interaction

# Configure application
app = Flask(__name__)

# Description:
# Basic news aggregator which seperates the news based on "left wing" to "right wing" bias.
# News leaning is based on the source. Leaning of the source if based on allsides.com
# guests can :
#   - view the news
#   - view the comments
#   - view the number of likes
#   - register
# Regular users can:
#   - view the news
#   - Post and view comments
#   - Like and view the number of likes
#   - Edit own user profile (so far, only editable item is email address)
# Admin can
#   - view the news
#   - Post and view comments
#   - Like and view the number of likes
#   - Edit profile for all users, including the ability to set the user as administrator and to delete users
#   - Change/add/delete news sources (change the name, URL, leaning). Can also disable a source so that it no longer shows up on the index (but articles are still in database and will re-appear if source is re-abled)
#   - Update the news shown on the index by fetching the latest data from newsAPI

# Issues and future improvements:
# News scrapping should be automated, right now admin needs to manually "fetch the news"
# Currently, news only visible is "top ten" from today. Ideally, the index would be "multi-page" so that the user can view the news from previous days.
# After scrapping the latest news, if a source which is not in the database is used. It will be added to the database, however, there is no indication to the admin that the leaning needs to be inputed.
# Content of the news article is not fully visible in free newsAPI version.
# Use Flask "role" feature. Currently using a simple if statement to check if the user is admin (by check in database). This is dangerous since somebody could easily guess the name of the "is_admin" variable in the database and generate a querry to register themselves as admin.
# Detailed user profiles and ability for users to follow one another
# There's a million other features that are common to social medias which would eventually need to be added (sorting, blocking, private messaging, sharing...etc.)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///scrapper.db")


@app.route("/")
def index():

    # Create a new "Users" table in the db if it doesn't exist
    db.execute("CREATE TABLE IF NOT EXISTS users ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL, 'is_admin' boolean NOT NULL DEFAULT 0, 'email' varchar(255))")

    # Create a new "News Item" table in the db if it doesn't exist
    db.execute("CREATE TABLE IF NOT EXISTS news_items ('id' INTEGER PRIMARY KEY, 'author' VARCHAR(255), 'headline' TEXT NOT NULL, 'description' TEXT, 'content' TEXT, 'url' TEXT NOT NULL, 'imgurl' TEXT, 'source_id' INTEGER, 'publishedat' DATETIME, 'date' DATETIME NOT NULL)")

    # Create a new "Sources" table in the db if it doesn't exist
    db.execute("CREATE TABLE IF NOT EXISTS sources ('id' INTEGER PRIMARY KEY, 'name' VARCHAR(255) DEFAULT NULL, 'url' TEXT DEFAULT NULL, 'bias' VARCHAR(255) DEFAULT NULL, 'disabled' BOOLEAN DEFAULT 0)")

    # Create a new "Likes" table in the db if it doesn't exist
    db.execute("CREATE TABLE IF NOT EXISTS news_item_likes ('id' INTEGER PRIMARY KEY, 'news_item_id' INTEGER NOT NULL, 'user_id' INTEGER NOT NULL)")

    # Create a new "Likes" table in the db if it doesn't exist
    db.execute("CREATE TABLE IF NOT EXISTS news_item_comments ('id' INTEGER PRIMARY KEY, 'comment' TEXT, 'news_item_id' INTEGER NOT NULL, 'user_id' INTEGER NOT NULL, 'date' DATETIME NOT NULL)")

    # Extract l, c and r news from database
    leftnews = db.execute(
        "SELECT news_items.id, news_items.headline, news_items.imgurl, news_items.url, news_items.date, sources.name, sources.url AS sourceurl, (SELECT COUNT() FROM news_item_likes WHERE news_item_id = news_items.id) AS likes, (SELECT COUNT() FROM news_item_comments WHERE news_item_id= news_items.id) AS commentsnb FROM news_items JOIN sources ON sources.id = news_items.source_id WHERE DATE(date) >= DATE() AND bias=:bias AND sources.disabled=0 ORDER BY likes DESC", bias="left")[:10]
    centernews = db.execute(
        "SELECT news_items.id, news_items.headline, news_items.imgurl, news_items.url, news_items.date, sources.name, sources.url AS sourceurl, (SELECT COUNT() FROM news_item_likes WHERE news_item_id = news_items.id) AS likes, (SELECT COUNT() FROM news_item_comments WHERE news_item_id= news_items.id) AS commentsnb FROM news_items JOIN sources ON sources.id = news_items.source_id WHERE DATE(date) >= DATE() AND bias=:bias AND sources.disabled=0 ORDER BY likes DESC", bias="center")[:10]
    rightnews = db.execute(
        "SELECT news_items.id, news_items.headline, news_items.imgurl, news_items.url, news_items.date, sources.name, sources.url AS sourceurl, (SELECT COUNT() FROM news_item_likes WHERE news_item_id = news_items.id) AS likes, (SELECT COUNT() FROM news_item_comments WHERE news_item_id= news_items.id) AS commentsnb FROM news_items JOIN sources ON sources.id = news_items.source_id WHERE DATE(date) >= DATE() AND bias=:bias AND sources.disabled=0 ORDER BY likes DESC", bias="right")[:10]

    # Extract the number of likes for each article, and list of articles liked by user.
    likes_dict = db.execute(
        "SELECT news_item_id FROM news_item_likes WHERE news_item_likes.user_id =:user_id GROUP BY news_item_id", user_id=session.get("user_id"))
    likes_list = [d['news_item_id'] for d in likes_dict]  # There is probably a more efficient way to do this.

    return render_template('index.html', leftnews=leftnews, centernews=centernews, rightnews=rightnews, likes=likes_list, isadmin=useris_admin())


@app.route('/view_<int:id>')
def view(id):

    # Extract the requested news article from the database
    news_item = db.execute(
        "SELECT news_items.id, news_items.headline, news_items.author, news_items.imgurl, news_items.url, news_items.publishedat, news_items.content, sources.name, sources.url AS sourceurl, (SELECT COUNT() FROM news_item_likes WHERE news_item_id = news_items.id) AS likes FROM news_items JOIN sources ON sources.id = news_items.source_id WHERE news_items.id=:id", id=id)[0]

    comments = db.execute(
        "SELECT comment, date, (SELECT username FROM users WHERE users.id=news_item_comments.user_id) AS username FROM news_item_comments WHERE news_item_id=:id ORDER BY date DESC", id=id)

    comments_nb = db.execute("SELECT COUNT() FROM news_item_comments WHERE news_item_id=:id", id=id)[0]['COUNT()']

    # Extract the number of likes for each article, and list of articles liked by user.
    likes_dict = db.execute(
        "SELECT news_item_id FROM news_item_likes WHERE news_item_likes.user_id =:user_id GROUP BY news_item_id", user_id=session.get("user_id"))
    likes_list = [d['news_item_id'] for d in likes_dict]  # There is probably a more efficient way to do this.

    return render_template('view.html', news_item=news_item, likes=likes_list, comments=comments, comments_nb=comments_nb, isadmin=useris_admin())


@app.route("/newslike_<int:id>", methods=["POST"])
@login_required
def newslike(id):

    # Determine if the user as already liked the news item (so that user can't like more than once)
    liked = len(db.execute("SELECT id FROM news_item_likes WHERE news_item_likes.user_id =:user_id AND news_item_likes.news_item_id =:news_item_id",
                           user_id=session.get("user_id"), news_item_id=id)) > 0

    if liked:  # If the user liked it, unlike if the form is submitted
        liked_id = db.execute("SELECT id FROM news_item_likes WHERE news_item_likes.user_id =:user_id AND news_item_likes.news_item_id =:news_item_id",
                              user_id=session.get("user_id"), news_item_id=id)[0]['id']
        db.execute("DELETE FROM news_item_likes WHERE id=:id", id=int(liked_id))
    else:  # IF not, add the user like to the DB
        db.execute("INSERT INTO news_item_likes (news_item_id, user_id) VALUES (:news_item_id, :user_id)",
                   news_item_id=id, user_id=session.get("user_id"))

    source = request.form.get("source")

    if source == "index":
        # Redirect user to home page
        return redirect("/")
    else:
        target = "view_" + source
        return redirect(target)


@app.route("/postcomment_<int:id>", methods=["POST"])
@login_required
def postcomment(id):

    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    db.execute("INSERT INTO news_item_comments (comment, news_item_id, user_id, date) VALUES (:comment, :news_item_id, :user_id, :date)",
               comment=request.form.get("comment"), news_item_id=id, user_id=session.get("user_id"), date=formatted_date)
    target = "view_" + str(id)
    return redirect(target)


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


@app.route("/register", methods=["GET", "POST"])
def register():

    # When form is submitted via POST, insert new user ino table
    # Be sure to check for invalid inputs (duplicated user, invalid password confirmation -> display apology), and to hash the user's password.
    if request.method == "POST":
        username = request.form.get("username")
        password_hash = generate_password_hash(request.form.get("password"))
        email = request.form.get("email").lower()
        user_exists = len(db.execute("SELECT * FROM users WHERE username = :username",
                                     username=request.form.get("username"))) > 0

        # Verify format of e-mail
        email_invalid = re.search(r"\A[\w+\-.]+@[a-z\d\-.]+\.[a-z]+\Z", email) is None

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

        # Add email format requirements
        elif email_invalid:
            return apology("E-mail format is invalid.")

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
        db.execute("INSERT INTO users (username, email, hash) VALUES(:username, :email, :hash)",
                   username=username, email=email, hash=password_hash)

        # Redirect user to home page
        return redirect("/")

    # When requested via GET, should display registration form (similar to login html)
    else:
        return render_template("register.html")


@app.route("/admin_update", methods=["GET", "POST"])
@login_required
def admin_update():

    # Check for Admin rights
    if useris_admin():
        # When the form is submited via POST, update the news in the database
        if request.method == "POST":
            # Get current date and format to MYSQL friendly format to attach to new item
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

            # Switching to News API
            # Reference: https://newsapi.org/docs/get-started
            url = ('http://newsapi.org/v2/top-headlines?'
                   'country=us&'
                   'apiKey=aeba79d105db43ee8646c2e0cf60e1a2')
            # fetching data in json format
            request_news = requests.get(url).json()
            # getting all articles in a string article
            articles = request_news["articles"]
            # Request the news from Reddit "news" subreddit.
            # Reference: https://www.reddit.com/dev/api/
            # r = requests.get('https://www.reddit.com/r/news/.json?count=10', headers={'User-agent': 'Chrome'})
            # news = r.json()['data']['children']

            # Save the news to the database
            for news_item in articles:
                url = news_item['url']
                imgurl = news_item['urlToImage']
                author = news_item['author']
                headline = news_item['title']
                description = news_item['description']
                content = news_item['content']
                pubdate = news_item['publishedAt']
                source_url = url.split("www.")[-1].split("//")[-1].split("/")[0]
                source_name = news_item['source']['name']

                # Make sure the news doesn't already exist. Check if the news source is already in sources DB.
                source_exists = len(db.execute("SELECT * FROM sources WHERE url=:url", url=source_url)) > 0
                news_exists = len(db.execute("SELECT * FROM news_items WHERE url=:url", url=url)) > 0

                if not source_exists:  # If source not in "source" DB, add it.
                    db.execute("INSERT INTO sources (name, url) VALUES (:name, :url)", name=source_name, url=source_url)

                if not news_exists:  # If the news doesn't exist to news_item DB, add it.
                    source_id = db.execute("SELECT id FROM sources WHERE url=:url", url=source_url)[0]["id"]
                    db.execute("INSERT INTO news_items (author, headline, description, content, url, imgurl, source_id, publishedat, date) VALUES (:author, :headline, :description, :content, :url, :imgurl, :source_id, :publishedat, :date)",
                               author=author, headline=headline, description=description, content=content, url=url, imgurl=imgurl, source_id=source_id, publishedat=pubdate, date=formatted_date)

            return redirect("/")

        # When requested via GET, should display a form to update the news
        else:
            return render_template("admin_update.html", isadmin=useris_admin())
    else:  # if not admin return permission denied page
        return apology("Permission Denied", 403)


@app.route("/admin_sources", methods=["GET", "POST"])
@login_required
def admin_sources():
    if useris_admin():
        # If user is admin, user can edit the sources properties.
        rows = db.execute("SELECT * FROM sources")
        return render_template("admin_sources.html", rows=rows, isadmin=useris_admin())
    else:
        return apology("Permission Denied", 403)


@app.route("/admin_users", methods=["GET", "POST"])
@login_required
def admin_users():
    if useris_admin():  # If user is admin, can edit all user.
        rows = db.execute("SELECT * FROM users")
        return render_template("admin_users.html", rows=rows, isadmin=useris_admin())
    else:  # If not, can only edit him/herself.
        rows = db.execute("SELECT * FROM users WHERE id=:id ", id=session.get("user_id"))
        return render_template("admin_users.html", rows=rows, isadmin=useris_admin())


@app.route('/addsource', methods=['GET', 'POST'])
@login_required
def addsource():
    if useris_admin():
        # If the user is admin, allow to create a source.
        if request.method == "POST":
            name = request.form.get("name")
            if not name:
                name = None
            url = request.form.get("url")
            if not url:
                url = None
            bias = request.form.get("bias")
            if not bias:
                bias = None
            disabled = request.form.get("disabled")
            if not disabled:
                disabled = 0
            db.execute("INSERT INTO sources (name, url, bias, disabled) VALUES (:name, :url, :bias, :disabled)",
                       name=name, url=url, bias=bias, disabled=disabled)
            return redirect('static/successful.html')
        else:
            return render_template('addsource.html')
    else:
        return apology("Permission Denied", 403)


@app.route('/editsource_<int:id>', methods=['GET', 'POST'])
@login_required
def editsource(id):
    if useris_admin():
        # if User is admin, can edit sources.
        sourcesqry = db.execute("SELECT * FROM sources WHERE id = :id", id=id)
        if not sourcesqry:
            return 'News source ID: #{id} not found'.format(id=id)

        name = sourcesqry[0]["name"]
        url = sourcesqry[0]["url"]
        bias = sourcesqry[0]["bias"]
        disabled = sourcesqry[0]["disabled"]

        if request.method == "POST":
            name_edit = request.form.get("name")
            if not name_edit:
                name_edit = None
            url_edit = request.form.get("url")
            if not url_edit:
                url_edit = None
            bias_edit = request.form.get("bias")
            if not bias_edit:
                bias_edit = None
            disabled_edit = request.form.get("disabled")
            if not disabled_edit:
                disabled_edit = 0
            db.execute("UPDATE sources SET name=:name, url=:url, bias=:bias, disabled=:disabled WHERE id=:id",
                       id=id, name=name_edit, url=url_edit, bias=bias_edit, disabled=disabled_edit)
            return redirect('static/successful.html')
        else:
            return render_template('editsource.html', id=id, name=name, url=url, bias=bias, disabled=disabled)
    else:
        return apology("Permission Denied", 403)


@app.route('/deletesource_<int:id>', methods=['GET', 'POST'])
@login_required
def deletesource(id):
    if useris_admin():
        sourcesqry = db.execute("SELECT * FROM sources WHERE id = :id", id=id)
        if not sourcesqry:
            return 'News source ID: #{id} not found'.format(id=id)

        name = sourcesqry[0]["name"]

        if request.method == "POST":
            db.execute("DELETE FROM sources WHERE id=:id", id=id)
            return redirect('static/successful.html')
        else:
            return render_template('deletesource.html', id=id, name=name)
    else:
        return apology("Permission Denied", 403)


@app.route('/edituser_<int:id>', methods=['GET', 'POST'])
@login_required
def edituser(id):
    if useris_admin():
        sourcesqry = db.execute("SELECT * FROM users WHERE id = :id", id=id)
        if not sourcesqry:
            return 'User ID: #{id} not found'.format(id=id)

        username = sourcesqry[0]["username"]
        email = sourcesqry[0]["email"]
        is_admin = sourcesqry[0]["is_admin"]
        username_exists = len(db.execute("SELECT * FROM users WHERE username = :username AND id!=:id",
                                         username=request.form.get("username"), id=id)) > 0

        if request.method == "POST":
            username_edit = request.form.get("username")
            # Ensure username was submitted
            if not username:
                return apology("must enter username")

            # Ensure username doesn't exist already
            elif (username_exists):
                return apology("Username already exists")

            # Add email format requirements
            elif re.search(r"\A[\w+\-.]+@[a-z\d\-.]+\.[a-z]+\Z", request.form.get("email")) is None:
                return apology("E-mail format is invalid.")

            is_admin_edit = request.form.get("is_admin")
            if not is_admin_edit:
                is_admin_edit = 0
            db.execute("UPDATE users SET username=:username, email=:email, is_admin=:is_admin WHERE id=:id",
                       id=id, username=username_edit, email=request.form.get("email"), is_admin=is_admin_edit)
            return redirect('static/successful.html')
        else:
            return render_template('edituser.html', id=id, username=username, email=email, isadmin=useris_admin())
    else:
        sourcesqry = db.execute("SELECT * FROM users WHERE id = :id", id=session.get("user_id"))
        email = sourcesqry[0]["email"]
        if request.method == "POST":
            if re.search(r"\A[\w+\-.]+@[a-z\d\-.]+\.[a-z]+\Z", request.form.get("email")) is None:
                return apology("E-mail format is invalid.")

            db.execute("UPDATE users SET email=:email WHERE id=:id",
                       id=session.get("user_id"), email=request.form.get("email"))
            return redirect('static/successful.html')
        else:
            return render_template('edituser.html', id=id, email=email)


@app.route('/deleteuser_<int:id>', methods=['GET', 'POST'])
@login_required
def deleteuser(id):
    if useris_admin():
        sourcesqry = db.execute("SELECT * FROM users WHERE id = :id", id=id)
        if not sourcesqry:
            return 'User ID: #{id} not found'.format(id=id)

        username = sourcesqry[0]["username"]

        if request.method == "POST":
            db.execute("DELETE FROM users WHERE id=:id", id=id)
            return redirect('static/successful.html')
        else:
            return render_template('deleteuser.html', id=id, username=username)
    else:
        return apology("Permission Denied", 403)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


def useris_admin():
    if (len(db.execute("SELECT * FROM users WHERE id=:id and is_admin=1", id=session.get("user_id"))) > 0):
        return 1
    else:
        return 0


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)