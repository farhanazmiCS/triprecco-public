import os
import sys

import firebase_admin
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from dotenv import load_dotenv
from firebase_admin import credentials
from yaml.loader import SafeLoader

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frontend.details import details
from frontend.foryou import foryou
from frontend.preferences import preferences
from frontend.register_login import login, register
from frontend.wishlist import wishlist

from core_functions import build_faiss_index

try:
    firebase_admin.get_app()
except ValueError:
    load_dotenv()
    cred = credentials.Certificate({
        "type": os.getenv("TYPE"),
        "project_id": os.getenv("PROJECT_ID"),
        "private_key_id": os.getenv("PRIVATE_KEY_ID"),
        "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("CLIENT_EMAIL"),
        "client_id": os.getenv("CLIENT_ID"),
        "auth_uri": os.getenv("AUTH_URI"),
        "token_uri": os.getenv("TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN")
    })
    firebase_admin.initialize_app(cred)

st.set_page_config(page_title="Home", layout="wide")

if "is_register" not in st.session_state:
        st.session_state.is_register = False

if "all_trips" not in st.session_state:
    st.session_state.all_trips = []

if "index" not in st.session_state:
    st.session_state.index = None

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

if not st.session_state["authentication_status"]:
    # Show login page
    if not st.session_state.is_register:
        st.markdown("<p style='text-align: center; color: white; font-size: 80px;'><strong>Trip</strong>recco</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: white; font-size: 20px'>Don't know where to go for your next trip? Ask Triprecco!</p>", unsafe_allow_html=True)
        authenticator.login()
        _, center, _ = st.columns(3)
        with center:
            st.button(
                label="Don't have an account? Create one here!", 
                use_container_width=True,
                on_click=register
            )
    # Show register page
    else:
        st.markdown("<p style='text-align: center; color: white; font-size: 80px;'><strong>Trip</strong>recco</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: white; font-size: 20px'>Don't know where to go for your next trip? Ask Triprecco!</p>", unsafe_allow_html=True)
        try:
            email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)                                                                                                                         
            if email_of_registered_user:
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.success('User registered successfully!')
        except Exception as e:
            st.error(e)
        _, center, _ = st.columns(3)
        with center:
            st.button(
                label="Already have an account? Log in here!", 
                use_container_width=True,
                on_click=login
            )
        
    if st.session_state["authentication_status"] is False:
        st.error("Username or password is incorrect.")
else:
    # Reset form
    st.session_state.is_register = not st.session_state.is_register

    # Display router
    st.sidebar.markdown("<p style='color: white; font-size: 30px;'><strong>Trip</strong>recco</p>", unsafe_allow_html=True)

    frontend = ["foryou", "wishlist", "preferences", "details"]
    if 'current_page' not in st.session_state:
        st.session_state.current_page = frontend[0]

    page = st.sidebar.radio(
        label="Navigation",
        options=["For You", "Wishlist", "Preferences", "Details"],
        label_visibility="collapsed",
        index=frontend.index(st.session_state.current_page),
    )

    # Logout button
    authenticator.logout(button_name="Log out", location="sidebar")
    
    if st.session_state.all_trips == None or st.session_state.index == None:
        st.session_state.all_trips, st.session_state.index = build_faiss_index()

    if page == "For You":
        st.session_state.current_page = "foryou"
    elif page == "Wishlist":
        st.session_state.current_page = "wishlist"
    elif page == "Preferences":
        st.session_state.current_page = "preferences"
    elif page == "Details":
        st.session_state.current_page = "details"

    if st.session_state.current_page == "foryou":
        # Add a search bar
        search_query = st.text_input(
            label="Search",
            label_visibility="collapsed",
            placeholder="Search a trip...",
        )
        st.header("For You")
        foryou(st.session_state.username, search_query, st.session_state.all_trips, st.session_state.index)
    elif st.session_state.current_page == "wishlist":
        st.header("Wishlist")
        wishlist(st.session_state.username)
    elif st.session_state.current_page == "preferences":
        st.header("Enter your travel preferences")
        preferences(st.session_state.username)
    elif st.session_state.current_page == "details":
        st.header("Trip details")
        details(st.session_state.username)