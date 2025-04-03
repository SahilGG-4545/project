from flask import Flask, render_template, request, redirect, url_for
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = pyodbc.connect(
        os.getenv('DB_CONNECTION_STRING')
    )
    return conn

# @app.route('/')
# def home():
#     return "Azure Deployment Successful!"

# @app.route('/health')
# def health():
#     return "OK", 200
    
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
