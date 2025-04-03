from flask import Flask, render_template, jsonify
import pyodbc
import os
from dotenv import load_dotenv
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AzureApp')

load_dotenv()  # Load environment variables

app = Flask(__name__)

def get_db_connection():
    """Enhanced DB connection with Azure-specific troubleshooting"""
    try:
        connection_string = os.getenv('DB_CONNECTION_STRING')
        
        # Debug: Print connection string (remove in production)
        logger.info(f"Attempting connection with: {connection_string[:30]}...") 
        
        # Azure-specific connection parameters
        conn = pyodbc.connect(
            connection_string,
            timeout=30  # Explicit timeout
        )
        logger.info("✅ Database connection established")
        return conn
    except pyodbc.InterfaceError as e:
        logger.error(f"Driver error: {str(e)}")
        raise
    except pyodbc.OperationalError as e:
        logger.error(f"Connection failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

@app.route('/health')
def health_check():
    """Azure-specific health endpoint"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return jsonify({
                "status": "healthy",
                "database": "accessible"
            }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "azure_help": "Check: 1) Firewall rules 2) Connection string 3) DB server status"
        }), 500

@app.route('/')
def index():
    """Main endpoint with Azure-optimized error handling"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Products")
            products = cursor.fetchall()
            return render_template('index.html', products=products)
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        return render_template('error.html', 
                            error="Service unavailable",
                            azure_tips=[
                                "Verify DB_CONNECTION_STRING in App Settings",
                                "Check Azure SQL firewall rules",
                                "Review App Service logs"
                            ]), 503

if __name__ == '__main__':
    # Azure App Service uses gunicorn, so this only runs locally
    app.run(host='0.0.0.0', port=5000, debug=True)
