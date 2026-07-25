import sqlite3
import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
# Flash messages (like Express req.flash) need a secret key to sign the session cookie
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

DATABASE = "expenses.db"


# --------------------------------------------------------------------------
# Database helpers  (think of these like your Mongoose model layer)
# --------------------------------------------------------------------------

def get_db():
    """Open a connection to the SQLite file.  sqlite3 ≈ MongoClient()."""
    conn = sqlite3.connect(DATABASE)
    # Row objects that behave like dicts  →  like Mongoose document objects
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the table if it doesn't exist yet (runs once on startup)."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                type      TEXT    NOT NULL CHECK(type IN ('Income','Expense')),
                category  TEXT    NOT NULL,
                amount    REAL    NOT NULL CHECK(amount > 0),
                date      TEXT    NOT NULL
            )
        """)
        conn.commit()


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@app.route("/")
def index():
    """Dashboard: summary cards + full transaction history.
       Equivalent to  router.get('/', async (req, res) => { ... })  in Express."""
    db = get_db()

    # Fetch all rows ordered newest-first
    transactions = db.execute(
        "SELECT * FROM transactions ORDER BY date DESC, id DESC"
    ).fetchall()

    # Aggregate totals — SQLite handles this in one query
    summary = db.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN type='Income'  THEN amount ELSE 0 END), 0) AS total_income,
            COALESCE(SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END), 0) AS total_expense
        FROM transactions
    """).fetchone()

    db.close()

    total_income   = summary["total_income"]
    total_expense  = summary["total_expense"]
    balance        = total_income - total_expense

    # render_template  ≈  res.render() in Express + EJS/Handlebars
    return render_template(
        "index.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        today=date.today().isoformat(),   # pre-fill today's date in the form
    )


@app.route("/add", methods=["POST"])
def add_transaction():
    """Handle the Add Transaction form submission.
       Equivalent to  router.post('/add', async (req, res) => { ... })."""
    # request.form  ≈  req.body  (populated by Flask's built-in form parser)
    t_type    = request.form.get("type", "").strip()
    category  = request.form.get("category", "").strip()
    amount_raw = request.form.get("amount", "").strip()
    t_date    = request.form.get("date", "").strip()

    errors = []

    # --- Validation ---
    if t_type not in ("Income", "Expense"):
        errors.append("Please select a valid transaction type.")

    if not category:
        errors.append("Category is required.")

    amount = None
    if not amount_raw:
        errors.append("Amount is required.")
    else:
        try:
            amount = float(amount_raw)
            if amount <= 0:
                errors.append("Amount must be greater than 0.")
        except ValueError:
            errors.append("Amount must be a valid number.")

    if not t_date:
        errors.append("Date is required.")

    if errors:
        # flash()  stores messages in the session for the next request
        # (like connect-flash in Express)
        for err in errors:
            flash(err, "danger")
        return redirect(url_for("index"))

    # --- Persist to SQLite ---
    # Parameterised query (? placeholders) prevents SQL injection — same idea as
    # Mongoose's type coercion / Joi validation keeping bad data out.
    with get_db() as conn:
        conn.execute(
            "INSERT INTO transactions (type, category, amount, date) VALUES (?, ?, ?, ?)",
            (t_type, category, amount, t_date),
        )
        conn.commit()

    flash("Transaction added successfully!", "success")
    return redirect(url_for("index"))


@app.route("/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    """Bonus: delete a transaction by ID."""
    with get_db() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
    flash("Transaction deleted.", "info")
    return redirect(url_for("index"))


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    # On Render, PORT env var is injected automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
