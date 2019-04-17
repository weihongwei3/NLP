import psycopg2

def get_conn():
    conn = psycopg2.connect(database="postgres", user="postgres", password="123456", host="localhost",
                            port="5432")
    return conn