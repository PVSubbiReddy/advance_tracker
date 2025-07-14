import streamlit as st
import requests
import os
import base64
import time
from utils import load_credentials
from streamlit_lottie import st_lottie

def load_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

image_path = os.path.join("images", "lf_logo.png")
base64_image = load_base64_image(image_path)

def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "role" not in st.session_state:
        st.session_state.role = None
    if "has_admin_access" not in st.session_state:
        st.session_state.has_admin_access = False
    if "empid" not in st.session_state:
        st.session_state.empid = None
    if "login_tries" not in st.session_state:
        st.session_state.login_tries = 3
    if "session_time" not in st.session_state:
        st.session_state.session_time = 0


def load_lottie_url(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
@st.dialog("Cast your vote")
def vote():
    st.markdown(f"<h3>Welcome back {st.session_state.username}</h3><br>", unsafe_allow_html=True)

def login():
    st.markdown("""
        <style>
        .login-card {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
            max-width: 350px;
            margin: auto;
        }
        .separator {
            border-left: 2px solid #e0e0e0;
            height: 100%;
            margin: 0 1rem;
        }
        .login-form-box {
            background-color: #ffffff;
            padding: 0rem;
            border-radius: 18px 6px 25px 6px;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
            text-align: center;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    left_col, sep_col, right_col, idle = st.columns([0.7, 0.1, 0.9, 0.1])

    with left_col:
        lottie_url = "https://lottie.host/40b1e1de-bc4a-4994-879d-42b115d2f84f/b6tjHNSyHR.json"
        lottie_animation = load_lottie_url(lottie_url)
        if lottie_animation:
            st_lottie(lottie_animation, speed=1, width=500, height=550, key="login_animation")
        else:
            st.error("Failed to load animation. Check URL.")

    with sep_col:
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
    base64_image1 = None #just remove 1 in the below url
    with right_col:
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        st.markdown(f"""<div class='login-form-box'>
            <h1>
                <img src="data:image/png;base64,{base64_image1}" style="width:95px; vertical-align:middle; margin-right:0px;"><span style="color:orange;">
                Advance Management Portal</span>
            </h1> """, unsafe_allow_html=True)

        username = st.text_input("**Username**", placeholder="Enter your username", key="username_input")
        password = st.text_input("**Password**", placeholder="Enter your password", type="password", key="password_input")

        login_button_style = """
        <style>
            div.stButton > button:first-child {
                background-color: #2E86C1;
                color: white;
                padding: 0.6em 1.5em;
                border-radius: 32px;
                border: none;
                font-size: 16px;
                transition: background-color 0.3s ease;
                text-align: center;
                width: 100%;
            }
            div.stButton > button:first-child:hover {
                background-color: #1B4F72;
            }
        </style>
        """
        st.markdown(login_button_style, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("**⚡Login**", disabled=st.session_state.login_tries <= 0):
                credentials = load_credentials()
                if username in credentials and credentials[username]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = credentials[username]["role"]
                    st.session_state.has_admin_access = credentials[username]["has_admin_access"]
                    st.session_state.empid = credentials[username]["empid"]
                    st.session_state.login_tries = 3
                    st.session_state['session_time'] = time.time()
                    print(f"Login successful, session time set to: {st.session_state['session_time']}")
                    st.toast("✅Login successful!")
                    st.rerun()
                else:
                    st.session_state.login_tries -= 1
                    if st.session_state.login_tries > 0:
                        st.error(f"❌ Invalid username or password. You have {st.session_state.login_tries} attempts left.")
                    else:
                        st.error("❌ You have exceeded the maximum number of login attempts. Please try again later.")

        if st.session_state.login_tries <= 0:
            st.warning("You have exceeded the maximum number of login attempts. Please contact support.")

        st.markdown('</div>', unsafe_allow_html=True)

def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.has_admin_access = False
    st.session_state.empid = None
    st.session_state.login_tries = 3
    st.session_state.session_time = 0
    st.success("✅ Logged out successfully!")
    st.rerun()

# if __name__ == "__main__":
#     init_session_state()
#     if not st.session_state.authenticated:
#         login()
