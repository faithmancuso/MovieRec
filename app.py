from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
from werkzeug.security import check_password_hash
from database import init_db, add_user, get_user, update_movie_library
from tmdb_client import TMDbClient
import requests

# API Configuration
TMDB_API_KEY = "014a60d17b4bac376330b1a7b7161372"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Utility function to fetch movie details from TMDb API
def fetch_movie_details(movie_name):
    """
    Fetch movie details like genre, rating, and release date from TMDb API.
    Args: movie_name (str): Name of the movie to search for.
    Returns:  dict: Movie details including genre, rating, and release date.
    """
    search_url = f"{TMDB_BASE_URL}/search/movie"
    details = {"genre": "Unknown", "rating": "Unknown", "release_date": "Unknown"}

    try:
        # API call to search for the movie
        response = requests.get(
            search_url,
            params={"api_key": TMDB_API_KEY, "query": movie_name}
        )
        response_data = response.json()

        # Process the first result from the search
        if response_data.get("results"):
            movie = response_data["results"][0]
            details["genre"] = fetch_movie_genres(movie["genre_ids"])
            details["rating"] = movie.get("vote_average", "Unknown")
            details["release_date"] = movie.get("release_date", "Unknown")
    except Exception as e:
        print(f"Error fetching movie details: {e}")

    return details

# Utility function to fetch movie genres
def fetch_movie_genres(genre_ids):
    """
    Retrieve genre names based on genre IDs from TMDb API.
    Args:  genre_ids (list): List of genre IDs associated with a movie.
    Returns:  str: Comma-separated string of genre names.
    """
    genre_url = f"{TMDB_BASE_URL}/genre/movie/list"
    genres = {}

    try:
        # Fetch all genres from TMDb API
        response = requests.get(
            genre_url,
            params={"api_key": TMDB_API_KEY}
        )
        genre_data = response.json()
        if genre_data.get("genres"):
            for genre in genre_data["genres"]:
                genres[genre["id"]] = genre["name"]

        # Map genre IDs to names
        return ", ".join([genres.get(genre_id, "Unknown") for genre_id in genre_ids])
    except Exception as e:
        print(f"Error fetching genres: {e}")
        return "Unknown"

# Flask application setup
app = Flask(__name__)
app.secret_key = "492"

# Initialize the database on app start
init_db()

# TMDb API client setup
api_key = "014a60d17b4bac376330b1a7b7161372"
tmdb_client = TMDbClient(api_key)

# Route for the homepage
@app.route("/")
def home():
    """
    Handle requests to the homepage. Fetch the user's movie library if logged in.
    Returns: Renders the homepage with the user's movie library and data.
    """
    user_data = None

    # Check if the user is logged in
    if "user_username" in session:
        user_data = get_user(session["user_username"])  # Fetch user data
        movie_library = json.loads(user_data[3])  # Parse the user's movie library (stored as JSON)
    else:
        movie_library = []  # Default to an empty library for guests

    # Render the homepage with the user's movie library
    return render_template("index.html", movie_library=movie_library, user_data=user_data)

# Route for authentication (Sign in/Sign up)
@app.route("/auth", methods=["GET", "POST"])
def auth():
    """
    Handle user authentication for sign-in and sign-up.
    Methods:
        GET: Render the authentication page.
        POST: Process sign-in or sign-up requests.
    Returns: Redirects or renders authentication page with messages.
    """
    if request.method == "POST":
        # Handle user sign-up
        if "sign_up" in request.form:
            username = request.form["username"]
            password = request.form["password"]

            # Add new user to the database
            if add_user(username, password):
                flash("Sign up successful! Please sign in.", "success")
                return redirect(url_for("auth"))
            else:
                flash("Username already taken. Try another.", "error")
        # Handle user sign-in
        elif "sign_in" in request.form:
            username = request.form["username"]
            password = request.form["password"]

            # Verify user credentials
            user = get_user(username)
            if user and check_password_hash(user[2], password):
                session["user_id"] = user[0]
                session["user_username"] = user[1]
                flash("Signed in successfully!", "success")
                return redirect(url_for("home"))
            else:
                flash("Invalid username or password.", "danger")

    # Render the authentication page
    return render_template("auth.html")

# Route for logout
@app.route("/logout")
def logout():
    """
    Handle user logout. Clear the session and redirect to the homepage.
    Returns: Redirect to homepage with a message.
    """
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

# Route for the user's movie library
@app.route("/library", methods=["GET", "POST"])
def library():
    """
    Handle requests to view or update the user's movie library.
    Methods:
        GET: Render the library page with the user's current library.
        POST: Add a new movie to the library.
    Returns: Renders the library page or redirects with messages.
    """
    # Ensure the user is signed in
    if "user_username" not in session:
        flash("Please sign in to access your movie library.", "warning")
        return redirect(url_for("auth"))

    # Fetch user data and parse their current movie library
    user_data = get_user(session["user_username"])
    if user_data is None:
        flash("User not found. Please sign in again.", "warning")
        session.clear()
        return redirect(url_for("auth"))

    movie_library = json.loads(user_data[3]) if user_data[3] else []

    if request.method == "POST":
        # Retrieve movie details from form
        movie_name = request.form["movie_name"]
        user_rating = float(request.form.get("user_rating"))

        # Fetch movie details using the API
        movie_details = fetch_movie_details(movie_name)

        # Add the new movie to the library
        new_movie = {
            "title": movie_name,
            "user_rating": user_rating,
            "genre": movie_details["genre"],
            "rating": movie_details["rating"],
            "release_date": movie_details["release_date"],
        }
        movie_library.append(new_movie)

        # Save the updated library to the database
        update_movie_library(user_data[0], json.dumps(movie_library))
        flash("Movie added successfully!", "success")

    # Render the library page with the current movie library
    return render_template("library.html", movie_library=movie_library)

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)