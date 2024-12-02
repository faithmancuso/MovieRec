import requests

class TMDbClient:
    """
    A client for interacting with The Movie Database (TMDb) API.
    Attributes:
        api_key (str): The API key for authenticating TMDb API requests.
        base_url (str): The base URL for the TMDb API.
    """
    
    def __init__(self, api_key):
        """
        Initialize the TMDbClient with an API key.
        Args:  api_key (str): The API key for TMDb API.
        """
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    def search_movie(self, title):
        """
        Search for a movie by its title.
        Args:  title (str): The title of the movie to search for.
        Returns:  list: A list of movies matching the title, or an empty list if no results.
        """
        url = f"{self.base_url}/search/movie"
        params = {
            "api_key": self.api_key,
            "query": title
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            # Return a list of matching movies
            return response.json().get("results", [])
        else:
            print("Error:", response.status_code, response.text)
            return None

    def get_movie_details(self, movie_id):
        """
        Fetch detailed information about a movie by its ID.
        Args:  movie_id (int): The ID of the movie to fetch details for.
        Returns:  dict: A dictionary containing the movie's details, or None if an error occurs.
        """
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            "api_key": self.api_key
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            # Return the movie details as a dictionary
            return response.json()
        else:
            print("Error:", response.status_code, response.text)
            return None
