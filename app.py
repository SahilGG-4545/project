from flask import Flask, render_template
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = Flask(__name__)

def test_db_connection():
    """Simple connection test that prints to logs"""
    try:
        conn = pyodbc.connect(os.getenv('DB_CONNECTION_STRING'))
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database test successful - Server is reachable")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

# Test connection immediately when app starts
print("=== Starting connection test ===")
test_db_connection()
print("=== Test completed ===")

@app.route('/')
def index():
    """Simplified main endpoint"""
    try:
        conn = pyodbc.connect(os.getenv('DB_CONNECTION_STRING'))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        conn.close()
        return render_template('index.html', products=products)
    except Exception as e:
        return f"Error loading products: {str(e)}", 500

if __name__ == '__main__':
    app.run()
