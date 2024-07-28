import streamlit as st
import yaml
from yaml.loader import SafeLoader

from core_functions import (
    add_to_wishlist,
    check_trip_added_to_wishlist,
    fetch_images_with_cycling,
    generate_search_queries,
    remove_from_wishlist
)

def details(username: str):
    # Load config file
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Access the API keys and search engine IDs from the config
    GOOGLE_API_KEYS = config['api_keys']['google_custom_search']['api_keys']
    SEARCH_ENGINE_IDS = config['api_keys']['google_custom_search']['search_engine_ids']

    with st.container():
        if "trip_name" in st.session_state:
            #Trip name
            st.markdown(f"<h1 style='font-size:40px;'>{st.session_state['trip_name']}</h1>", unsafe_allow_html=True)
            #Images
            search_queries = generate_search_queries(st.session_state["the_trip"])
            image_urls = fetch_images_with_cycling(search_queries, GOOGLE_API_KEYS, SEARCH_ENGINE_IDS)

            if image_urls:
                cols = st.columns(3)
                for i, img_url in enumerate(image_urls[:3]):
                    cols[i % 3].image(img_url, caption=f"Image {i + 1}")
            #Trip Desc
            st.markdown(f"<p style='font-size:32px;'>{st.session_state['trip_description']}</p>", unsafe_allow_html=True)
            
            #Trip budget
            st.markdown(f"<h2 style='font-size:28px;'>Budget: ${st.session_state['budget']}</h2>", unsafe_allow_html=True)

            #Stopovers
            stopovers = st.session_state['stopovers']
            for stopover in stopovers:
                stopover_name = list(stopover.items())[0]
                st.write(f"### Stopover: {stopover_name[1]}")
                st.write(f"**Activities:**")
                for activity in stopover["activities"]:
                    st.write(f"- {activity}")
                st.write(f"**Stay:** {stopover['stay']}")
                st.write("---")
            #st.markdown(f"<p style='font-size:28px;'>Stopovers: {st.session_state['stopovers']}</p>", unsafe_allow_html=True)

            if check_trip_added_to_wishlist(username, st.session_state['trip_id']):
                st.button(
                    label="✅ Added to Wishlist",
                    key=st.session_state['trip_name']+str(st.session_state['trip_id']),
                    on_click=remove_from_wishlist,
                    args=(username, st.session_state['trip_id'])
                )
            else:
                st.button(
                    label="\+ Add to Wishlist",
                    key= st.session_state['trip_name']+str(st.session_state["trip_id"]),
                    on_click=add_to_wishlist,
                    args=(username,st.session_state["the_trip"],st.session_state["trip_id"])
                )
