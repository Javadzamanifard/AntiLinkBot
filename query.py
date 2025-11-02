import sqlite3
from environs import Env

env = Env()
env.read_env()
DATABASE_NAME = env.str("DATABASE_NAME", "database.db")

# Function to connect to the SQLite database
def connect_to_db():
    conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cursor = conn.cursor()  
    return conn, cursor

# Function to insert a user into the database
def insert_user(user_id):
    conn, cursor = connect_to_db()
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (user_id, white, warns)
        VALUES (?, 'False', 0)
        """, (user_id,)
    )
    conn.commit()
    conn.close()

# Function to get a user's ID from the database
# Returns None if the user does not exist
def get_user_id(user_id):
    conn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT user_id FROM users WHERE user_id = ?
        """, (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Function to update a user's whitelist status
# Sets the 'white' field to 'True' for the specified user_id
def update_white_by_user_id(user_id):
    conn, cursor = connect_to_db()
    cursor.execute(
        """
        UPDATE users SET white = 'True' WHERE user_id = ?
        """, (user_id,)
    )
    conn.commit()
    conn.close()

# Function to remove a user from the whitelist
# Deletes the user with the specified user_id from the database
def remove_user_from_whitlist(user_id):
    conn, cursor = connect_to_db()
    cursor.execute(
        """
        DELETE FROM users WHERE user_id = ?
        """, (user_id,)
    )
    conn.commit()
    conn.close()

# Function to get the whitelist status of a user
# Returns the 'white' field value for the specified user_id
def get_whitelist(user_id):
    conn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT white FROM users WHERE user_id = ?
        """, (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Function to update the current link handling mode
def update_link_mode(mode):
    conn, cursor = connect_to_db()
    cursor.execute(
        """
        UPDATE link_mode SET mode = ?
        """, (mode,)
    )
    conn.commit()
    conn.close()

# Function to get the current link handling mode
def get_current_link_mode():
    conn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT mode FROM link_mode LIMIT 1
        """
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'delete'  # Default to 'delete' if no mode is set

# Function to get the number of users in the whitelist
def get_number_of_all_whitelists_user():
    conn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT COUNT(*) FROM users WHERE white = 'True'
        """
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

# Function to get the number of users with warnings
def get_number_of_warned_users():
    conn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT COUNT(*) FROM users WHERE warns > 0
        """
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

# Function to increment the warning count for a user
def update_warns_by_user_id(user_id):
    conn, cursor = connect_to_db()
    cursor.execute(
        """
        UPDATE users SET warns = warns + 1 WHERE user_id = ?
        """, (user_id,)
    )
    conn.commit()
    conn.close()

# Function to get the number of warnings for a user
def get_warns_by_user_id(user_id):
    conn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT warns FROM users WHERE user_id = ?
        """, (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0