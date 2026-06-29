import os
import csv
import random
import math
from datetime import datetime, timedelta

# Set random seed for reproducibility
random.seed(42)

# Ensure folders exist
os.makedirs("Dataset/raw", exist_ok=True)
os.makedirs("Dataset/cleaned", exist_ok=True)

print("Starting pure Python realistic E-Commerce data generation...")

# Helper to format datetime
def format_dt(dt):
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Helper to format date
def format_date(dt):
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d")

# ----------------------------------------------------
# 1. Categories Mapping
# ----------------------------------------------------
categories = {
    "electronics": "Electronics",
    "computers_accessories": "Computers & Accessories",
    "telephony": "Telephony/Mobile",
    "fashion_clothing": "Fashion & Apparel",
    "fashion_shoes": "Shoes & Footwear",
    "housewares": "Housewares",
    "home_appliances": "Home Appliances",
    "sports_leisure": "Sports & Leisure",
    "toys": "Toys & Games",
    "beauty_cosmetics": "Beauty & Cosmetics",
    "health_perfumery": "Health & Perfumery",
    "books_stationery": "Books & Stationery",
    "automotive": "Automotive Parts",
    "garden_tools": "Garden Tools",
    "office_furniture": "Office Furniture"
}

with open("Dataset/raw/categories.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["product_category_name", "product_category_name_english"])
    for k, v in categories.items():
        writer.writerow([k, v])

# ----------------------------------------------------
# 2. Generate Sellers (500 records)
# ----------------------------------------------------
num_sellers = 500
seller_ids = [f"sel_{i:04d}" for i in range(1, num_sellers + 1)]
states_pool = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "DF", "PE", "CE"]
states_weights = [0.4, 0.15, 0.1, 0.08, 0.07, 0.05, 0.05, 0.04, 0.03, 0.03]

seller_cities_map = {
    "SP": "São Paulo", "RJ": "Rio de Janeiro", "MG": "Belo Horizonte", "RS": "Porto Alegre",
    "PR": "Curitiba", "BA": "Salvador", "SC": "Florianópolis", "DF": "Brasília", "PE": "Recife", "CE": "Fortaleza"
}

sellers_data = []
for s_id in seller_ids:
    state = random.choices(states_pool, weights=states_weights)[0]
    city = seller_cities_map[state]
    zip_code = f"{random.randint(1000, 99999):05d}"
    sellers_data.append([s_id, zip_code, city, state])

with open("Dataset/raw/sellers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"])
    writer.writerows(sellers_data)

# ----------------------------------------------------
# 3. Generate Customers (40,000 unique customer profiles)
# ----------------------------------------------------
num_customers = 40000
customer_states_pool = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "DF", "PE", "CE", "GO", "ES"]
customer_states_weights = [0.35, 0.15, 0.1, 0.08, 0.07, 0.05, 0.05, 0.03, 0.03, 0.03, 0.03, 0.03]
customer_cities_map = {
    "SP": "São Paulo", "RJ": "Rio de Janeiro", "MG": "Belo Horizonte", "RS": "Porto Alegre",
    "PR": "Curitiba", "BA": "Salvador", "SC": "Florianópolis", "DF": "Brasília", "PE": "Recife",
    "CE": "Fortaleza", "GO": "Goiânia", "ES": "Vitória"
}

customers_data = []
for i in range(1, num_customers + 1):
    c_id = f"cus_{i:06d}"
    c_uniq = f"usr_{i:06d}"
    state = random.choices(customer_states_pool, weights=customer_states_weights)[0]
    city = customer_cities_map[state]
    
    # Introduce some null zip codes (0.5% rate) for data cleaning demo
    if random.random() < 0.005:
        zip_code = ""
    else:
        zip_code = f"{random.randint(1000, 99999):05d}"
        
    customers_data.append([c_id, c_uniq, zip_code, city, state])

# Inject 100 duplicate customer records
dup_customers = random.sample(customers_data, 100)
customers_data.extend(dup_customers)

with open("Dataset/raw/customers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"])
    writer.writerows(customers_data)

# ----------------------------------------------------
# 4. Generate Products (2,500 records)
# ----------------------------------------------------
num_products = 2500
product_ids = [f"prd_{i:05d}" for i in range(1, num_products + 1)]
prod_categories_list = list(categories.keys())
prod_categories_weights = [0.15, 0.08, 0.07, 0.12, 0.08, 0.08, 0.06, 0.08, 0.05, 0.06, 0.06, 0.04, 0.03, 0.02, 0.02]

category_price_ranges = {
    "electronics": (50, 800),
    "computers_accessories": (100, 1500),
    "telephony": (80, 1000),
    "fashion_clothing": (15, 120),
    "fashion_shoes": (30, 200),
    "housewares": (10, 150),
    "home_appliances": (120, 1000),
    "sports_leisure": (10, 300),
    "toys": (15, 150),
    "beauty_cosmetics": (10, 100),
    "health_perfumery": (15, 120),
    "books_stationery": (8, 60),
    "automotive": (20, 400),
    "garden_tools": (15, 250),
    "office_furniture": (80, 500)
}

products_data = []
outlier_indices = set(random.sample(range(num_products), 5))  # 5 extreme pricing outliers
anomaly_indices = set(random.sample(range(num_products), 10)) # 10 negative weights/prices

for idx, p_id in enumerate(product_ids):
    cat = random.choices(prod_categories_list, weights=prod_categories_weights)[0]
    low, high = category_price_ranges[cat]
    base_price = round(random.uniform(low, high), 2)
    weight = random.randint(100, 15000)
    length = random.randint(10, 100)
    height = random.randint(5, 80)
    width = random.randint(10, 80)
    
    # Inject deliberate cleaning anomalies
    if idx in outlier_indices:
        base_price = 99999.00
    elif idx in anomaly_indices:
        if idx % 2 == 0:
            base_price = -abs(base_price)
        else:
            weight = -abs(weight)
            
    products_data.append([
        p_id, cat,
        random.randint(20, 60),  # product_name_length
        random.randint(100, 1000), # product_description_length
        random.randint(1, 8),  # product_photos_qty
        weight, length, height, width, base_price
    ])

with open("Dataset/raw/products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "product_id", "product_category_name", "product_name_length",
        "product_description_length", "product_photos_qty", "product_weight_g",
        "product_length_cm", "product_height_cm", "product_width_cm", "product_base_price"
    ])
    writer.writerows(products_data)

# ----------------------------------------------------
# 5. Generate Orders & Order Items (~100k items across ~85k orders)
# ----------------------------------------------------
num_orders = 85000
start_date = datetime(2024, 1, 1)
end_date = datetime(2026, 6, 15)
date_range_days = (end_date - start_date).days

print(f"Planning {num_orders} orders over {date_range_days} days...")

# Generate transaction timestamps with seasonality
order_dates = []
for day in range(date_range_days):
    current_date = start_date + timedelta(days=day)
    # Trend: 1.0 -> 1.8 growth
    growth_factor = 1.0 + (day / date_range_days) * 0.8
    # Seasonality
    month = current_date.month
    month_factor = 1.0
    if month == 11:
        month_factor = 2.2
    elif month == 12:
        month_factor = 2.0
    elif month in [1, 2]:
        month_factor = 0.75
    
    # Weekday factor
    weekday = current_date.weekday()
    day_factor = 1.2 if weekday < 3 else 0.85
    
    # Poisson approximation for daily orders
    avg_orders = 80 * growth_factor * month_factor * day_factor
    # Quick random poisson approximation
    daily_orders = int(max(10, random.normalvariate(avg_orders, math.sqrt(avg_orders))))
    
    for _ in range(daily_orders):
        h = random.randint(0, 23)
        m = random.randint(0, 59)
        s = random.randint(0, 59)
        order_dates.append(current_date.replace(hour=h, minute=m, second=s))

order_dates = sorted(order_dates)
if len(order_dates) > num_orders:
    order_dates = order_dates[:num_orders]
else:
    num_orders = len(order_dates)

print(f"Actual orders to generate: {num_orders}")

# Set up unique user weights to simulate repeat buying (Pareto Principle)
# We will mapping orders to customer IDs
unique_users = [c[1] for c in customers_data[:num_customers]] # customer_unique_ids
# We assign weights: a small fraction of users are very active
user_weights = [1.0 / (i**0.7) for i in range(1, num_customers + 1)]
sum_weights = sum(user_weights)
user_weights = [w / sum_weights for w in user_weights]

# Map user to customer_id
user_to_customer_map = {}
for c in customers_data[:num_customers]:
    user_to_customer_map[c[1]] = c[0] # c[1]=unique_id, c[0]=customer_id

# Sample users based on Pareto weight
selected_users = random.choices(unique_users, weights=user_weights, k=num_orders)
selected_customer_ids = [user_to_customer_map[u] for u in selected_users]

order_ids = [f"ord_{i:06d}" for i in range(1, num_orders + 1)]
statuses_pool = ["delivered", "shipped", "processing", "canceled", "invoiced", "unavailable"]
statuses_weights = [0.97, 0.015, 0.005, 0.006, 0.002, 0.002]

orders_rows = []
shipping_records = []
review_records = []
return_records = []

shipping_carriers = ["FedEx", "DHL", "UPS", "USPS", "SpeedyShip"]
shipping_counter = 1
review_counter = 1
return_counter = 1

# Pre-map products popularity (20% products get 80% sales)
product_weights = [1.0 / (i**0.9) for i in range(1, num_products + 1)]
sum_p_weights = sum(product_weights)
product_weights = [w / sum_p_weights for w in product_weights]

# Pre-map product prices and categories
prod_meta = {}
for p in products_data:
    # p = [product_id, category, name_len, desc_len, photo_qty, weight, len, ht, wd, base_price]
    prod_meta[p[0]] = {"price": p[9], "cat": p[1]}

order_items_records = []
order_item_counter = 1

print("Looping through orders to generate sub-records...")

for idx, (order_id, cust_id, o_date) in enumerate(zip(order_ids, selected_customer_ids, order_dates)):
    status = random.choices(statuses_pool, weights=statuses_weights)[0]
    
    # Calculate delivery dates
    est_days = random.randint(7, 21)
    est_dt = o_date + timedelta(days=est_days)
    
    approved_dt = None
    carrier_dt = None
    delivered_dt = None
    
    if not (status == "canceled" and random.random() < 0.7):
        approved_dt = o_date + timedelta(hours=random.expovariate(10)) # average 6 mins
        
        if status not in ["processing", "invoiced"]:
            carrier_dt = approved_dt + timedelta(days=random.expovariate(0.66)) # average 1.5 days
            
            if status not in ["shipped"]:
                # Normal delivery time
                del_days = random.normalvariate(5, 3)
                delivered_dt = carrier_dt + timedelta(days=max(0.1, del_days))
    
    orders_rows.append([
        order_id, cust_id, status,
        format_dt(o_date), format_dt(approved_dt),
        format_dt(carrier_dt), format_dt(delivered_dt),
        format_dt(est_dt)
    ])
    
    # Generate Order Items
    num_items = random.choices([1, 2, 3, 4], weights=[0.85, 0.11, 0.03, 0.01])[0]
    order_price_total = 0.0
    order_freight_total = 0.0
    
    order_items_temp = []
    
    for _ in range(num_items):
        p_id = random.choices(product_ids, weights=product_weights)[0]
        base_pr = prod_meta[p_id]["price"]
        cat = prod_meta[p_id]["cat"]
        
        # Discounts
        disc = random.choices([0.0, 0.05, 0.1, 0.15, 0.2], weights=[0.6, 0.15, 0.1, 0.1, 0.05])[0]
        price = round(base_pr * (1 - disc), 2)
        freight = round(random.lognormvariate(2.5, 0.5), 2)
        qty = random.choices([1, 2, 3], weights=[0.95, 0.04, 0.01])[0]
        
        seller_id = random.choice(seller_ids)
        
        order_items_records.append([
            order_item_counter, order_id, p_id, seller_id, price, freight, qty
        ])
        
        order_price_total += price * qty
        order_freight_total += freight
        
        order_items_temp.append((p_id, price, qty, cat))
        order_item_counter += 1
        
    # Generate Payments
    num_pymts = random.choices([1, 2, 3], weights=[0.96, 0.03, 0.01])[0]
    total_val = round(order_price_total + order_freight_total, 2)
    p_types = random.choices(["credit_card", "boleto", "voucher", "debit_card"], weights=[0.73, 0.19, 0.05, 0.03], k=num_pymts)
    
    if num_pymts == 1:
        shares = [1.0]
    else:
        # Simple split
        shares = [random.random() for _ in range(num_pymts)]
        sum_shares = sum(shares)
        shares = [s / sum_shares for s in shares]
        
    payment_records = []
    for seq, p_type in enumerate(p_types, 1):
        pymt_val = round(total_val * shares[seq - 1], 2)
        if seq == num_pymts: # adjustment for rounding
            sum_prev = sum([round(total_val * s, 2) for s in shares[:seq-1]])
            pymt_val = round(total_val - sum_prev, 2)
            
        installments = random.choice([1, 2, 3, 4, 6, 10, 12]) if p_type == "credit_card" else 1
        payment_records.append([order_id, seq, p_type, installments, pymt_val])
        
    # Write payments directly or save them
    # For speed, write reviews, payments, shipping, returns sequentially or batch write them later
    
    # Shipping record
    ship_status = "pending"
    if status == "delivered":
        ship_status = "delivered"
    elif status == "shipped":
        ship_status = "in_transit"
    elif status == "canceled":
        ship_status = "failed"
        
    shipping_records.append([
        f"shp_{shipping_counter:06d}", order_id,
        random.choice(shipping_carriers), f"TRK{random.randint(1000000000, 9999999999)}",
        format_dt(est_dt), format_dt(delivered_dt), ship_status
    ])
    shipping_counter += 1
    
    # Reviews (80% rate)
    if random.random() <= 0.8:
        # Check delay
        delay = None
        if delivered_dt and est_dt:
            delay = (delivered_dt - est_dt).days
            
        if delay is None:
            if status == "canceled":
                score = random.choices([1, 2, 3], weights=[0.8, 0.15, 0.05])[0]
            else:
                score = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.1, 0.2, 0.3, 0.3])[0]
        elif delay > 3:
            score = random.choices([1, 2, 3, 4, 5], weights=[0.6, 0.2, 0.1, 0.05, 0.05])[0]
        elif delay > 0:
            score = random.choices([1, 2, 3, 4, 5], weights=[0.25, 0.25, 0.2, 0.2, 0.1])[0]
        else:
            score = random.choices([1, 2, 3, 4, 5], weights=[0.02, 0.03, 0.05, 0.2, 0.7])[0]
            
        review_comments = {
            5: ("Excellent", "Perfect item, fast delivery, highly recommended!"),
            4: ("Good product", "Arrived in good condition. Shipped fast."),
            3: ("Average", "Product is fine but shipping took longer than expected."),
            2: ("Disappointed", "Product quality is mediocre. Packaging was damaged."),
            1: ("Very bad", "Product arrived broken, or was extremely delayed. Do not buy.")
        }
        
        title, msg = review_comments[score]
        if random.random() < 0.4:
            title = ""
        if random.random() < 0.5:
            msg = ""
            
        rev_date = o_date + timedelta(days=random.randint(3, 15))
        ans_date = rev_date + timedelta(days=random.randint(1, 5))
        
        review_records.append([
            f"rev_{review_counter:06d}", order_id, score, title, msg,
            format_dt(rev_date), format_dt(ans_date)
        ])
        review_counter += 1
        
        # Returns probability (about 3% of orders with specific reasons)
        if status == "delivered":
            for item in order_items_temp:
                p_id, price, qty, cat = item
                ret_prob = 0.01
                if cat in ["fashion_clothing", "fashion_shoes"]:
                    ret_prob = 0.06
                elif cat in ["electronics", "computers_accessories"]:
                    ret_prob = 0.035
                    
                if score == 1:
                    ret_prob += 0.25
                elif score == 2:
                    ret_prob += 0.12
                    
                if random.random() < ret_prob:
                    ret_date = o_date + timedelta(days=random.randint(5, 30))
                    reason = random.choices(
                        ["defective", "wrong_item", "unsatisfied", "delayed_delivery"],
                        weights=[0.35, 0.25, 0.3, 0.1]
                    )[0]
                    ret_status = random.choices(["approved", "rejected", "pending"], weights=[0.85, 0.1, 0.05])[0]
                    
                    return_records.append([
                        f"ret_{return_counter:06d}", order_id, p_id, reason,
                        format_dt(ret_date), ret_status
                    ])
                    return_counter += 1

# Write payments, shipping, reviews, returns, and order_items to CSV
print("Writing orders and sub-records to CSV files...")

# Inject duplicate orders
dup_orders = random.sample(orders_rows, 50)
orders_rows.extend(dup_orders)

with open("Dataset/raw/orders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "order_id", "customer_id", "order_status", "order_purchase_timestamp",
        "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ])
    writer.writerows(orders_rows)

# Inject duplicate items
dup_items = random.sample(order_items_records, 100)
order_items_records.extend(dup_items)

with open("Dataset/raw/order_items.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["order_item_id", "order_id", "product_id", "seller_id", "price", "freight_value", "quantity"])
    writer.writerows(order_items_records)

# Write payments
payments_all = []
# Re-generate payments based on orders list to ensure consistency or dump the pre-calculated payment records.
# Since we didn't store payments array globally, let's regenerate payments cleanly based on order_items.
# To do it quickly:
order_to_items = {}
for item in order_items_records:
    # item = [seq, order_id, product_id, seller_id, price, freight, qty]
    o_id = item[1]
    if o_id not in order_to_items:
        order_to_items[o_id] = []
    order_to_items[o_id].append(item)

payments_rows = []
for o_id, items in order_to_items.items():
    o_price = sum([float(it[4]) * int(it[6]) for it in items])
    o_freight = sum([float(it[5]) for it in items])
    total_val = round(o_price + o_freight, 2)
    
    num_pymts = random.choices([1, 2, 3], weights=[0.96, 0.03, 0.01])[0]
    p_types = random.choices(["credit_card", "boleto", "voucher", "debit_card"], weights=[0.73, 0.19, 0.05, 0.03], k=num_pymts)
    
    if num_pymts == 1:
        shares = [1.0]
    else:
        shares = [random.random() for _ in range(num_pymts)]
        sum_shares = sum(shares)
        shares = [s / sum_shares for s in shares]
        
    for seq, p_type in enumerate(p_types, 1):
        pymt_val = round(total_val * shares[seq - 1], 2)
        if seq == num_pymts:
            sum_prev = sum([round(total_val * s, 2) for s in shares[:seq-1]])
            pymt_val = round(total_val - sum_prev, 2)
            
        installments = random.choice([1, 2, 3, 4, 6, 10, 12]) if p_type == "credit_card" else 1
        payments_rows.append([o_id, seq, p_type, installments, pymt_val])

with open("Dataset/raw/payments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"])
    writer.writerows(payments_rows)

# Write shipping
with open("Dataset/raw/shipping.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["shipping_id", "order_id", "shipping_carrier", "shipping_tracking_number", "shipping_estimated_delivery_date", "shipping_actual_delivery_date", "shipping_status"])
    writer.writerows(shipping_records)

# Write reviews
with open("Dataset/raw/reviews.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["review_id", "order_id", "review_score", "review_comment_title", "review_comment_message", "review_creation_date", "review_answer_timestamp"])
    writer.writerows(review_records)

# Write returns
with open("Dataset/raw/returns.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["return_id", "order_id", "product_id", "return_reason", "return_date", "return_status"])
    writer.writerows(return_records)

print(f"Generated raw data summary:")
print(f" - Customers: {len(customers_data)}")
print(f" - Products: {len(products_data)}")
print(f" - Sellers: {len(sellers_data)}")
print(f" - Orders: {len(orders_rows)}")
print(f" - Order Items: {len(order_items_records)}")
print(f" - Payments: {len(payments_rows)}")
print(f" - Shipping: {len(shipping_records)}")
print(f" - Reviews: {len(review_records)}")
print(f" - Returns: {len(return_records)}")
print("Data generation complete!")
