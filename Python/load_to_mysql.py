import os
import csv
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load env variables if available
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ecommerce_analytics")

print("MySQL Loader configuration:")
print(f" - Host: {DB_HOST}")
print(f" - User: {DB_USER}")
print(f" - Database: {DB_NAME}")

def get_db_connection(use_db=True):
    try:
        if use_db:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        else:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD
            )
        return conn
    except Error as e:
        print(f"Connection Error: {e}")
        return None

def execute_sql_file(filename, conn):
    if not os.path.exists(filename):
        print(f"SQL file {filename} not found.")
        return False
    
    print(f"Executing SQL schema file: {filename}...")
    cursor = conn.cursor()
    
    with open(filename, 'r', encoding='utf-8') as f:
        sql_content = f.read()
        
    # Split queries by semicolon (simple splitter, handling comments)
    queries = sql_content.split(';')
    for query in queries:
        clean_query = query.strip()
        if not clean_query:
            continue
        # Skip commented lines
        if clean_query.startswith('--') or clean_query.startswith('/*'):
            continue
        try:
            cursor.execute(clean_query)
        except Error as e:
            # We ignore errors about database already exists if creating it
            if "database exists" in str(e).lower() or "table already exists" in str(e).lower():
                continue
            print(f"Error executing query:\n{clean_query[:100]}...\nReason: {e}")
            
    conn.commit()
    cursor.close()
    print("Schema executed successfully.")
    return True

def load_csv_to_table(csv_path, table_name, columns, conn):
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return False
    
    cursor = conn.cursor()
    
    # Check if table already has records
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Table '{table_name}' already contains {count} records. Truncating to reload...")
        # Disable foreign keys temporarily to truncate
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        
    print(f"Loading data from {csv_path} into table '{table_name}'...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # skip headers
        
        # Build query placeholders: INSERT INTO table (col1, col2) VALUES (%s, %s)
        cols_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"
        
        batch = []
        batch_size = 1000
        total_inserted = 0
        
        for row in reader:
            # Handle empty strings as None (NULL in MySQL)
            row_clean = [None if val == "" else val for val in row]
            batch.append(row_clean)
            
            if len(batch) >= batch_size:
                cursor.executemany(query, batch)
                conn.commit()
                total_inserted += len(batch)
                batch = []
                
        if batch:
            cursor.executemany(query, batch)
            conn.commit()
            total_inserted += len(batch)
            
    cursor.close()
    print(f"Successfully loaded {total_inserted} records into '{table_name}'.")
    return True

def main():
    print("Connecting to MySQL Server to initialize database...")
    # First connect without database to create it
    conn = get_db_connection(use_db=False)
    if not conn:
        print("\nCould not connect to MySQL server.")
        print("Please ensure MySQL is running locally and credentials in your environment are correct.")
        print("Skipping bulk loading. SQL schema and queries have been generated for you to run manually.")
        return
        
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.commit()
    cursor.close()
    conn.close()
    
    # Reconnect to target database
    conn = get_db_connection(use_db=True)
    if not conn:
        print("Could not connect to database after creating it.")
        return
        
    # Execute schema
    if not execute_sql_file("SQL/schema.sql", conn):
        print("Failed to set up schema. Aborting loader.")
        conn.close()
        return

    # In e-commerce, load order is critical due to foreign key relationships:
    # 1. Categories
    # 2. Sellers
    # 3. Customers
    # 4. Products (depends on Categories)
    # 5. Orders (depends on Customers)
    # 6. Order Items (depends on Orders, Products, Sellers)
    # 7. Payments (depends on Orders)
    # 8. Shipping (depends on Orders)
    # 9. Reviews (depends on Orders)
    # 10. Returns (depends on Orders, Products)
    
    load_sequence = [
        ("Dataset/cleaned/categories.csv", "categories", ["product_category_name", "product_category_name_english"]),
        ("Dataset/cleaned/sellers.csv", "sellers", ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"]),
        ("Dataset/cleaned/customers.csv", "customers", ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"]),
        ("Dataset/cleaned/products.csv", "products", ["product_id", "product_category_name", "product_name_length", "product_description_length", "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm", "product_base_price"]),
        ("Dataset/cleaned/orders.csv", "orders", ["order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]),
        ("Dataset/cleaned/order_items.csv", "order_items", ["order_item_id", "order_id", "product_id", "seller_id", "price", "freight_value", "quantity"]),
        ("Dataset/cleaned/payments.csv", "payments", ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"]),
        ("Dataset/cleaned/shipping.csv", "shipping", ["shipping_id", "order_id", "shipping_carrier", "shipping_tracking_number", "shipping_estimated_delivery_date", "shipping_actual_delivery_date", "shipping_status"]),
        ("Dataset/cleaned/reviews.csv", "reviews", ["review_id", "order_id", "review_score", "review_comment_title", "review_comment_message", "review_creation_date", "review_answer_timestamp"]),
        ("Dataset/cleaned/returns.csv", "returns", ["return_id", "order_id", "product_id", "return_reason", "return_date", "return_status"])
    ]
    
    print("\nStarting bulk data load...")
    success = True
    for csv_path, table_name, columns in load_sequence:
        if not load_csv_to_table(csv_path, table_name, columns, conn):
            print(f"Error loading table '{table_name}'. Stopping loader.")
            success = False
            break
            
    conn.close()
    if success:
        print("\nAll datasets loaded to MySQL database successfully!")
    else:
        print("\nFailed to load all datasets to MySQL database.")

if __name__ == "__main__":
    main()
