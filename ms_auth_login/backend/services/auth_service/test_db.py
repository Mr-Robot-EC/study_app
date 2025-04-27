import psycopg2
import sys

# Print Python version and encoding information
print(f"Python version: {sys.version}")
print(f"Default encoding: {sys.getdefaultencoding()}")

# Try connecting with psycopg2 directly
try:
    conn = psycopg2.connect(
        dbname="auth_db",
        user="auth_user",
        password="1234",
        host="localhost"
    )
    print("Direct connection successful!")
    conn.close()
except Exception as e:
    print(f"Direct connection error: {e}")

# Try with connection string
try:
    conn_string = "postgresql://auth_user:1234@localhost/auth_db"
    conn = psycopg2.connect(conn_string)
    print("Connection string successful!")
    conn.close()
except Exception as e:
    print(f"Connection string error: {e}")