# database.py
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='todolist',
            user='root',           # ← MUDE SE NECESSÁRIO
            password='SUA_SENHA',  # ← COLOQUE A SENHA CORRETA AQUI
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None