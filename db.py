import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="energy_db",
        user="brkkrdg",
        password="burakk000",
        port=5432
    )