import mysql.connector

# Isolate the sql connector so that it is centralized and standardised to all programs
# Also to reduce duplicate code across multiple programs
def sql_connector():
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database='le_future'
    )

    return mydb