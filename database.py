import sqlite3
from werkzeug.security import generate_password_hash

# Database file name
DB_NAME = "users.db"

def init_db():
    """
    Initialize the SQLite database and create the required tables.
    Creates a table 'users' with the following fields:
        - id: Primary key, auto-incremented.
        - username: Unique username for each user.
        - password: Hashed password for user authentication.
        - movie_library: JSON string to store the user's movie library.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            movie_library TEXT DEFAULT '[]'  -- Store movie library as a JSON string
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    """
    Add a new user to the database with a hashed password.
    Args:
        username (str): The username of the new user.
        password (str): The plaintext password of the new user.
    Returns:  bool: True if the user was added successfully, False if the username already exists.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, hashed_password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()
    return True

def get_user(username):
    """
    Retrieve user data from the database by username.
    Args: username (str): The username to search for.
    Returns: tuple: The user's data (id, username, password, movie_library) or None if not found.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_movie_library(user_id, movie_library):
    """
    Update the movie library for a specific user in the database.
    Args:
        user_id (int): The ID of the user whose library will be updated.
        movie_library (str): The updated movie library as a JSON string.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET movie_library = ? WHERE id = ?',
        (movie_library, user_id)
    )
    conn.commit()
    conn.close()