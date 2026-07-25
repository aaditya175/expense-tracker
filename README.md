# Expense Tracker

A full-stack web app built with **Python (Flask)**, **SQLite**, and **Bootstrap 5**.

## Local Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Visit **http://localhost:5000**

## Features
- Add Income / Expense transactions with type, category, amount, and date
- Server-side + client-side validation
- Live summary dashboard (Total Income, Total Expense, Balance)
- Full transaction history table
- Delete individual transactions
- Fully responsive via Bootstrap 5

## Deploy to Render

1. Push this repo to GitHub (the `.db` file is gitignored — that's intentional).
2. On [render.com](https://render.com) → **New → Web Service** → connect your repo.
3. Render auto-detects `render.yaml`; confirm the settings:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT`
4. Add env var `SECRET_KEY` (any random string, or let Render generate it).
5. Click **Deploy**.

> ⚠️ **SQLite on Render free tier:** Render's free tier uses an ephemeral filesystem,
> meaning `expenses.db` resets on every deploy or restart. This is fine for
> evaluation — the app will still work perfectly during the review session.
> For production you'd swap SQLite for PostgreSQL (Render provides a free managed DB).
