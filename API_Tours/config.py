import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("CATALOGO_DB_USER")
    MYSQL_PASSWORD = os.getenv("CATALOGO_DB_PASS")
    MYSQL_DB = os.getenv("CATALOGO_DB_NAME")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    
    CATALOGO_API_KEY = os.getenv("CATALOGO_API_KEY")