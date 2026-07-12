import requests
import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL =  f"http://www.omdbapi.com/?apikey={os.getenv('OMDB_API_KEY')}"

def search_movie(movie_name):
    params={
        "t" : movie_name,
        "type" : "movie"
    }
    response = requests.get(BASE_URL , params=params)
    data=response.json()
    if data.get('Response') == "True":
        return{
            "title" : data["Title"],
            "rating" : data.get('imdbRating', 'N/A'),
            "poster": data.get('Poster') if data.get('Poster') != 'N/A' else None,
            "release_date" : data.get('Released')
        }
    return None
