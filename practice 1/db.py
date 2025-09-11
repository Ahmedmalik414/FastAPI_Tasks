import mysql.connector as mc

def get_connection():
    return mc.connect(
        host="localhost",
        user="root",
        password="03345265362", 
        database="taskdb"
    )
