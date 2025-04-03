from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # Load environment variables

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')  # Required for flash messages

# Database connection
def get_db_connection():
    conn = pyodbc.connect(
        os.getenv('DB_CONNECTION_STRING')
    )
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all products with category and supplier information
    cursor.execute("""
        SELECT p.*, c.CategoryName, s.SupplierName 
        FROM Products p 
        LEFT JOIN Categories c ON p.CategoryID = c.CategoryID 
        LEFT JOIN Suppliers s ON p.SupplierID = s.SupplierID
        WHERE p.IsActive = 1
        ORDER BY p.ProductName
    """)
    products = cursor.fetchall()
    
    # Get categories for dropdown
    cursor.execute("SELECT * FROM Categories ORDER BY CategoryName")
    categories = cursor.fetchall()
    
    # Get suppliers for dropdown
    cursor.execute("SELECT * FROM Suppliers ORDER BY SupplierName")
    suppliers = cursor.fetchall()
    
    conn.close()
    return render_template('index.html', products=products, categories=categories, suppliers=suppliers)

@app.route('/add', methods=['POST'])
def add_product():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate SKU (you might want to implement your own SKU generation logic)
        sku = f"SKU-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute("""
            INSERT INTO Products (
                SKU, ProductName, Description, CategoryID, SupplierID,
                CostPrice, SellingPrice, QuantityInStock, MinimumStockLevel,
                LocationCode, Barcode, IsActive, WeightKG, Dimensions, Notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
        """, (
            sku,
            request.form['ProductName'],
            request.form['Description'],
            request.form['CategoryID'],
            request.form.get('SupplierID'),  # Optional field
            request.form['CostPrice'],
            request.form['SellingPrice'],
            request.form['QuantityInStock'],
            request.form.get('MinimumStockLevel', 5),
            request.form.get('LocationCode'),
            request.form.get('Barcode'),
            request.form.get('WeightKG'),
            request.form.get('Dimensions'),
            request.form.get('Notes')
        ))
        conn.commit()
        flash('Product added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding product: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('index'))

@app.route('/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Products 
            SET ProductName = ?, Description = ?, CategoryID = ?, SupplierID = ?,
                CostPrice = ?, SellingPrice = ?, QuantityInStock = ?, 
                MinimumStockLevel = ?, LocationCode = ?, Barcode = ?,
                WeightKG = ?, Dimensions = ?, Notes = ?, LastUpdated = GETDATE()
            WHERE ProductID = ?
        """, (
            request.form['ProductName'],
            request.form['Description'],
            request.form['CategoryID'],
            request.form.get('SupplierID'),
            request.form['CostPrice'],
            request.form['SellingPrice'],
            request.form['QuantityInStock'],
            request.form.get('MinimumStockLevel', 5),
            request.form.get('LocationCode'),
            request.form.get('Barcode'),
            request.form.get('WeightKG'),
            request.form.get('Dimensions'),
            request.form.get('Notes'),
            product_id
        ))
        conn.commit()
        flash('Product updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating product: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Soft delete by setting IsActive to 0
        cursor.execute("UPDATE Products SET IsActive = 0 WHERE ProductID = ?", (product_id,))
        conn.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
