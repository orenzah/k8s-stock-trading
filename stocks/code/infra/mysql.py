import mysql.connector
import os

import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.propagate = False


class MySQLConnection:
    def __init__(self):
        self.cnx = self.open_connection()

    def __enter__(self):
        return self.cnx

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cnx.close()
        
    @staticmethod
    def open_connection(database: str = None):
        # Load MySQL connection parameters from environment variables
        mysql_host = os.getenv("MYSQL_HOST")        
        mysql_user = os.getenv("MYSQL_USER")
        mysql_password = os.getenv("MYSQL_PASSWORD")
        mysql_database = os.getenv("MYSQL_DATABASE")

        # Connect to MySQL
        cnx = mysql.connector.connect(
            host=mysql_host,            
            user=mysql_user,
            password=mysql_password,
            database=mysql_database
        )
        return cnx

    def get_cursor(self):
        return self.cnx.cursor()

    def commit(self):
        self.cnx.commit()
        
    def rollback(self):
        self.cnx.rollback()
        
    def insert_rows(self, table, columns, values):
        cursor = self.get_cursor()
        if len(columns) != len(values[0]):
            raise ValueError("Columns and values must have the same length")        
        cols = [f"`{col}`" for col in columns]
        cols = ", ".join(cols)     
                   
        data = []
        for row in values:
            row = [f"'{val}'" for val in row]
            row = ", ".join(row)
            data.append(f"({row})")
        data = ", ".join(data)
        
        
        query = f"""INSERT IGNORE INTO {table} ({cols}) VALUES {data}"""
        logger.debug(query)
        cursor.execute(query)
        self.commit()
        cursor.close()
        
    def insert_row(self, table, columns, values):
        cursor = self.get_cursor()
        if len(columns) != len(values):
            raise ValueError("Columns and values must have the same length")        
        cols = [f"`{col}`" for col in columns]
        cols = ", ".join(cols)     
                   
        data = [f"'{val}'" for val in values]
        data = ", ".join(data)
        
        
        query = f"INSERT IGNORE INTO {table} ({cols}) VALUES ({data})"
        logger.debug(query)
        cursor.execute(query)
        self.commit()
        cursor.close()
    
    def select(self, table, where=None, limit=None):
        cursor = self.get_cursor()
        query = f"SELECT * FROM {table}"
        if where:
            query += f" WHERE {where}"
        if limit:
            query += f" LIMIT {limit}"
        logger.debug(query)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def show_columns(self, table):
        cursor = self.get_cursor()
        query = f"SHOW COLUMNS FROM {table}"
        logger.debug(query)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
        
        
        
        
    def write(self, query):
        cursor = self.get_cursor()
        cursor.execute(query)
        self.commit()
        cursor.close()
        


