import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="kasturi@326",   
        database="queue_system",
        connection_timeout=5
    )
