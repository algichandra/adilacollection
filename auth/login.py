import streamlit as st
import base64
import os

def login(username, password):
    return username == "admin" and password == "admin123"

def get_base64_image(image_path):
    with open(image_path, "rb") as file:
        return base64.b64encode(file.read()).decode()

def login_page():
    image_path = "background.jpeg"
    if not os.path.exists(image_path):
        st.error(f"❌ File gambar '{image_path}' tidak ditemukan.")
        return

    bg_base64 = get_base64_image(image_path)

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        h1 {{
            color: white !important;
            text-align: center;
            font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Login")
    username = st.text_input("Username", key="login_username") 
    password = st.text_input("Password", type="password", key="login_password") 

    if st.button("Login"):
        if login(username, password):
            st.session_state.logged_in = True
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username atau Password salah!")
