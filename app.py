from flask import Flask, render_template
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = Flask(__name__)

def get_connection_string():
    """Get connection string with validation"""
    conn_str = os.getenv('DB_CONNECTION_STRING')
    if not conn_str:
        raise ValueError("DB_CONNECTION_STRING is not set in environment variables")
    return conn_str

@app.route('/')
def index():
    """Main endpoint with proper error handling"""
    try:
        conn_str = get_connection_string()
        print(f"Using connection string: {conn_str[:30]}...")  # Log first 30 chars
        
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Products")
            products = cursor.fetchall()
            return render_template('index.html', products=products)
            
    except Exception as e:
        error_msg = f"Error loading products: {str(e)}"
        print(error_msg)  # This will appear in Azure logs
        return error_msg, 500

if __name__ == '__main__':
    app.run()
