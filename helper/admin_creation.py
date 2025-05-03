import bcrypt
import sqlite3  # You can replace this with your preferred database connector
from sql_connector import sql_connector

mydb = sql_connector()

# Function to hash a password
def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    return hashed_password

# Function to save hashed password to database
def save_to_database(username, hashed_password):
    db = mydb.cursor(dictionary=True)
    
    # Insert the user data into the table
    try:
        db.execute('INSERT INTO admin (username, password) VALUES (%s, %s)', (username, hashed_password))
        mydb.commit()
        print("User saved successfully!")

    except sqlite3.IntegrityError as e:
        print("Error:", e)

    finally:
        mydb.close()

# Example usage
if __name__ == '__main__':
    # Input username and password
    username = input("Enter your admin username: ")
    password = input("Enter your admin password: ")
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Save to database
    save_to_database(username, hashed_password)
