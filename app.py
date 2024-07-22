import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Query for user's cash balance
    rows = db. execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = rows[0]["cash"]

    # Query for user's stocks
    stocks = db.execute("SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])

    # list to hold stock data
    portfolio = []
    total_value = 0

    for stock in stocks:
        stock_info = lookup(stock["symbol"])
        if stock_info:
            current_price = stock_info["price"]
            total_stock_value = stock["shares"]*current_price
            total_value += total_stock_value
            portfolio.append({"symbol": stock["symbol"],"shares": stock["shares"],"price": usd(current_price),"total": usd(total_stock_value)})
        else:
            return apology("invalid symbol", 403)

    # Calculate the grand total (cash+total vale of stocks)
    grand_total = cash + total_value

    return render_template("index.html", cash=usd(cash), portfolio=portfolio, grand_total=usd(grand_total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")

        # Ensure symbol was submitted
        if not symbol:
            return apology("must provide symbol", 403)

        # Ensure shares was submitted and is a positive integer
        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("must provide a positive number of shares", 403)

        shares = int(shares)

        # Look up the stock price
        stock = lookup(symbol)
        if not stock:
            return apology("invalid symbol", 403)

        # Calculate the total cost
        total_cost = shares * stock["price"]

        # Query databse for user's cash
        rows = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash = rows[0]["cash"]

        # Ensure the suer can afford the purchase
        if cash < total_cost:
            return apology("can't afford", 403)

        # Update the user's cash
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, session["user_id"])

        # Record the transactions
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                    session["user_id"], symbol, shares, stock["price"])

        # Redirect to home page
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Query for all transactions of the user
    transactions = db.execute("SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", session["user_id"])

    # Format the transactions
    for transaction in transactions:
        transaction["price"] = usd(transaction["price"])
        if transaction["shares"] > 0:
            transaction["type"] = "BUY"
        else:
            transaction["type"] = "SELL"
        transaction["shares"] = abs(transaction["shares"])

    return render_template("history.html", transactions=transactions)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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
    """Get stock quote."""
    # Submitting the user's input via quote
    if request.method == "POST":
        # Getting the symbol of the stock from the form
        symbol = request.form.get("symbol")

        # Ensure symbol was submitted
        if not symbol:
            return apology("must provide symbol", 403)

        # If submitted, lookup for the stock with that symbol
        stock = lookup(symbol)

        # Ensure stock symbol is valid
        if not stock:
            return apology("invlaid symbol", 403)

        # Render quoted template with providede stock info
        return render_template("quoted.html", stock=stock)

    # User reached route via GET
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # Ensure username was submitted
        elif not confirmation:
            return apology("must confirm password", 403)

        # Ensure both passwords match
        elif password != confirmation:
            return apology("passwords do not match", 403)

        # Hash the password
        hash = generate_password_hash(password)

        # Insert the new user into users
        try:
            new_user_id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except ValueError:
            return apology("username already exists", 403)

        # Remember which user has logged in
        session["user_id"] = new_user_id

        ## Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Ensure symbol was submitted
        if not symbol:
            return apology("must provide symbol", 403)

        # Ensure shares was submitted and is a positive integer
        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("must provide a positive number of shares", 403)

        shares = int(shares)

        # Query for user's current shares of the stock
        rows = db.execute("SELECT SUM(shares) as shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", session["user_id"], symbol)
        if len(rows) != 1 or rows[0]["shares"] < shares:
            return apology("too many shares", 403)

        # Look up the current stock price
        stock = lookup(symbol)
        if not stock:
            return apology("invalid symbol", 403)

        # Calculate the total sale value
        sale_value = shares * stock["price"]

        # Update the user's cash balance
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", sale_value, session["user_id"])

        # Record the sale transaction
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)", session["user_id"], symbol, -shares, stock["price"])

        # Redirect to home page
        return redirect("/")

    else:
        # Query for the user's current holdings
        holdings = db.execute("SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])
        return render_template("sell.html", holdings=holdings)


@app.route("/watchlist", methods=["GET", "POST"])
@login_required
def watchlist():
    """Show and Manage Watchlist"""
    if request.method == "POST":
        # Adding a new stock to the watchlist
        symbol = request.form.get("symbol").upper()

        # Ensure symbol was submitted
        if not symbol:
            return apology("must provide symbol", 403)

        # Look up the stock to validate symbol
        stock = lookup(symbol)
        if not stock:
            return apology("invalid symbol", 403)

        # Add the stock to the watchlist
        db.execute("INSERT INTO watchlist (user_id, symbol) VALUES (?, ?)", session["user_id"], symbol)

        # Redirect to the watchlist page
        return redirect("/watchlist")

    else:
        # Query for user's watchlist
        watchlist = db.execute("SELECT symbol, timestamp FROM watchlist WHERE user_id = ? ORDER BY timestamp DESC", session["user_id"])

        # Fetch current prices for the stocks in the watchlist
        for stock in watchlist:
            stock_info = lookup(stock["symbol"])
            if stock_info:
                stock["price"] = usd(stock_info["price"])
            else:
                stock["price"] = "N/A"
                
        return render_template("watchlist.html", watchlist=watchlist)


@app.route("/watchlist/remove", methods=["POST"])
@login_required
def remove_from_watchlist():
    """Remove a stock from the watchlist"""
    symbol = request.form.get("symbol").upper()

    # Ensure symbol was submitted
    if not symbol:
        return apology("must provide symbol", 403)

    # Remove the stock from the watchlist
    db.execute("DELETE FROM watchlist WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)

    # Redirect to the watchlist page
    return redirect("/watchlist")




