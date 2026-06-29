import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import os
import base64
import datetime

st.set_page_config(page_title="AI Marketing Agent", page_icon="🤖", layout="wide")

DB_NAME = "social_media_users.db"

def set_bg(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.72), rgba(0,0,0,0.72)),
        url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stSidebar"] {{
        background: rgba(10,10,15,0.92);
    }}

    .block-container {{
        padding-top: 3rem;
    }}

    .login-card {{
        max-width: 520px;
        margin: auto;
        margin-top: 40px;
        padding: 45px 38px;
        border-radius: 28px;
        background: rgba(20, 22, 28, 0.86);
        box-shadow: 0 0 40px rgba(40, 90, 255, 0.35);
        border: 1px solid rgba(70, 120, 255, 0.4);
        text-align: center;
    }}

    .login-title {{
        font-size: 44px;
        font-weight: 700;
        color: white;
        margin-bottom: 10px;
    }}

    .login-subtitle {{
        color: #b8beca;
        font-size: 15px;
        margin-bottom: 25px;
    }}

    div.stButton > button {{
        width: 100%;
        height: 48px;
        border-radius: 30px;
        border: none;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: white;
        font-size: 16px;
        font-weight: 600;
    }}

    div.stTextInput > div > div > input {{
        background-color: rgba(15, 18, 25, 0.95);
        color: white;
        border-radius: 25px;
        border: 1px solid rgba(80, 130, 255, 0.5);
        padding: 12px;
    }}

    h1, h2, h3, p, label, div {{
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg("images/background.jpg")

def create_user_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup_user(name, email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO users(name,email,password,created_at)
        VALUES(?,?,?,?)
        """, (name, email, hash_password(password), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def login_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT user_id, name, email, created_at FROM users
    WHERE email=? AND password=?
    """, (email, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

create_user_table()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

def auth_page():
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>Log in</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='login-subtitle'>Log in to your account and continue managing your marketing dashboard.</div>",
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab1:
        email = st.text_input("Enter your email address", key="login_email")
        password = st.text_input("Enter your password", type="password", key="login_password")

        if st.button("Log in"):
            user = login_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = {
                    "user_id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "created_at": user[3]
                }
                st.success("Login Successful ✅")
                st.rerun()
            else:
                st.error("Invalid Email or Password ❌")

    with tab2:
        name = st.text_input("Enter full name")
        email = st.text_input("Enter email address", key="signup_email")
        password = st.text_input("Create password", type="password", key="signup_password")

        if st.button("Sign up"):
            if signup_user(name, email, password):
                st.success("Account Created ✅ Please Login")
            else:
                st.error("Email already exists ❌")

    st.markdown("</div>", unsafe_allow_html=True)

def dashboard():
    user = st.session_state.user

    st.sidebar.title("🤖 AI Marketing Agent")
    st.sidebar.success(f"Welcome, {user['name']}")

    menu = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "📊 Analytics", "✍️ AI Content", "📝 Reports", "🤖 AI Insights"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    df = pd.read_csv("data/social_media_data.csv")
    df["Engagement"] = df["Likes"] + df["Comments"] + df["Shares"]

    st.title("🚀 AI Marketing Agent Dashboard")

    if menu == "🏠 Dashboard":
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📈 Likes", df["Likes"].sum())
        col2.metric("💬 Comments", df["Comments"].sum())
        col3.metric("🔄 Shares", df["Shares"].sum())
        col4.metric("🔥 Engagement", df["Engagement"].sum())

        st.dataframe(df, use_container_width=True)

    elif menu == "📊 Analytics":
        st.subheader("Platform-wise Engagement")
        st.bar_chart(df.groupby("Platform")["Engagement"].sum())

        st.subheader("Post-wise Engagement")
        st.bar_chart(df.set_index("Post")["Engagement"])

    elif menu == "✍️ AI Content":
        topic = st.text_input("Enter Topic/Product")
        platform = st.selectbox("Select Platform", ["Instagram", "Facebook", "LinkedIn", "X"])

        if st.button("Generate Content"):
            st.success(f"""
🚀 Introducing **{topic}**

Grow smarter with **{topic}**.  
Perfect for **{platform}** marketing.

#Marketing #Growth #SocialMedia
""")

    elif menu == "📝 Reports":
        top_post = df.loc[df["Engagement"].idxmax()]
        st.success(f"Top Post: {top_post['Post']}")
        st.info(f"Platform: {top_post['Platform']}")
        st.warning(f"Engagement: {top_post['Engagement']}")

    elif menu == "🤖 AI Insights":
        top_post = df.loc[df["Engagement"].idxmax()]
        st.info(f"Create more content similar to **{top_post['Post']}**.")

if st.session_state.logged_in:
    dashboard()
else:
    auth_page()