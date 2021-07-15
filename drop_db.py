# Script to drop database (useful for restructuring/rebuilding)
import Config
import sqlite3

connection = sqlite3.connect(Config.DB_FILE)

cursor = connection.cursor()

cursor.execute("""
    DROP TABLE stock_price
""")

cursor.execute("""
    DROP TABLE stock_price_minute
""")

cursor.execute("""
    DROP TABLE stock
""")

cursor.execute("""
    DROP TABLE strategy
""")

cursor.execute("""
    DROP TABLE stock_strategy
""")

connection.commit()
