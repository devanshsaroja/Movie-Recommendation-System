import streamlit as st
import pickle as pk
import pandas as pd
import requests
import time

# Load the data
movies_dict = pk.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pk.load(open('similarity.pkl', 'rb'))

# Fetch movie posters from the API
def fetch_posters(movie_id):
    api_key = '3786a13ea0c164ca7502af894bafff62'
    base_url = 'https://api.themoviedb.org/3/movie/'
    try:
        response = requests.get(f'{base_url}{movie_id}?api_key={api_key}&language=en-US', timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        return 'https://image.tmdb.org/t/p/w500/' + data['poster_path']
    except requests.exceptions.RequestException as e:
        st.write(f"Error fetching poster for movie ID {movie_id}: {e}")
        return ""  # Return an empty string if fetching fails
    except KeyError:
        st.write(f"Poster not found for movie ID {movie_id}.")
        return ""

# Recommend function to get similar movies
def recommend(movie):
    try:
        movie = movie.strip().lower()
        matched_movies = movies[movies['title'].str.strip().str.lower() == movie]
        
        if matched_movies.empty:
            st.write(f"Movie '{movie}' not found in the dataset.")
            return [], []
        
        index = matched_movies.index[0]
        movies_list = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        movies_list = movies_list[1:6]
        
        recommended_movies_posters = []
        recommended_movies = []

        for i in movies_list:
            movie_id = movies.iloc[i[0]]['id']
            recommended_movies.append(movies.iloc[i[0]]['title'])
            poster_url = fetch_posters(movie_id)
            if poster_url:  # Only append if the poster URL is valid
                recommended_movies_posters.append(poster_url)
            else:
                recommended_movies_posters.append('https://via.placeholder.com/150')  # Fallback placeholder
            time.sleep(1)  # Add delay between requests
        
        return recommended_movies, recommended_movies_posters

    except Exception as e:
        st.write(f"An error occurred in recommendation: {e}")
        return [], []

# Streamlit interface
st.title("MOVIE RECOMMENDATION SYSTEM")
st.image("movi_poster.jpg")

option = st.selectbox(
    "Movies",
    (movies['title'].values),
)

if st.button("Recommend"):
    names, posters = recommend(option)
    if not names:
        st.write("No recommendations found.")
    else:
        cols = st.columns(len(names))
        for i in range(len(names)):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])