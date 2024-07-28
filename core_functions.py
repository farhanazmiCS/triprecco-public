import json
import re
from datetime import datetime

import numpy as np
import requests
from faiss import IndexFlatL2
from firebase_admin import firestore

def computeTripVector(trip, vectorizer):
    """ Function to compute the trip vector based on the trip details """
    # To Tfidf vectorize
    trip_text = " ".join([
            trip['trip_name'], 
            trip['trip_description'], 
            " ".join([stopover[f'stopover_{index + 1}'] for index, stopover in enumerate(trip['stopovers'])])
        ])
    trip_vector = vectorizer.transform([trip_text])
    trip_vector = trip_vector.toarray()

    return trip_vector

def computeUserVector(user_preferences, vectorizer):
    """ Function to compute the user vector based on the user preferences """
    # To Tfidf vectorize
    features = ' '.join(user_preferences['preferences']['activity_preferences']) + ' ' + user_preferences['preferences']['travel_type'] + ' ' + user_preferences['preferences']['age_group'] + ' ' + user_preferences['preferences']['budget']
    user_preferences_vector = vectorizer.transform([features])
    user_preferences_vector = user_preferences_vector.toarray()

    return user_preferences_vector

def computeSearchQueryVector(search_query, vectorizer):
    """ Function to compute the search query vector based on the search query """
    # To Tfidf vectorize
    search_query_vector = vectorizer.transform([search_query])
    search_query_vector = search_query_vector.toarray()

    return search_query_vector

def build_faiss_index() -> tuple:
    all_trips = fetch_trips()
    if not all_trips:
        return [], None
    
    embeddings = np.array([trip['itinerary_vector'] for trip in all_trips])
    print(f"Fetched {len(all_trips)} products with embeddings shape: {embeddings.shape}")
    
    d = embeddings.shape[1]
    index = IndexFlatL2(d)  # Initialize the index
    index.add(embeddings)  # Add the embeddings to the index
    
    return all_trips, index

def fetch_trips() -> list:
    with open('itineraries/trip_itineraries_global_with_encodings.json') as file:
        trips = json.load(file)
    for trip in trips:
        trip['itinerary_vector'] = np.array(trip['itinerary_vector'])
    return trips

def query_faiss_index(index, all_trips, query_vector, top_k=10) -> list:
    """ 
        Function to query the FAISS index to get the recommended trips based on a query vector 
        
        A query vector could be of:

        - User preferences
        - A trip vector
        - A search query
    
    """
    query_vector = np.array(query_vector).reshape(1, -1)  # Reshape query vector for FAISS
    distances, indices = index.search(query_vector, top_k)
    results = [all_trips[i] for i in indices[0]]
    return results

def read_preferences() -> tuple:
    """ Function to read the predefined preferences from the preferences.txt file """
    preferences = open('preferences.txt').read().split('\n')
    activity_preferences_options_index = preferences.index("ACTIVITY_PREFERENCES_OPTIONS")
    travel_type_options_index = preferences.index("TRAVEL_TYPE_OPTIONS")

    age_group_options = preferences[1:activity_preferences_options_index]
    activity_preferences_options = preferences[activity_preferences_options_index + 1:travel_type_options_index]
    travel_type_options = preferences[travel_type_options_index + 1:]

    return age_group_options, activity_preferences_options, travel_type_options

def retrieve_user_preferences(username: str) -> list:
    """ Function to retrieve the user preferences from the Firestore database """
    db = firestore.client()
    users_ref = db.collection('user_features')
    query = users_ref.where('username', '==', username)
    docs = query.stream()

    results = []

    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        results.append(data)
    return results

def fetch_google_images(search_query, api_key, search_engine_id, num_images=5):
    """ Function to retrieve images from Google Custom Search JSON API"""
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "q": search_query,
        "cx": search_engine_id,
        "searchType": "image",
        "num": num_images,
        "key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        image_urls = [item["link"] for item in data.get("items", [])]
        return image_urls
    else:
        return []

def generate_search_queries(trip):
    """ Function to generate queries for image search using Google Custom Search JSON API """
    queries = []
    for stopover in trip["stopovers"]:
        for key, value in stopover.items():
            if key.startswith("stopover"):
                # Extract capitalized words from each activity and create search queries
                for activity in stopover["activities"]:
                    capitalized_words = " ".join(re.findall(r'\b[A-Z][a-zA-Z]*\b', activity))
                    if capitalized_words:
                        queries.append(f"{value} {capitalized_words}")
    return queries

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

def log_search(username: str, search_query: str):
    db = firestore.client()
    try:
        search_ref = db.collection('interactions')
    except Exception as e:
        print(e)
    else:
        try:
            search_ref.add({
                'type': 'search',
                'username': username,
                'search_query': search_query,
                'date': datetime.now().isoformat()
            })
        except Exception as e:
            print(e)
        else:
            print('Logged search successfully!')

def add_to_wishlist(username: str, trip: object, trip_id: int):
    db = firestore.client()
    try:
        wishlist_ref = db.collection('interactions')
    except Exception as e:
        print(e)
    else:
        try:
            trip['itinerary_vector'] = trip['itinerary_vector'].tolist()
            wishlist_ref.add({
                'type': 'wishlist',
                'username': username,
                'trip_id': trip_id,
                'trip': trip,
                'date': datetime.now().isoformat()
            })
        except Exception as e:
            print(e)
        else:
            print('Added to wishlist successfully!')

def remove_from_wishlist(username: str, tripID: int):
    db = firestore.client()
    wishlist_ref = db.collection('interactions')
    # Get the trip with the trip id
    query = wishlist_ref.where('username', '==', username).where('trip_id', '==', tripID)
    docs = query.stream()
    for doc in docs:
        doc.reference.delete()

def check_trip_added_to_wishlist(username: str, tripID: int) -> bool:
    """ Function to check if a trip has been added to the user's wishlist, 
    
        Returns: True if added, False otherwise """
    db = firestore.client()
    wishlist_ref = db.collection('interactions')
    query = wishlist_ref.where('username', '==', username).where('trip_id', '==', tripID)
    docs = query.stream()
    return len(list(docs)) > 0

def fetch_latest_interaction(username: str, interaction_type: str = 'wishlist'):
    db = firestore.client()
    interactions_ref = db.collection('interactions')
    
    # Query for the latest interaction of the given type for the user
    query = interactions_ref.where('username', '==', username)\
                            .where('type', '==', interaction_type)\
                            .order_by('date', direction=firestore.Query.DESCENDING)\
                            .limit(1)
    interaction_docs = query.stream()

    for doc in interaction_docs:
        return doc.to_dict()

    return None