import os
import sys

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from firebase_admin import firestore
from core_functions import read_preferences, retrieve_user_preferences


age_group_options, activity_preferences_options, travel_type_options = read_preferences()

def save_preferences(username: str, preferences: dict):
    # Check if user's user_preferences document already exists
    db = firestore.client()
    user_preference = retrieve_user_preferences(username)
    if user_preference == []:
        # Create a new document
        try:
            db.collection('user_features').document().set(
                {
                    "username": username,
                    "preferences": {
                        "age_group": preferences['age_group'],
                        "activity_preferences": preferences['activity_preferences'],
                        "travel_type": preferences['travel_type'],
                        "budget": '${}.00'.format(preferences['budget'])
                    },
                    "trips_clicked": [],
                    "trips_wishlist": []
                }
            )
        except:
            st.toast(body="red-background[An error occurred. Preferences not saved.]")
        else:
            st.toast(body=":green-background[Preferences Saved]")
    else:
        try:
            db.collection('user_features').document(user_preference[0]['id']).update({
                "preferences": {
                    "age_group": preferences['age_group'],
                    "activity_preferences": preferences['activity_preferences'],
                    "travel_type": preferences['travel_type'],
                    "budget": '${}.00'.format(preferences['budget'])
                },
            }
        )

        except:
            st.toast(body="red-background[An error occurred. Preferences not saved.]")
        else:
            st.toast(body=":green-background[Preferences Saved]")

def preferences(username: str):
    try:
        user_preferences = retrieve_user_preferences(username)[0]
        user_preferences = {
        'age_group': user_preferences["preferences"]["age_group"],
        'activity_preferences': user_preferences["preferences"]["activity_preferences"],
        'travel_type': user_preferences["preferences"]["travel_type"],
        'budget': user_preferences["preferences"]["budget"]
    }
    except IndexError:
        user_preferences = {
            'age_group': "18-29",
            'activity_preferences': [],
            'travel_type': "Solo",
            'budget': "$1000.00"
        }

    st.write("1. Age Group")
    age_group = st.selectbox(
        label="age_group",
        options=age_group_options,
        label_visibility="collapsed",
        index=age_group_options.index(user_preferences['age_group'])
    )

    st.write("2. Activity Preferences")
    activity_preferences = st.multiselect(
        label="activity_preferences",
        options=activity_preferences_options,
        label_visibility="collapsed",
        default=user_preferences['activity_preferences']
    )

    st.write("3. Travel Type")
    travel_type = st.selectbox(
        label="travel_type",
        options=travel_type_options,
        label_visibility="collapsed",
        index=travel_type_options.index(user_preferences['travel_type'])
    )

    st.write("4. Budget")
    budget = st.slider(
        label="budget",
        min_value=0,
        max_value=100000,
        value=int(user_preferences['budget'][1:-3]),
        format="$%.2f",
        label_visibility="collapsed"
    )

    _, center, _ = st.columns(3)

    preferences = {
        'age_group': age_group, # str
        'activity_preferences': activity_preferences, # list
        'travel_type': travel_type, # str
        'budget': budget
    }

    with center:
        st.button(label="Save Preferences", use_container_width=True, on_click=save_preferences, args=(username, preferences))