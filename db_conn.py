import os
import pymysql
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def get_db_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USERNAME"),
            password=os.getenv("MYSQL_PASSWORD"),
            db=os.getenv("MYSQL_DATABASE", "defaultdb"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
            read_timeout=10,
            write_timeout=10
        )
        return connection
    except pymysql.MySQLError as e:
        print("❌ Aiven DB connection failed:", e)
        return None
