#!/usr/bin/env python3
"""
Flask version — Relationship Clarity Coaching
Reads .streamlit/secrets.toml for payments, email, and social configs.
"""

from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import tomllib

# -------------------------------------------------------------
#  Flask App Setup
# -------------------------------------------------------------
app = Flask(__name__)

# -------------------------------------------------------------
#  Load secrets.toml (payments / smtp / social)
# -------------------------------------------------------------
SECRETS_PATH = Path(__file__).parent / ".streamlit" / "secrets.toml"
secrets = {}

if SECRETS_PATH.exists():
    try:
        with open(SECRETS_PATH, "rb") as f:
            secrets = tomllib.load(f)
        print("✅ Loaded secrets.toml successfully.")
    except Exception as e:
        print(f"⚠️ Error loading secrets.toml: {e}")
else:
    print("⚠️ No .streamlit/secrets.toml found.")

payments = secrets.get("payments", {})
smtp_conf = secrets.get("smtp", {})
social = secrets.get("social", {})

# -------------------------------------------------------------
#  ROUTES
# -------------------------------------------------------------
@app.route("/")
def index():
    """Render the main landing page (templates/index.html)."""
    return render_template(
        "index.html",
        upi_id=payments.get("upi_id", "your-upi@bank"),
        upi_payee_name=payments.get("upi_payee_name", "Abhijit"),
        amount_inr=payments.get("amount_inr", 500),
        instagram_handle=social.get("instagram_handle", "ask_abhijit"),
    )


@app.route("/book-report", methods=["POST"])
def book_report():
    """Handles the booking form and sends confirmation email."""
    name = request.form.get("name")
    email = request.form.get("email")
    dob = request.form.get("dob")
    gender = request.form.get("gender")
    instagram = request.form.get("instagram")
    message = request.form.get("message")

    print(f"📩 New Booking from {name} ({email}) - Gender: {gender} - IG: {instagram}")

    # ---------------------------------------------------------
    # Send confirmation email (optional)
    # ---------------------------------------------------------
    smtp_host = smtp_conf.get("host")
    smtp_port = int(smtp_conf.get("port", 587))
    smtp_user = smtp_conf.get("user")
    smtp_pass = smtp_conf.get("pass")
    sender = smtp_conf.get("from", smtp_user)

    if smtp_host and smtp_user and smtp_pass and sender and email:
        try:
            msg = MIMEText(
                f"""
Hi {name},

Thank you for booking the Clarity Report (₹{payments.get('amount_inr', 500)}).

I will review your details and send your personalised guidance within 24–48 hours.

Warm regards,
Abhijit
Relationship Clarity Coaching
Instagram: @{social.get('instagram_handle', 'ask_abhijit')}
"""
            )
            msg["Subject"] = "Clarity Report — Booking Confirmed"
            msg["From"] = sender
            msg["To"] = email
            msg["Date"] = formatdate(localtime=True)

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(sender, [email], msg.as_string())

            print(f"✅ Confirmation email sent to {email}")
        except Exception as e:
            print(f"⚠️ Email sending failed: {e}")
    else:
        print("ℹ️ SMTP not configured, skipping email sending.")

    # Redirect back to main page
    return redirect(url_for("index", submitted=True, name=name))


# -------------------------------------------------------------
#  MAIN ENTRY POINT
# -------------------------------------------------------------
if __name__ == "__main__":
    # Run Flask server (http://0.0.0.0:8501)
    app.run(host="0.0.0.0", port=8501)
