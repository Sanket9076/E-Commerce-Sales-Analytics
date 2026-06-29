import os
import csv
import sqlite3

DB_PATH = "SQL/ecommerce_analytics.db"

print(f"Initializing SQLite Database at {DB_PATH}...")

# Ensure SQL folder exists
os.makedirs("SQL", exist_ok=True)

# Delete existing DB if any to reload fresh
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON;")

# Create SQLite tables schema
schema = """
-- 1. Categories
CREATE TABLE categories (
    product_category_name TEXT PRIMARY KEY,
    product_category_name_english TEXT NOT NULL
);

-- 2. Sellers
CREATE TABLE sellers (
    seller_id TEXT PRIMARY KEY,
    seller_zip_code_prefix TEXT,
    seller_city TEXT,
    seller_state TEXT
);

-- 3. Customers
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT NOT NULL,
    customer_zip_code_prefix TEXT,
    customer_city TEXT,
    customer_state TEXT
);

-- 4. Products
CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g REAL,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER,
    product_base_price REAL NOT NULL,
    FOREIGN KEY (product_category_name) REFERENCES categories (product_category_name) ON DELETE SET NULL
);

-- 5. Orders
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_status TEXT NOT NULL,
    order_purchase_timestamp TEXT NOT NULL,
    order_approved_at TEXT,
    order_delivered_carrier_date TEXT,
    order_delivered_customer_date TEXT,
    order_estimated_delivery_date TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE
);

-- 6. Order Items
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    seller_id TEXT NOT NULL,
    price REAL NOT NULL,
    freight_value REAL NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES sellers (seller_id) ON DELETE CASCADE
);

-- 7. Payments
CREATE TABLE payments (
    order_id TEXT NOT NULL,
    payment_sequential INTEGER NOT NULL DEFAULT 1,
    payment_type TEXT NOT NULL,
    payment_installments INTEGER NOT NULL DEFAULT 1,
    payment_value REAL NOT NULL,
    PRIMARY KEY (order_id, payment_sequential),
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);

-- 8. Shipping
CREATE TABLE shipping (
    shipping_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    shipping_carrier TEXT NOT NULL,
    shipping_tracking_number TEXT NOT NULL,
    shipping_estimated_delivery_date TEXT NOT NULL,
    shipping_actual_delivery_date TEXT,
    shipping_status TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);

-- 9. Reviews
CREATE TABLE reviews (
    review_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    review_score INTEGER NOT NULL,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TEXT NOT NULL,
    review_answer_timestamp TEXT,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);

-- 10. Returns
CREATE TABLE returns (
    return_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    return_reason TEXT NOT NULL,
    return_date TEXT NOT NULL,
    return_status TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
);

-- Optimization Indexes
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_purchase_timestamp ON orders(order_purchase_timestamp);
CREATE INDEX idx_items_product_id ON order_items(product_id);
CREATE INDEX idx_items_order_id ON order_items(order_id);
CREATE INDEX idx_products_category ON products(product_category_name);
"""

# Execute schema
cursor.executescript(schema)
conn.commit()
print("SQLite Database schema created successfully.")

# Load sequence mapping
load_sequence = [
    ("Dataset/cleaned/categories.csv", "categories", 2),
    ("Dataset/cleaned/sellers.csv", "sellers", 4),
    ("Dataset/cleaned/customers.csv", "customers", 5),
    ("Dataset/cleaned/products.csv", "products", 10),
    ("Dataset/cleaned/orders.csv", "orders", 8),
    ("Dataset/cleaned/order_items.csv", "order_items", 7),
    ("Dataset/cleaned/payments.csv", "payments", 5),
    ("Dataset/cleaned/shipping.csv", "shipping", 7),
    ("Dataset/cleaned/reviews.csv", "reviews", 7),
    ("Dataset/cleaned/returns.csv", "returns", 6)
]

for csv_path, table_name, num_cols in load_sequence:
    if not os.path.exists(csv_path):
        print(f"Cleaned CSV not found: {csv_path}")
        continue
    
    print(f"Loading {csv_path} into table '{table_name}'...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        placeholders = ", ".join(["?"] * num_cols)
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        
        batch = []
        for row in reader:
            row_clean = [None if val == "" else val for val in row]
            # Match number of columns
            if len(row_clean) < num_cols:
                row_clean.extend([None] * (num_cols - len(row_clean)))
            batch.append(row_clean)
            
        cursor.executemany(query, batch)
        conn.commit()
        print(f" Loaded {len(batch)} rows.")

conn.close()
print(f"Data loading complete! SQLite DB file created at {DB_PATH}.")
