import streamlit as st
import base64
import os
from auth import init_session_state, login, logout
from user_management import user_management
from admin import admin_module




def load_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Provide the path to your image
image_path = os.path.join("images", "favicon.png")
base64_image = load_base64_image(image_path)

st.set_page_config(page_title="LF CS Module",page_icon="images/favicon.png", layout="wide")

# Initialize session state
init_session_state()
    

hide_streamlit_style = """
<style>
#MainMenu{
    background: linear-gradient(90deg, rgba(0,255,226,1) 0%, rgba(254,255,0,1) 32%, rgba(0,121,135,1) 68%, rgba(51,49,103,1) 100%);
    animation: gradient-animation 10s ease infinite;
    background-size: 200% 200%;
}
#stDecoration{
    background: linear-gradient(90deg, rgba(0,255,226,1) 0%, rgba(254,255,0,1) 32%, rgba(0,121,135,1) 68%, rgba(51,49,103,1) 100%);
    animation: gradient-animation 10s ease infinite;
    background-size: 200% 200%;
}
header{
    background: linear-gradient(90deg, rgba(0,255,226,1) 0%, rgba(254,255,0,1) 32%, rgba(0,121,135,1) 68%, rgba(51,49,103,1) 100%);
    animation: gradient-animation 10s ease infinite;
    background-size: 200% 200%;
}

@keyframes gradient-animation {
    0% {
        background-position: 91% 0%;
    }
    50% {
        background-position: 10% 100%;
    }
    100% {
        background-position: 91% 0%;
    }
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown("""
        <style>
               .block-container {
                    padding-top: 3rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

user = st.session_state.username
# Main app logic
if not st.session_state.authenticated:
    login()
else:
    st.sidebar.write(f"<h1>Welcome,<br><span style='color:#FFE100;'>{st.session_state.username}👋!</span></h1><br><br>",unsafe_allow_html=True)
    if st.session_state.role == 'voice':
        st.sidebar.write(f"🟡 Role: {st.session_state.role}🎧",unsafe_allow_html=True)
    elif st.session_state.role == 'email':
        st.sidebar.write(f"🟡 Role: {st.session_state.role}📧",unsafe_allow_html=True)
    else:
        st.sidebar.write(f"🟡 Role: {st.session_state.role}💸",unsafe_allow_html=True)
    st.sidebar.write(f"🟡 EmpID: {st.session_state.empid}",unsafe_allow_html=True)

    if st.session_state.has_admin_access:
        st.sidebar.write("You have admin access.")
        
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)

    # Module selection based on role
    if st.session_state.role == "Base_User":
        module = st.sidebar.selectbox("🔸Select Module", ["Advance Manager"],)
    elif st.session_state.role == "super_admin":
        module = st.sidebar.selectbox("🔸Select Module", ["Advance Manager", "User Management"])

    # Display selected module
    if module == "Advance Manager":
        admin_module()
    elif module == "User Management":
        user_management()
        
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    if st.sidebar.button("⏻ Logout",use_container_width=True, ):
        logout()
        
