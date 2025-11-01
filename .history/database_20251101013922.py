
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='todolist',
            user='root',
            password='senac123',  
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        if conn.is_connected():
            print("Conexão com MySQL bem-sucedida!")
            return conn
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None