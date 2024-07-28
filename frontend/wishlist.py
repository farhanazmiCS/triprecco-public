import numpy as np
import streamlit as st
import yaml
from firebase_admin import firestore
from core_functions import fetch_images_with_cycling, generate_search_queries, remove_from_wishlist
from yaml.loader import SafeLoader

def wishlist(username: str):
    # Load config file
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Access the API keys and search engine IDs from the config
    GOOGLE_API_KEYS = config['api_keys']['google_custom_search']['api_keys']
    SEARCH_ENGINE_IDS = config['api_keys']['google_custom_search']['search_engine_ids']

    # Get all the trip ids from the user's wishlist
    db = firestore.client()
    interactions = db.collection('interactions').where('username', '==', username).stream()
    trips = [trip.to_dict() for trip in interactions if trip.to_dict()['type'] == 'wishlist']

    if not trips:
        st.write("No trips in your wishlist yet :(")
    else:
        for trip in trips:
            with st.container():
                left, right = st.columns([3, 0.6])
                left.title(f"{trip['trip']['trip_name']}")
                left.write(f"{trip['trip']['trip_description']}")
                right.title(f"S${trip['trip']['budget']}")
                
                search_queries = generate_search_queries(trip['trip'])                
                image_urls = fetch_images_with_cycling(search_queries, GOOGLE_API_KEYS, SEARCH_ENGINE_IDS)

                if image_urls:
                    cols = st.columns(3)
                    for i, img_url in enumerate(image_urls[:3]):
                        cols[i % 3].image(img_url, caption=f"Image {i + 1}")

                if st.button(
                    label="❌ Remove from Wishlist",
                    key=trip['trip']['trip_name']+str(trip['trip']['trip_id'])
                ):
                    remove_from_wishlist(username, trip['trip_id'])                

                if st.button(
                    label="View Details", 
                    key=f"details_{trip['trip']['trip_name']}",
                    on_click=view_details,
                    args=(trip['trip']["trip_name"], trip['trip']["trip_description"], trip['trip']["stopovers"], trip['trip']["budget"], trip['trip'])
                    ):
                        #st.query_params(trip=trip['trip_name'])
                        #So st.query_params.key = value or st.query_params["key"] = value should do.
                        #st.query_params.key = trip['trip_name']
                        
                        st.session_state.current_page = "details"
                        st.experimental_rerun()

                st.write("\n")

def view_details(trip_name, trip_description, trip_stopovers, trip_budget, trip):
    st.session_state["trip_name"] = trip_name
    st.session_state["trip_description"] = trip_description
    st.session_state["stopovers"] = trip_stopovers
    st.session_state["budget"] = trip_budget
    st.session_state["the_trip"] = trip

def wishlist(username: str):
    # Load config file
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Access the API keys and search engine IDs from the config
    GOOGLE_API_KEYS = config['api_keys']['google_custom_search']['api_keys']
    SEARCH_ENGINE_IDS = config['api_keys']['google_custom_search']['search_engine_ids']

    # Get all the trip ids from the user's wishlist
    db = firestore.client()
    interactions = db.collection('interactions').where('username', '==', username).stream()
    trips = [trip.to_dict() for trip in interactions if trip.to_dict()['type'] == 'wishlist']

    if not trips:
        st.write("No trips in your wishlist yet :(")
    else:
        for trip in trips:
            with st.container():
                left, right = st.columns([3, 0.6])
                left.title(f"{trip['trip']['trip_name']}")
                left.write(f"{trip['trip']['trip_description']}")
                right.title(f"S${trip['trip']['budget']}")
                
                search_queries = generate_search_queries(trip['trip'])                
                image_urls = fetch_images_with_cycling(search_queries, GOOGLE_API_KEYS, SEARCH_ENGINE_IDS)

                if image_urls:
                    cols = st.columns(3)
                    for i, img_url in enumerate(image_urls[:3]):
                        cols[i % 3].image(img_url, caption=f"Image {i + 1}")

                if st.button(
                    label="❌ Remove from Wishlist",
                    key=trip['trip']['trip_name']+str(trip['trip']['trip_id'])
                ):
                    remove_from_wishlist(username, trip['trip_id'])
                    st.experimental_rerun()
                

                if st.button(
                    label="View Details", 
                    key=f"details_{trip['trip']['trip_name']}",
                    on_click=view_details,
                    args=(trip['trip']["trip_name"], trip['trip']["trip_description"], trip['trip']["stopovers"], trip['trip']["budget"], trip['trip'])
                    ):
                        #st.query_params(trip=trip['trip_name'])
                        #So st.query_params.key = value or st.query_params["key"] = value should do.
                        #st.query_params.key = trip['trip_name']
                        
                        st.session_state.current_page = "details"

                st.write("\n")

def view_details(trip_name, trip_description, trip_stopovers, trip_budget, trip):
    st.session_state["trip_name"] = trip_name
    st.session_state["trip_description"] = trip_description
    st.session_state["stopovers"] = trip_stopovers
    st.session_state["budget"] = trip_budget
    st.session_state["the_trip"] = trip
