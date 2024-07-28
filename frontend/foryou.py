import os
import sys

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import yaml
from yaml.loader import SafeLoader

from core_functions import (
    add_to_wishlist,
    check_trip_added_to_wishlist,
    computeSearchQueryVector,
    computeTripVector,
    computeUserVector,
    fetch_google_images,
    fetch_images_with_cycling,
    fetch_latest_interaction,
    generate_search_queries,
    log_search,
    query_faiss_index,
    remove_from_wishlist,
    retrieve_user_preferences
)

import pickle

def foryou(username: str, search_query: str = "", all_trips: list = None, index: object = None):
    try:
        # Retrieve user preferences from the database
        user_preferences = retrieve_user_preferences(username)[0]

        # Load vectorizer
        with open('vectorizer.pkl', 'rb') as file:
            tfidf_vectorizer = pickle.load(file)
            print(tfidf_vectorizer)

        # Load config file
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)

        # Access the API keys and search engine IDs from the config
        GOOGLE_API_KEYS = config['api_keys']['google_custom_search']['api_keys']
        SEARCH_ENGINE_IDS = config['api_keys']['google_custom_search']['search_engine_ids']

        # Query the FAISS index to get the recommended trips based on the user preferences

        # Initialize weights in session state if not present
        if "weights" not in st.session_state:
            st.session_state.weights = {
                'user_preferences': 1.0,
                'wishlist': 0.0,
                'search_query': 0.0
            }

        user_preferences_vector = computeUserVector(user_preferences, tfidf_vectorizer)
        combined_vector = st.session_state.weights['user_preferences'] * user_preferences_vector

        # Fetch latest wishlist interaction
        latest_wishlist = fetch_latest_interaction(username, 'wishlist')
        if latest_wishlist:
            wishlist_vector = computeTripVector(latest_wishlist['trip'], tfidf_vectorizer)
            st.session_state.weights['wishlist'] = 0.15
            st.session_state.weights['user_preferences'] = 1 - st.session_state.weights['wishlist']
            combined_vector = combined_vector + st.session_state.weights['wishlist'] * wishlist_vector

        # Fetch latest search query interaction
        latest_search_query = fetch_latest_interaction(username, 'search')
        if latest_search_query:
            search_query_vector = computeSearchQueryVector(latest_search_query['search_query'], tfidf_vectorizer)
            st.session_state.weights['search_query'] = 0.15
            st.session_state.weights['wishlist'] = 0.15 if latest_wishlist else 0.0
            st.session_state.weights['user_preferences'] = 1 - st.session_state.weights['search_query'] - st.session_state.weights['wishlist']
            print(st.session_state.weights)
            combined_vector = combined_vector + st.session_state.weights['search_query'] * search_query_vector

        # Query the FAISS index to get the recommended trips
        recommended_trips = query_faiss_index(index, all_trips, combined_vector, 20)
        
        # If a search query is provided, update the recommended trips based on the search query
        if search_query:
            log_search(username, search_query)
            search_query_vector = computeSearchQueryVector(search_query, tfidf_vectorizer)
            recommended_trips = query_faiss_index(index, all_trips, search_query_vector)

    except IndexError:
        st.write("User preferences not found :/")
    else:
        for trip in recommended_trips[:50]:
            with st.container():
                left, right = st.columns([3, 0.6])
                left.title(f"{trip['trip_name']}")
                left.write(f"{trip['trip_description']}")
                right.title(f"S${trip['budget']}")
                
                search_queries = generate_search_queries(trip)
                image_urls = fetch_images_with_cycling(search_queries, GOOGLE_API_KEYS, SEARCH_ENGINE_IDS)

                if image_urls:
                    cols = st.columns(3)
                    for i, img_url in enumerate(image_urls[:3]):
                        cols[i % 3].image(img_url, caption=f"Image {i + 1}")

                if check_trip_added_to_wishlist(username, trip['trip_id']):
                    st.button(
                        label="✅ Added to Wishlist",
                        key=trip['trip_name']+str(trip['trip_id']),
                        on_click=remove_from_wishlist,
                        args=(username, trip['trip_id'])
                    )
                else:
                    st.button(
                        label="\+ Add to Wishlist",
                        key=trip['trip_name']+str(trip['trip_id']),
                        on_click=add_to_wishlist,
                        args=(username, trip, trip['trip_id'])
                    )

                if st.button(
                    label="View Details", 
                    key=f"details_{trip['trip_name']+str(trip['trip_id'])}",
                    on_click=view_details,
                    args=(trip["trip_name"], trip["trip_description"], trip["stopovers"], trip["budget"], trip, trip["trip_id"])
                    ):
                        #st.query_params(trip=trip['trip_name'])
                        #So st.query_params.key = value or st.query_params["key"] = value should do.
                        #st.query_params.key = trip['trip_name']
                        
                        st.session_state.current_page = "details"
 
                st.write("\n")

def view_details(trip_name, trip_description, trip_stopovers, trip_budget, trip, trip_id):
    st.session_state["trip_name"] = trip_name
    st.session_state["trip_description"] = trip_description
    st.session_state["stopovers"] = trip_stopovers
    st.session_state["budget"] = trip_budget
    st.session_state["the_trip"] = trip
    st.session_state["trip_id"] = trip_id

def fetch_images_with_cycling(search_queries, api_keys, search_engine_ids):
    api_key_index = 0
    image_urls = []
    
    for query in search_queries:
        # Try each key until we find images or exhaust all keys
        for _ in range(len(api_keys)):
            api_key = api_keys[api_key_index]
            search_engine_id = search_engine_ids[api_key_index]
            
            try:
                image_urls.extend(fetch_google_images(query, api_key, search_engine_id))
                if image_urls:
                    break
            except Exception as e:
                # Handle exception if needed (e.g., log the error, move to the next key)
                pass
            
            # Move to the next key
            api_key_index = (api_key_index + 1) % len(api_keys)
        
        if image_urls:
            break
    
    return image_urls
