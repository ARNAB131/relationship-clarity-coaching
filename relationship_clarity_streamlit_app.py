import streamlit as st
from pathlib import Path
import csv
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import datetime
import urllib.parse

# -----------------------------
# Branding and Global Config
# -----------------------------
st.set_page_config(page_title="Relationship Clarity Coaching", page_icon="💙", layout="wide")

PRIMARY = "#1C1C7D"   # Deep Blue
ALT_PRIMARY = "#7D1C3A"  # Wine Red (optional toggle later)
SECONDARY = "#F5E9DA" # Warm Beige
ACCENT = "#C49A6C"    # Gold

# Load Google Fonts and custom CSS (Roboto for body, Merriweather for headings)
st.markdown(
    f"""
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Merriweather:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: {PRIMARY};
            --secondary: {SECONDARY};
            --accent: {ACCENT};
        }}
        html, body, [class*="css"]  {{ font-family: 'Roboto', sans-serif; }}
        h1, h2, h3, .hero-title {{ font-family: 'Merriweather', serif; }}
        .hero {{
            background: linear-gradient(135deg, rgba(28,28,125,0.9), rgba(196,154,108,0.85)), url('https://images.unsplash.com/photo-1520975922071-a569c2b21cf2?q=80&w=1950&auto=format&fit=crop');
            background-size: cover; background-position: center; color: white;
            border-radius: 24px; padding: 64px 48px; margin-bottom: 24px;
        }}
        .cta-btn {{
            background: var(--accent); color: #111; padding: 14px 22px; border-radius: 999px;
            text-decoration: none; font-weight: 700; border: none; cursor: pointer;
        }}
        .outline-btn {{
            background: transparent; color: white; border: 2px solid white; padding: 12px 20px; border-radius: 999px;
            font-weight: 600; cursor: pointer;
        }}
        .section {{ background: white; border-radius: 24px; padding: 28px; margin-bottom: 18px; }}
        .beige {{ background: var(--secondary); }}
        .gold-text {{ color: var(--accent); }}
        .footer {{ color: #333; font-size: 14px; padding: 12px 0; }}
        .small {{ font-size: 13px; opacity: 0.8; }}
        .pill {{ display:inline-block; background:var(--secondary); color:#111; padding:6px 12px; border-radius:999px; font-size:12px; margin-right:6px; }}
        .testimonial-card {{ background: #fff; border: 1px solid rgba(0,0,0,0.06); border-radius: 20px; padding: 16px; height: 100%; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def load_images(folder: Path, patterns=("*.png", "*.jpg", "*.jpeg", "*.webp", "*.PNG", "*.JPG", "*.JPEG", "*.WEBP", "*.PMG")):
    files = []
    for pat in patterns:
        files.extend(sorted(folder.glob(pat)))
    return files

def get_secrets_section(name: str) -> dict:
    """Return a secrets section or {} if secrets.toml is missing."""
    try:
        return dict(st.secrets.get(name, {}))
    except Exception:
        return {}

# Paths for local assets relative to repo
ROOT = Path(__file__).parent
FEEDBACK_DIR = ROOT / "images" / "feedback"
ABOUTME_DIR = ROOT / "images" / "aboutme"

FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
ABOUTME_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Hero Section
# -----------------------------
with st.container():
    st.markdown(
        """
        <div class="hero">
            <div class="pill">Private 1:1 Guidance</div>
            <h1 class="hero-title" style="font-size:48px; margin: 8px 0 4px;">Get Clarity in Love, Heal Patterns, Move Forward.</h1>
            <p style="font-size:18px; margin: 0 0 20px;">Personalised guidance Report by Abhijit.</p>
            <div style="display:flex; gap:12px; align-items:center;">
                <a href="#book" class="cta-btn">Book your clarity Report — ₹299</a>
                <a href="#what" class="outline-btn">What you’ll get</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Booking Form Section
# -----------------------------
st.markdown('<a name="book"></a>', unsafe_allow_html=True)
st.markdown("<div class='section beige'><h2>Book Your Clarity Report</h2>", unsafe_allow_html=True)

with st.form("booking_form"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        name = st.text_input("Name")
        dob = st.date_input(
            "Date of Birth",
            value=None,
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
            format="DD/MM/YYYY"
        )
        gender = st.selectbox("Gender", ["Prefer not to say", "Female", "Male", "Other"])
    with col2:
        email = st.text_input("Email")
        whatsapp = st.text_input("WhatsApp Number", placeholder="with country code e.g. +91XXXXXXXXXX")
    with col3:
        issue = st.text_area("Describe your issue", height=120)
    st.caption("You will be redirected to payment after submitting. Price: ₹299.")
    submitted = st.form_submit_button("Proceed to Payment", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Handle submission
# -----------------------------
if submitted:
    if not name or not email:
        st.error("Name and Email are required.")
    else:
        data_dir = ROOT / "data"
        data_dir.mkdir(exist_ok=True)
        csv_file = data_dir / "bookings.csv"
        new_row = [datetime.datetime.now().isoformat(), name, str(dob) if dob else "", gender, email, whatsapp, issue]
        header = ["ts", "name", "dob", "gender", "email", "whatsapp", "issue"]
        write_header = not csv_file.exists()
        with open(csv_file, "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(header)
            writer.writerow(new_row)

        st.success("Details captured. Choose a payment option below.")

        st.markdown("### Payment")
        st.write("Select one option:")

        payments = get_secrets_section("payments")
        upi_id = payments.get("upi_id", "your-upi@bank")
        upi_payee_name = payments.get("upi_payee_name", "Abhijit")
        amount = payments.get("amount_inr", 299)
        transaction_note = "ClarityReport"
        upi_link = f"upi://pay?pa={upi_id}&pn={upi_payee_name}&am={amount}&cu=INR&tn={transaction_note}"
        st.link_button("Pay via UPI", upi_link, use_container_width=True)

        stripe_link = payments.get("stripe_checkout_url", "")
        razorpay_link = payments.get("razorpay_checkout_url", "")
        paypal_link = payments.get("paypal_link", "")

        cols_pay = st.columns(3)
        with cols_pay[0]:
            if stripe_link:
                st.link_button("Pay with Stripe", stripe_link, use_container_width=True)
        with cols_pay[1]:
            if razorpay_link:
                st.link_button("Pay with Razorpay", razorpay_link, use_container_width=True)
        with cols_pay[2]:
            if paypal_link:
                st.link_button("Pay with PayPal", paypal_link, use_container_width=True)

        st.divider()
        st.markdown("#### After Payment")
        paid = st.checkbox("I have completed the payment")
        if paid:
            smtp_conf = get_secrets_section("smtp")
            smtp_host = smtp_conf.get("host")
            smtp_port = int(smtp_conf.get("port", 587)) if smtp_conf.get("port") else 587
            smtp_user = smtp_conf.get("user")
            smtp_pass = smtp_conf.get("pass")
            sender = smtp_conf.get("from", smtp_user)

            confirmation_msg = f"""
Hi {name},

Thank you for booking the Clarity Report. I will review your details and send your personalised guidance on WhatsApp/Email.

— Abhijit
"""

            sent_ok = False
            if smtp_host and smtp_user and smtp_pass and sender:
                try:
                    msg = MIMEText(confirmation_msg)
                    msg["Subject"] = "Clarity Report — Booking Confirmed"
                    msg["From"] = sender
                    msg["To"] = email
                    msg["Date"] = formatdate(localtime=True)

                    with smtplib.SMTP(smtp_host, smtp_port) as server:
                        server.starttls()
                        server.login(smtp_user, smtp_pass)
                        server.sendmail(sender, [email], msg.as_string())
                    sent_ok = True
                except Exception as e:
                    st.warning(f"Email not sent: {e}")

            if sent_ok:
                st.success("Confirmation email sent.")
            else:
                st.info("Confirmation step recorded. Email sending is optional and needs SMTP secrets.")

            if whatsapp:
                wa_text = f"Hi Abhijit, I paid for the Clarity Report. Name: {name}."
                wa_encoded = urllib.parse.quote_plus(wa_text)
                wa_number = whatsapp.replace("+", "").replace(" ", "")
                wa_link = f"https://wa.me/{wa_number}?text={wa_encoded}"
                st.link_button("Send WhatsApp confirmation", wa_link, use_container_width=True)

# -----------------------------
# What You’ll Get Section
# -----------------------------
st.markdown('<a name="what"></a>', unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='section'><h2>What You’ll Get</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        - You will get clarity of your core issues, what exactly happening.
        - What are the risks, and my personal Suggestions for you to move forward.
        """
    )
    st.link_button("Book your clarity Report now", "#book")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Client Proof / Testimonials
# -----------------------------
with st.container():
    st.markdown("<div class='section beige'><h2>Client Proof / Testimonials</h2>", unsafe_allow_html=True)

    images = load_images(FEEDBACK_DIR)
    if not images:
        st.info("Place your testimonial screenshots in images/feedback as feedback1.PNG ... feedback10.PNG")
    else:
        if "t_index" not in st.session_state:
            st.session_state.t_index = 0
        cols = st.columns([1, 2, 1])
        with cols[0]:
            if st.button("◀ Prev"):
                st.session_state.t_index = (st.session_state.t_index - 1) % len(images)
        with cols[1]:
            st.image(
                str(images[st.session_state.t_index]),
                use_container_width=True,
                caption="All real messages from clients. See more on Instagram highlights @yourhandle."
            )
        with cols[2]:
            if st.button("Next ▶"):
                st.session_state.t_index = (st.session_state.t_index + 1) % len(images)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='testimonial-card'><strong>Felt peace after years of pain.</strong></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='testimonial-card'><strong>He finally chose me after your guidance.</strong></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='testimonial-card'><strong>Could move on in 2 days, not 2 years.</strong></div>", unsafe_allow_html=True)

    st.caption("All real messages from clients. See more on my Instagram highlights @yourhandle.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# About Me Section
# -----------------------------
with st.container():
    st.markdown("<div class='section'><h2>About Me — Why I Do This</h2>", unsafe_allow_html=True)

    cols = st.columns([1, 2])
    with cols[0]:
        about_images = load_images(ABOUTME_DIR)
        fallback1 = ABOUTME_DIR / "client1.PMG"
        fallback2 = ABOUTME_DIR / "client1.PNG"
        if fallback1.exists():
            about_images = [fallback1]
        elif fallback2.exists():
            about_images = [fallback2]
        if about_images:
            st.image(str(about_images[0]), caption="Abhijit", use_container_width=True)
        else:
            st.info("Add your photo to images/aboutme/client1.PNG or client1.PMG")

    with cols[1]:
        st.write(
            "I’ve seen how painful it is when love feels one-sided, or when the same heartbreak repeats again and again. "
            "People started coming to me for guidance, and I realised I could help them find the clarity they needed. "
            "Today, I offer private 1:1 clarity Guidance — simple, personal, and practical."
        )
        st.link_button("Start Your Session", "#book")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# FAQ Section
# -----------------------------
with st.container():
    st.markdown("<div class='section beige'><h2>FAQ</h2>", unsafe_allow_html=True)
    with st.expander("Is this free or paid?"):
        st.write("Small supportive replies are free, full guidance is paid.")
    with st.expander("How will I receive my guidance?"):
        st.write("Over WhatsApp or Instagram DM in chat / PDF format.")
    with st.expander("Can I trust you?"):
        st.write("Yes, I have many real reviews visible on Instagram highlights.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Final CTA
# -----------------------------
with st.container():
    st.markdown("<div class='section'><h2>Ready for Clarity in Love?</h2>", unsafe_allow_html=True)
    st.link_button("Book Your Report Now", "#book")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Footer with social links and Instagram embed placeholder
# -----------------------------
with st.container():
    st.markdown("<div class='section beige'>", unsafe_allow_html=True)
    colA, colB = st.columns([2, 1])
    with colA:
        st.write("Follow on Instagram: ")
        social = get_secrets_section("social")
        ig_handle = social.get("instagram_handle", "Instagram.com/ask_abhijit")
        st.markdown(f"[@{ig_handle}](https://instagram.com/{ask_abhijit})")
        st.write("Privacy & Confidentiality: Your details are kept confidential and never shared.")
    with colB:
        st.write("Instagram Feed Preview")
        ig_embed_username = social.get("ask_abhijit", "")
        if ig_embed_username:
            st.components.v1.html(
                f"""
                <blockquote class="instagram-media" data-instgrm-permalink="https://www.instagram.com/{ig_embed_username}/" data-instgrm-version="14"></blockquote>
                <script async src="https://www.instagram.com/embed.js"></script>
                """,
                height=300,
            )
        else:
            st.caption("Add 'social.instagram_embed_username' in secrets to show an embed.")
    st.markdown("<div class='footer small'>© {}</div>".format(datetime.datetime.now().year), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Notes for deployment (visible in app if needed)
# -----------------------------
with st.expander("Admin Notes: Setup & Secrets"):
    st.markdown(
        """
        **Paths**
        - Place testimonial images in `images/feedback/feedback1.PNG ... feedback10.PNG`.
        - Place your photo in `images/aboutme/client1.PNG` or `client1.PMG`.

        **Optional Secrets (add in `.streamlit/secrets.toml`)**

        ```toml
        [payments]
        upi_id = "your-upi@bank"
        upi_payee_name = "Abhijit"
        amount_inr = 299
        stripe_checkout_url = "https://buy.stripe.com/..."  # optional
        razorpay_checkout_url = "https://pages.razorpay.com/..."  # optional
        paypal_link = "https://paypal.me/yourid/3.99"  # optional

        [smtp]
        host = "smtp.gmail.com"
        port = 587
        user = "youremail@example.com"
        pass = "app_password"
        from = "youremail@example.com"

        [social]
        instagram_handle = "yourhandle"
        instagram_embed_username = "p/POST_ID"  # optional embed permalink slug
        ```

        **Deploy**
        - Run locally: `streamlit run relationship_clarity_streamlit_app.py`
        - Streamlit Cloud: push repo, set secrets, then deploy.
        """
    )
