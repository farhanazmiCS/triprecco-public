import streamlit as st 

def register():
   st.session_state.is_register = True

def login():
   st.session_state.is_register = False