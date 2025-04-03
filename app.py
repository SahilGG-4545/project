from flask import Flask, render_template, request, redirect, url_for
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = Flask(__name__)

# Database connection with enhanced error handling
def get_db_connection():
    try:
        connection_string = os.getenv('DB_CONNECTION_STRING')
        print(f"Attempting connection with string: {connection_string}")  # Debug log
        
        conn = pyodbc.connect(connection_string)
        print("✅ Database connection successful!")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        raise  # Re-raise the exception for Flask to handle

@app.route('/health')
def health():
    """Simple health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return "OK - Database connection successful", 200
    except Exception as e:
        return f"Database connection failed: {str(e)}", 500

@app.route('/test-db')
def test_db():
    """Test database query endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 * FROM Products")
        result = cursor.fetchone()
        conn.close()
        return f"Success! First product: {result}", 200
    except Exception as e:
        return f"Query failed: {str(e)}", 500

@app.route('/')
def index():
    """Main endpoint with error handling"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        conn.close()
        return render_template('index.html', products=products)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)
