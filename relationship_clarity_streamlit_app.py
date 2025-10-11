#!/usr/bin/env python3
"""
Relationship Clarity Coaching — Streamlit Web App
Deployment-ready version (₹500 update, FAQ replaced)
Author: Abhijit
"""

import streamlit as st
from pathlib import Path
import csv, datetime, smtplib, urllib.parse
from email.mime.text import MIMEText
from email.utils import formatdate


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Relationship Clarity Coaching", page_icon="💙", layout="wide")

PRIMARY = "#1C1C7D"   # Deep Blue
SECONDARY = "#F5E9DA" # Warm Beige
ACCENT = "#C49A6C"    # Gold

# ---------------------------------------------------------
# FONTS + CSS
# ---------------------------------------------------------
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;700&family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --primary:{PRIMARY}; --secondary:{SECONDARY}; --accent:{ACCENT};
}}
html, body, [class*="css"] {{ font-family:'Poppins',sans-serif; }}
h1,h2,h3,.hero-title {{ font-family:'Lora',serif; }}

.hero {{
  background: var(--secondary);
  border-radius: 24px; padding: 64px 48px; margin-bottom: 32px;
  box-shadow:0 20px 50px rgba(28,28,125,0.1);
}}
.section {{ background:white; border-radius:24px; padding:40px; margin-bottom:24px; }}
.beige {{ background:var(--secondary); }}
.cta-btn {{
  background:var(--primary); color:white; padding:14px 30px;
  border-radius:999px; font-weight:700; text-decoration:none;
}}
.card {{
  background:white; border-top:4px solid var(--accent);
  border-radius:20px; padding:24px; box-shadow:0 4px 16px rgba(0,0,0,0.08);
}}
.testimonial {{
  border-radius:20px; padding:20px; box-shadow:0 4px 20px rgba(0,0,0,0.1);
}}
.footer {{ text-align:center; color:#444; font-size:13px; opacity:0.8; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

def get_secret_section(name: str) -> dict:
    try:
        return dict(st.secrets.get(name, {}))
    except Exception:
        return {}


# ---------------------------------------------------------
# HERO SECTION (with banner background)
# ---------------------------------------------------------
hero_image = "images/hero/hero.PNG"
if not Path(hero_image).exists():
    hero_image = "https://placehold.co/1200x500/1C1C7D/C49A6C?text=Upload+hero.PNG+in+/images/hero"

st.markdown(f"""
<div class="hero"
     style="
        background: url('{hero_image}') center/cover no-repeat;
        color: white;
        position: relative;
        border-radius: 24px;
        padding: 100px 60px;
        margin-bottom: 40px;
        box-shadow: 0 20px 50px rgba(28,28,125,0.3);
     ">
  <div style="background:rgba(28,28,125,0.55);padding:40px;border-radius:20px;max-width:700px;">
    <h1 class="hero-title" style="font-size:52px;line-height:1.2;color:white;">
      Get <b>Clarity in Love</b>, Heal Patterns, Move Forward.
    </h1>
    <p style="font-size:20px;margin-top:16px;color:#f5f5f5;">
      Personalised guidance Report by Abhijit. Stop guessing. Start healing.
    </p>
    <a href="#book" class="cta-btn"
       style="display:inline-block;margin-top:24px;background:var(--accent);color:var(--primary);">
       Book your Clarity Report — ₹500
    </a>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# BOOKING FORM SECTION
# ---------------------------------------------------------
st.markdown('<a name="book"></a>', unsafe_allow_html=True)
st.markdown("<div class='section beige'><h2>Book Your Clarity Report</h2>", unsafe_allow_html=True)

with st.form("booking_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", placeholder="Your full name")
        email = st.text_input("Email Address (Report will be delivered here)")
        dob = st.date_input("Date of Birth (Optional)", value=None, min_value=datetime.date(1900,1,1))
    with col2:
        gender = st.selectbox("Gender", ["Select...", "Female", "Male", "Other"])
        instagram = st.text_input("Your Instagram Handle (for follow-up questions)", placeholder="@ask_abhijit")
        message = st.text_area("Explain Your Issue (Open up completely...)", height=140)
    submitted = st.form_submit_button("Unlock My Clarity Report", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SUBMISSION LOGIC + EMAIL CONFIRMATION
# ---------------------------------------------------------
if submitted:
    if not name or not email:
        st.error("Name and Email are required.")
    else:
        csv_file = DATA_DIR / "bookings.csv"
        new_row = [datetime.datetime.now().isoformat(), name, str(dob), gender, email, instagram, message]
        header = ["timestamp","name","dob","gender","email","instagram","message"]
        write_header = not csv_file.exists()
        with open(csv_file, "a", newline='', encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header: w.writerow(header)
            w.writerow(new_row)

        st.success(f"✅ Thank you, {name}! Your details are successfully submitted.")
        st.info("You’ll be redirected to the payment page (₹500). A confirmation email will follow after payment.")

        pay_conf = get_secret_section("payments")
        upi_id = pay_conf.get("upi_id", "your-upi@bank")
        upi_payee = pay_conf.get("upi_payee_name", "Abhijit")
        amount = pay_conf.get("amount_inr", 500)
        txn_note = "ClarityReport"
        upi_link = f"upi://pay?pa={upi_id}&pn={upi_payee}&am={amount}&cu=INR&tn={txn_note}"
        st.link_button("Pay via UPI", upi_link, width="stretch")

        stripe_link = pay_conf.get("stripe_checkout_url", "")
        razor_link = pay_conf.get("razorpay_checkout_url", "")
        paypal_link = pay_conf.get("paypal_link", "")
        cols = st.columns(3)
        if stripe_link: cols[0].link_button("Pay with Stripe", stripe_link, width="stretch")
        if razor_link:  cols[1].link_button("Pay with Razorpay", razor_link, width="stretch")
        if paypal_link: cols[2].link_button("Pay with PayPal", paypal_link, width="stretch")

        st.divider()
        st.markdown("#### After Payment")
        paid = st.checkbox("I have completed the payment")
        if paid:
            smtp_conf = get_secret_section("smtp")
            smtp_host = smtp_conf.get("host")
            smtp_port = int(smtp_conf.get("port", 587))
            smtp_user = smtp_conf.get("user")
            smtp_pass = smtp_conf.get("pass")
            sender = smtp_conf.get("from", smtp_user)

            confirmation_msg = f"""
Hi {name},

Thank you for booking the Clarity Report (₹500).

I will review your details and send your personalised guidance report within 24-48 hours.
You may reach out on Instagram DM for clarifications (@ask_abhijit).

— Abhijit
Relationship Clarity Coaching
"""

            sent_ok = False
            if smtp_host and smtp_user and smtp_pass and sender:
                try:
                    msg = MIMEText(confirmation_msg)
                    msg["Subject"] = "Clarity Report — Booking Confirmed"
                    msg["From"] = sender
                    msg["To"] = email
                    msg["Date"] = formatdate(localtime=True)
                    with smtplib.SMTP(smtp_host, smtp_port) as s:
                        s.starttls()
                        s.login(smtp_user, smtp_pass)
                        s.sendmail(sender, [email], msg.as_string())
                    sent_ok = True
                except Exception as e:
                    st.warning(f"Email not sent: {e}")

            if sent_ok:
                st.success("📧 Confirmation email sent.")
            else:
                st.info("Email sending skipped or misconfigured (check secrets.toml).")

            wa_text = f"Hi Abhijit, I paid for the Clarity Report. Name: {name}."
            st.link_button("Send WhatsApp Confirmation", f"https://wa.me/919876543210?text={urllib.parse.quote_plus(wa_text)}", width="stretch")


# ---------------------------------------------------------
# WHAT YOU’LL GET SECTION
# ---------------------------------------------------------
st.markdown("<div class='section'><h2>What's Inside Your Personal Clarity Report?</h2>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("<div class='card'><b>Core Clarity</b><br>A precise breakdown of your fundamental issues and what’s really happening in your relationship dynamic.</div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='card'><b>Risk & Pattern Identification</b><br>Identify recurring toxic patterns or self-sabotage affecting your well-being.</div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='card'><b>Actionable Roadmap</b><br>Personal suggestions and a clear roadmap to move forward with confidence.</div>", unsafe_allow_html=True)
st.link_button("Book your Clarity Report now", "#book", width="stretch")
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# TESTIMONIALS
# ---------------------------------------------------------
st.markdown("<div class='section beige'><h2>Real Transformations. Real Clarity.</h2>", unsafe_allow_html=True)
t1, t2, t3 = st.columns(3)
with t1:
    st.markdown("<div class='testimonial' style='background:var(--primary);color:white;'><b>Saved me literally. I'm all good now.</b><br><i>“I used to have breakdowns, but your guidance brought me back stronger.”</i><br><small>— Client (WhatsApp)</small></div>", unsafe_allow_html=True)
with t2:
    st.markdown("<div class='testimonial' style='background:var(--secondary);'><b>Harsh truth said gently.</b><br><i>“You told me the truth in a gentle way that helped me let go and heal.”</i><br><small>— Client (Instagram DM)</small></div>", unsafe_allow_html=True)
with t3:
    st.markdown("<div class='testimonial' style='background:var(--primary);color:white;'><b>My healing started.</b><br><i>“I saw my worth clearly and began focusing on myself again.”</i><br><small>— Client (WhatsApp)</small></div>", unsafe_allow_html=True)
st.caption("All real messages from clients. See more on Instagram highlights [@ask_abhijit](https://instagram.com/ask_abhijit).")
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# ABOUT ME (with image)
# ---------------------------------------------------------
st.markdown("<div class='section' style='background:var(--primary);color:white;'>", unsafe_allow_html=True)
c1, c2 = st.columns([1,2])
about_img = Path("images/aboutme/client1.PNG")
with c1:
    if about_img.exists():
        st.image(str(about_img), caption="Abhijit", use_container_width=True)
    else:
        st.info("Add your photo at images/aboutme/client1.PNG to display it here.")
with c2:
    st.markdown("""
    <h2 style='color:var(--accent);'>Why I Do This: My Promise of Clarity.</h2>
    <p>I’ve seen firsthand how painful it is when love feels one-sided or when the same heartbreak repeats again and again.
    People came to me for guidance, and I realised I could help them cut through confusion and find honest clarity.</p>
    <p>Today, I offer private 1:1 Clarity Guidance that is simple, personal, and practical. Let's stop the cycle of confusion together.</p>
    <a href='#book' class='cta-btn' style='background:white;color:var(--primary);'>Start Your Session</a>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# FAQ SECTION (UPDATED TEXT)
# ---------------------------------------------------------
st.markdown("<div class='section beige'><h2>Your Questions, Answered</h2>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size:17px;color:#333;line-height:1.6;'>
I will deeply study your situation and send you a personalized guide on what’s happening, your patterns, and next steps.<br><br>
It will be a detailed written guide prepared personally for you —<br><br>
It explains the root of your issue, what’s blocking you, and how to move forward with emotional balance and clarity.
</p>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# FINAL CTA + FOOTER
# ---------------------------------------------------------
st.markdown(f"""
<div class='section beige' style='text-align:center;'>
  <h2 style='color:var(--primary);'>Ready to Stop Guessing and Start Healing?</h2>
  <p style='color:#333;'>Get the focused, unbiased clarity you need to move forward with confidence.</p>
  <a href="#book" class="cta-btn" style="background:var(--accent);color:var(--primary);">Book Your Report Now — ₹500</a>
</div>
<div class='footer'>
  © {datetime.datetime.now().year} Abhijit | Relationship Clarity Coaching.<br>
  All sessions and reports are strictly confidential.
</div>
""", unsafe_allow_html=True)
