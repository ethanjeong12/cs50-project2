import psycopg2
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL(os.environ.get("DATABASE_URL") or "sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    return apology("YEAH!")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    
        """Buy shares of stock."""
        if request.method=="POST":
            st = (request.form.get("stock")).upper()
            if not st:
                return apology("Enter a symbol")
            nu = int(request.form.get("number"))
            if not nu:
                return apology("Enter shares")
            row = db.execute("SELECT * FROM users WHERE id=:id", id=session['user_id'])
            username = row[0]['username']
            check = lookup(st)
            if not check:
                return apology("Invalid symbol")
            elif nu < 0:
                return apology("Not positive Number")
            pr = lookup(st) ["price"]
            cash = row[0]['cash']
            if cash < nu*pr:
                return apology("Cannot afford")
            
            row1 = db.execute("SELECT * FROM Stocks WHERE symbol=:st AND username=:username",st=st,username=username)
            if not row1:
                db.execute("INSERT INTO Stocks (username,shares,symbol) VALUES (:username,:shares,:symbol)", username=username,shares=nu,symbol=st)
            else: 
                sto = row1[0]['shares']
                sto = sto + nu
                db.execute ("update Stocks set shares=:shares WHERE symbol=:symbol and username=:username" , shares=sto, username=username, symbol=st)
            return redirect(url_for("index"))
        else:
            return render_template("buy.html")
    
    
@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    return apology("TODO")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method=="POST":
        stock = request.form.get("stock")
        info = lookup(stock)
        if (stock== None):
            return apology("Error")
        else: return render_template("quoted.html", quote = info)
    return render_template("quote.html")    
        
            
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method=="POST":
        un = request.form.get("username")
        pwd = request.form.get("password")
        cf = request.form.get("confirm")
        encrypt = pwd_context.hash(pwd)
        if not un:
            return apology("Wrong Username")
        if un and cf:
            if pwd != cf:
                print (pwd) 
                print (cf)
                return apology("Wrong Password")
        else:
            return apology ("Error")
        print (un)
        ran = db.execute("INSERT INTO 'users' (username, hash) VALUES (:username, :encrypt)", username = un, encrypt = encrypt)
        if (ran== None):
            return apology("Error")
        return render_template("index.html")
    else:
        return render_template("register.html")
            

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method=="POST":
        st = (request.form.get("stock")).upper()
        if not st:
            return apology("Enter a symbol")
        nu = int(request.form.get("number"))
        if not nu:
            return apology("Enter shares")
        row = db.execute("SELECT * FROM users WHERE id=:id", id=session['user_id'])
        username = row[0]['username']
        check = lookup(st)
        if not check:
            return apology("Invalid symbol")
        elif nu < 0:
            return apology("Negative Number")
        pr = lookup(st) ["price"]
        cash = row[0]['cash']
        if cash < nu*pr:
            return apology("Cannot sell")
        
        row1 = db.execute("SELECT * FROM Stocks WHERE symbol=:st AND username=:username",st=st,username=username)
        if not row1:
            db.execute("INSERT INTO Stocks (username,shares,symbol) VALUES (:username,:shares,:symbol)", username=username,shares=nu,symbol=st)
        else: 
            sto = row1[0]['shares']
            sto = sto + nu
            db.execute ("update Stocks set shares=:shares WHERE symbol=:symbol and username=:username" , shares=sto, username=username, symbol=st)
        return redirect(url_for("index"))
    else:
        return render_template("sell.html")
        
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
