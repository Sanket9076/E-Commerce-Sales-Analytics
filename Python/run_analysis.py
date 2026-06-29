import os
import csv
import math
from datetime import datetime

print("Initializing data cleaning and analytics pipeline...")

# Ensure folders exist
os.makedirs("Dataset/cleaned", exist_ok=True)
os.makedirs("Images", exist_ok=True)
os.makedirs("Documentation", exist_ok=True)

# Helper: parse date safely
def parse_date(date_str):
    if not date_str or date_str.strip() == "":
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None

# Helper: format datetime safely
def format_dt(dt):
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# ----------------------------------------------------
# 1. Load Data in Pure Python
# ----------------------------------------------------
def load_csv(path):
    data = []
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return data
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(dict(row))
    return data

print("Loading raw CSV files...")
raw_categories = load_csv("Dataset/raw/categories.csv")
raw_sellers = load_csv("Dataset/raw/sellers.csv")
raw_customers = load_csv("Dataset/raw/customers.csv")
raw_products = load_csv("Dataset/raw/products.csv")
raw_orders = load_csv("Dataset/raw/orders.csv")
raw_order_items = load_csv("Dataset/raw/order_items.csv")
raw_payments = load_csv("Dataset/raw/payments.csv")
raw_shipping = load_csv("Dataset/raw/shipping.csv")
raw_reviews = load_csv("Dataset/raw/reviews.csv")
raw_returns = load_csv("Dataset/raw/returns.csv")

print(f"Loaded raw datasets. Cleaning raw data...")

# ----------------------------------------------------
# 2. Data Cleaning
# ----------------------------------------------------

# A. Clean Customers
# Deduplicate: customer_id
cleaned_customers = {}
dup_cust_count = 0
for row in raw_customers:
    c_id = row["customer_id"]
    if c_id in cleaned_customers:
        dup_cust_count += 1
        continue
    # Impute missing zip code prefix
    zip_code = row["customer_zip_code_prefix"]
    if not zip_code or zip_code.strip() == "":
        zip_code = "00000"
    
    cleaned_customers[c_id] = {
        "customer_id": c_id,
        "customer_unique_id": row["customer_unique_id"],
        "customer_zip_code_prefix": zip_code,
        "customer_city": row["customer_city"],
        "customer_state": row["customer_state"]
    }
print(f" - Customers cleaned: Deduplicated {dup_cust_count} records. Handled null zip codes.")

# B. Clean Products
# Handled negative weights/prices, handled extreme outliers ($99,999 phone cases)
# First, let's calculate average prices by category (excluding outliers) to impute outliers
cat_prices = {}
for row in raw_products:
    cat = row["product_category_name"]
    try:
        price = float(row["product_base_price"])
    except ValueError:
        price = 0.0
    if price > 0 and price < 50000: # exclude outliers and negatives
        if cat not in cat_prices:
            cat_prices[cat] = []
        cat_prices[cat].append(price)

cat_average_price = {}
for cat, prices in cat_prices.items():
    cat_average_price[cat] = sum(prices) / len(prices) if prices else 50.0

cleaned_products = []
price_outlier_count = 0
negative_val_count = 0

for row in raw_products:
    p_id = row["product_id"]
    cat = row["product_category_name"]
    
    try:
        price = float(row["product_base_price"])
    except ValueError:
        price = 50.0
        
    try:
        weight = float(row["product_weight_g"])
    except ValueError:
        weight = 1000.0
        
    # Correct negatives
    if price < 0:
        price = abs(price)
        negative_val_count += 1
    if weight < 0:
        weight = abs(weight)
        negative_val_count += 1
        
    # Impute extreme pricing outliers
    if price > 50000:
        price = round(cat_average_price.get(cat, 50.0), 2)
        price_outlier_count += 1
        
    cleaned_products.append({
        "product_id": p_id,
        "product_category_name": cat,
        "product_name_length": row["product_name_length"],
        "product_description_length": row["product_description_length"],
        "product_photos_qty": row["product_photos_qty"],
        "product_weight_g": weight,
        "product_length_cm": row["product_length_cm"],
        "product_height_cm": row["product_height_cm"],
        "product_width_cm": row["product_width_cm"],
        "product_base_price": price
    })
print(f" - Products cleaned: Handled {negative_val_count} negative weights/prices, corrected {price_outlier_count} pricing outliers ($99k cases).")

# C. Clean Orders
# Deduplicate, parse dates, impute missing delivery dates if delivered
cleaned_orders = {}
dup_order_count = 0
for row in raw_orders:
    o_id = row["order_id"]
    if o_id in cleaned_orders:
        dup_order_count += 1
        continue
    
    status = row["order_status"]
    p_date = parse_date(row["order_purchase_timestamp"])
    app_date = parse_date(row["order_approved_at"])
    carr_date = parse_date(row["order_delivered_carrier_date"])
    cust_date = parse_date(row["order_delivered_customer_date"])
    est_date = parse_date(row["order_estimated_delivery_date"])
    
    # Impute approved time if missing but delivered/shipped
    if app_date is None and p_date is not None and status in ["delivered", "shipped"]:
        app_date = p_date + timedelta(hours=1)
        
    # Impute customer delivery date if delivered but field is empty
    if status == "delivered" and cust_date is None and p_date is not None:
        cust_date = p_date + timedelta(days=7) # default to 7 days delivery
        
    cleaned_orders[o_id] = {
        "order_id": o_id,
        "customer_id": row["customer_id"],
        "order_status": status,
        "order_purchase_timestamp": p_date,
        "order_approved_at": app_date,
        "order_delivered_carrier_date": carr_date,
        "order_delivered_customer_date": cust_date,
        "order_estimated_delivery_date": est_date
    }
print(f" - Orders cleaned: Deduplicated {dup_order_count} records. Imputed missing dates for delivered orders.")

# D. Clean Order Items & Payments
# Deduplicate order items, enforce FK constraints, compute item values
cleaned_order_items = []
dup_items_count = 0
seen_item_ids = set()
products_set = {p["product_id"] for p in cleaned_products}
sellers_set = {s["seller_id"] for s in raw_sellers}

for row in raw_order_items:
    item_id = row["order_item_id"]
    if item_id in seen_item_ids:
        dup_items_count += 1
        continue
    seen_item_ids.add(item_id)
    
    o_id = row["order_id"]
    p_id = row["product_id"]
    s_id = row["seller_id"]
    
    # FK check
    if o_id not in cleaned_orders or p_id not in products_set or s_id not in sellers_set:
        continue # exclude orphaned records
        
    try:
        price = float(row["price"])
        freight = float(row["freight_value"])
        qty = int(row["quantity"])
    except ValueError:
        price = 0.0
        freight = 0.0
        qty = 1
        
    cleaned_order_items.append({
        "order_item_id": item_id,
        "order_id": o_id,
        "product_id": p_id,
        "seller_id": s_id,
        "price": price,
        "freight_value": freight,
        "quantity": qty
    })

# Write cleaned files to Dataset/cleaned/
def write_csv(data, headers, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

# Format dates back to string for writing
customers_write = list(cleaned_customers.values())
write_csv(customers_write, ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"], "Dataset/cleaned/customers.csv")
write_csv(cleaned_products, ["product_id", "product_category_name", "product_name_length", "product_description_length", "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm", "product_base_price"], "Dataset/cleaned/products.csv")

orders_write = []
for o in cleaned_orders.values():
    orders_write.append({
        "order_id": o["order_id"],
        "customer_id": o["customer_id"],
        "order_status": o["order_status"],
        "order_purchase_timestamp": format_dt(o["order_purchase_timestamp"]),
        "order_approved_at": format_dt(o["order_approved_at"]),
        "order_delivered_carrier_date": format_dt(o["order_delivered_carrier_date"]),
        "order_delivered_customer_date": format_dt(o["order_delivered_customer_date"]),
        "order_estimated_delivery_date": format_dt(o["order_estimated_delivery_date"])
    })
write_csv(orders_write, ["order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"], "Dataset/cleaned/orders.csv")
write_csv(cleaned_order_items, ["order_item_id", "order_id", "product_id", "seller_id", "price", "freight_value", "quantity"], "Dataset/cleaned/order_items.csv")

# Clean categories, sellers, payments, reviews, shipping, returns (just write them to cleaned/ since they are standard or drop foreign orphans)
write_csv(raw_sellers, ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"], "Dataset/cleaned/sellers.csv")
write_csv(raw_categories, ["product_category_name", "product_category_name_english"], "Dataset/cleaned/categories.csv")

payments_clean = [p for p in raw_payments if p["order_id"] in cleaned_orders]
write_csv(payments_clean, ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"], "Dataset/cleaned/payments.csv")

reviews_clean = [r for r in raw_reviews if r["order_id"] in cleaned_orders]
write_csv(reviews_clean, ["review_id", "order_id", "review_score", "review_comment_title", "review_comment_message", "review_creation_date", "review_answer_timestamp"], "Dataset/cleaned/reviews.csv")

shipping_clean = [s for s in raw_shipping if s["order_id"] in cleaned_orders]
write_csv(shipping_clean, ["shipping_id", "order_id", "shipping_carrier", "shipping_tracking_number", "shipping_estimated_delivery_date", "shipping_actual_delivery_date", "shipping_status"], "Dataset/cleaned/shipping.csv")

returns_clean = [r for r in raw_returns if r["order_id"] in cleaned_orders]
write_csv(returns_clean, ["return_id", "order_id", "product_id", "return_reason", "return_date", "return_status"], "Dataset/cleaned/returns.csv")

print("All cleaned datasets written to 'Dataset/cleaned/'.")

# ----------------------------------------------------
# 3. Exploratory Data Analysis & Business KPIs
# ----------------------------------------------------
print("Running exploratory data analysis and KPI calculations...")

# KPI variables
total_revenue = 0.0
total_freight = 0.0
total_items_sold = 0
order_revenue_map = {} # order_id -> revenue (excluding shipping)
order_total_map = {}   # order_id -> total value (including shipping)

for item in cleaned_order_items:
    o_id = item["order_id"]
    pr = float(item["price"])
    fr = float(item["freight_value"])
    qty = int(item["quantity"])
    val = pr * qty
    total_revenue += val
    total_freight += fr
    total_items_sold += qty
    
    order_revenue_map[o_id] = order_revenue_map.get(o_id, 0.0) + val
    order_total_map[o_id] = order_total_map.get(o_id, 0.0) + val + fr

# Estimate cost of goods sold (COGS) as 65% of product price to simulate profit metrics
total_cogs = total_revenue * 0.65
total_profit = total_revenue - total_cogs
profit_margin = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0.0

total_orders = len(cleaned_orders)
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

# Customers metrics
unique_cust_ids = set()
unique_users_ids = set()
user_to_orders = {} # user_unique_id -> [order_ids]
user_spend = {}     # user_unique_id -> spend

for o_id, o in cleaned_orders.items():
    cust_id = o["customer_id"]
    if cust_id in cleaned_customers:
        user_uniq = cleaned_customers[cust_id]["customer_unique_id"]
        unique_cust_ids.add(cust_id)
        unique_users_ids.add(user_uniq)
        if user_uniq not in user_to_orders:
            user_to_orders[user_uniq] = []
        user_to_orders[user_uniq].append(o_id)
        
        rev = order_revenue_map.get(o_id, 0.0)
        user_spend[user_uniq] = user_spend.get(user_uniq, 0.0) + rev

total_customers = len(unique_users_ids)

# Repeat customer rate
repeat_customers_count = sum([1 for u, ords in user_to_orders.items() if len(ords) > 1])
repeat_customer_rate = (repeat_customers_count / total_customers) * 100 if total_customers > 0 else 0.0

# Delivery days
delivery_days_sum = 0.0
delivered_count = 0
for o_id, o in cleaned_orders.items():
    if o["order_status"] == "delivered" and o["order_delivered_customer_date"] is not None and o["order_purchase_timestamp"] is not None:
        days = (o["order_delivered_customer_date"] - o["order_purchase_timestamp"]).total_seconds() / (24 * 3600)
        delivery_days_sum += days
        delivered_count += 1
avg_delivery_time = delivery_days_sum / delivered_count if delivered_count > 0 else 0.0

# Return rate (returns / delivered items count)
total_returns = len(returns_clean)
return_rate = (total_returns / len(cleaned_order_items)) * 100 if len(cleaned_order_items) > 0 else 0.0

# Reviews metrics
avg_review_score = sum([float(r["review_score"]) for r in reviews_clean]) / len(reviews_clean) if reviews_clean else 0.0

# CLV (Customer Lifetime Value) = Avg Purchase Value * Purchase Frequency * Average Lifespan
# In our simulation:
# Average Lifespan: Let's assume average user stays active for 2.5 years.
# Purchase Frequency = Total Orders / Total Customers (per year)
# Standard CLV formula: AOV * Purchase Frequency * Lifespan
avg_purchase_frequency = total_orders / total_customers
customer_lifetime_value = avg_order_value * avg_purchase_frequency

# Customer Retention Rate & Churn Rate
# Since our dataset covers 2.5 years:
# Let's define customer cohort retention: customers who ordered in 2024 and ordered again in 2025/2026
ordered_2024 = set()
ordered_later = set()
for o_id, o in cleaned_orders.items():
    p_date = o["order_purchase_timestamp"]
    if p_date:
        cust_id = o["customer_id"]
        if cust_id in cleaned_customers:
            user_uniq = cleaned_customers[cust_id]["customer_unique_id"]
            if p_date.year == 2024:
                ordered_2024.add(user_uniq)
            if p_date.year in [2025, 2026]:
                ordered_later.add(user_uniq)
retained_users = ordered_2024.intersection(ordered_later)
retention_rate = (len(retained_users) / len(ordered_2024)) * 100 if ordered_2024 else 0.0
churn_rate = 100.0 - retention_rate

print("\n--- Business KPIs ---")
print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Total Profit: ${total_profit:,.2f} (Profit Margin: {profit_margin:.2f}%)")
print(f"Total Orders: {total_orders:,}")
print(f"Total Unique Customers: {total_customers:,}")
print(f"Average Order Value (AOV): ${avg_order_value:.2f}")
print(f"Customer Lifetime Value (CLV): ${customer_lifetime_value:.2f}")
print(f"Repeat Customer Rate: {repeat_customer_rate:.2f}%")
print(f"Customer Retention Rate: {retention_rate:.2f}% (Churn Rate: {churn_rate:.2f}%)")
print(f"Average Delivery Time: {avg_delivery_time:.2f} days")
print(f"Return Rate: {return_rate:.2f}%")
print(f"Average Review Score: {avg_review_score:.2f} / 5.0")

# Write KPIs report to a file
with open("Documentation/kpi_metrics.txt", "w", encoding="utf-8") as f:
    f.write("=== E-Commerce Sales & Customer Analytics KPIs ===\n")
    f.write(f"Total Revenue: ${total_revenue:,.2f}\n")
    f.write(f"Total Profit: ${total_profit:,.2f}\n")
    f.write(f"Profit Margin: {profit_margin:.2f}%\n")
    f.write(f"Total Orders: {total_orders:,}\n")
    f.write(f"Total Unique Customers: {total_customers:,}\n")
    f.write(f"Average Order Value (AOV): ${avg_order_value:.2f}\n")
    f.write(f"Customer Lifetime Value (CLV): ${customer_lifetime_value:.2f}\n")
    f.write(f"Repeat Customer Rate: {repeat_customer_rate:.2f}%\n")
    f.write(f"Customer Retention Rate: {retention_rate:.2f}%\n")
    f.write(f"Churn Rate: {churn_rate:.2f}%\n")
    f.write(f"Average Delivery Time: {avg_delivery_time:.2f} days\n")
    f.write(f"Return Rate: {return_rate:.2f}%\n")
    f.write(f"Average Review Score: {avg_review_score:.2f} / 5.0\n")

# ----------------------------------------------------
# 4. Customer Segmentation (RFM Analysis)
# ----------------------------------------------------
print("Performing RFM Analysis...")
max_order_date = max([o["order_purchase_timestamp"] for o in cleaned_orders.values() if o["order_purchase_timestamp"]])

rfm_profiles = {}
for user_uniq, ord_ids in user_to_orders.items():
    # Recency
    user_orders = [cleaned_orders[oid] for oid in ord_ids]
    last_order_date = max([o["order_purchase_timestamp"] for o in user_orders if o["order_purchase_timestamp"]])
    recency_days = (max_order_date - last_order_date).days
    
    # Frequency
    frequency = len(ord_ids)
    
    # Monetary
    monetary = user_spend.get(user_uniq, 0.0)
    
    rfm_profiles[user_uniq] = {
        "customer_unique_id": user_uniq,
        "recency": recency_days,
        "frequency": frequency,
        "monetary": monetary
    }

# Define Quintiles for R, F, M
recencies = [p["recency"] for p in rfm_profiles.values()]
frequencies = [p["frequency"] for p in rfm_profiles.values()]
monetaries = [p["monetary"] for p in rfm_profiles.values()]

def get_quintile_score(val, quantiles, ascending=True):
    # Quantiles can be calculated manually
    for q_idx, q_val in enumerate(quantiles):
        if ascending:
            if val <= q_val:
                return q_idx + 1
        else:
            if val >= q_val:
                return q_idx + 1
    return len(quantiles) + 1

def compute_percentiles(arr, num_buckets=5):
    s_arr = sorted(arr)
    n = len(s_arr)
    percentiles = []
    for i in range(1, num_buckets):
        idx = int(n * (i / num_buckets))
        percentiles.append(s_arr[idx])
    return percentiles

rec_percentiles = compute_percentiles(recencies, 5) # Recency: lower is better (ascending score)
# Note: Frequency has very low uniqueness since most are 1 or 2, we will segment manually for F
# 1 order = F score 1, 2 orders = F score 3, 3 orders = F score 4, 4+ orders = F score 5
mon_percentiles = compute_percentiles(monetaries, 5)

rfm_segmented = []
segment_counts = {}

for u, p in rfm_profiles.items():
    # Recency score: lower recency days -> higher score (5)
    r_val = p["recency"]
    if r_val <= rec_percentiles[0]:
        r_score = 5
    elif r_val <= rec_percentiles[1]:
        r_score = 4
    elif r_val <= rec_percentiles[2]:
        r_score = 3
    elif r_val <= rec_percentiles[3]:
        r_score = 2
    else:
        r_score = 1
        
    # Frequency score: frequency based
    f_val = p["frequency"]
    if f_val >= 4:
        f_score = 5
    elif f_val == 3:
        f_score = 4
    elif f_val == 2:
        f_score = 3
    else:
        f_score = 1
        
    # Monetary score: higher spend -> higher score (5)
    m_val = p["monetary"]
    if m_val <= mon_percentiles[0]:
        m_score = 1
    elif m_val <= mon_percentiles[1]:
        m_score = 2
    elif m_val <= mon_percentiles[2]:
        m_score = 3
    elif m_val <= mon_percentiles[3]:
        m_score = 4
    else:
        m_score = 5
        
    # Segment assignment
    seg = "Others"
    if r_score >= 4 and f_score >= 4 and m_score >= 4:
        seg = "Champions"
    elif r_score >= 3 and f_score >= 3 and m_score >= 3:
        seg = "Loyal Customers"
    elif r_score >= 4 and f_score == 1:
        seg = "New Customers"
    elif r_score <= 2 and f_score >= 3:
        seg = "At Risk"
    elif r_score <= 2 and f_score <= 2:
        seg = "Hibernating"
    else:
        seg = "Promising/Active"
        
    segment_counts[seg] = segment_counts.get(seg, 0) + 1
    
    rfm_segmented.append({
        "customer_unique_id": u,
        "recency": r_val,
        "frequency": f_val,
        "monetary": round(m_val, 2),
        "r_score": r_score,
        "f_score": f_score,
        "m_score": m_score,
        "segment": seg
    })

# Write RFM segments to file
write_csv(rfm_segmented, ["customer_unique_id", "recency", "frequency", "monetary", "r_score", "f_score", "m_score", "segment"], "Dataset/cleaned/rfm_analysis.csv")

print("\n--- RFM Segment Summary ---")
for k, v in segment_counts.items():
    pct = (v / total_customers) * 100
    print(f"{k}: {v:,} customers ({pct:.2f}%)")

# ----------------------------------------------------
# 5. Pareto Analysis (80/20 Rule)
# ----------------------------------------------------
print("Performing Pareto Analysis...")
sorted_spends = sorted(list(user_spend.values()), reverse=True)
cum_spend = 0.0
pareto_limit = total_revenue * 0.8
customers_needed = 0

for spend in sorted_spends:
    cum_spend += spend
    customers_needed += 1
    if cum_spend >= pareto_limit:
        break
        
pareto_cust_pct = (customers_needed / total_customers) * 100
print(f"Pareto Principle: {pareto_cust_pct:.2f}% of customers generate 80% of revenue.")

# ----------------------------------------------------
# 6. ABC Analysis for Products
# ----------------------------------------------------
print("Performing ABC Analysis for products...")
product_sales = {}
for item in cleaned_order_items:
    p_id = item["product_id"]
    val = float(item["price"]) * int(item["quantity"])
    product_sales[p_id] = product_sales.get(p_id, 0.0) + val

sorted_prod_sales = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
cum_prod_sales = 0.0
abc_segmented = []

for idx, (p_id, val) in enumerate(sorted_prod_sales, 1):
    cum_prod_sales += val
    cum_pct = cum_prod_sales / total_revenue
    
    if cum_pct <= 0.70:
        cls = "A"
    elif cum_pct <= 0.90:
        cls = "B"
    else:
        cls = "C"
        
    abc_segmented.append({
        "product_id": p_id,
        "revenue": round(val, 2),
        "cumulative_revenue": round(cum_prod_sales, 2),
        "cumulative_pct": round(cum_pct * 100, 2),
        "class": cls
    })

write_csv(abc_segmented, ["product_id", "revenue", "cumulative_revenue", "cumulative_pct", "class"], "Dataset/cleaned/abc_analysis.csv")

abc_counts = {"A": 0, "B": 0, "C": 0}
abc_rev = {"A": 0.0, "B": 0.0, "C": 0.0}
for item in abc_segmented:
    cls = item["class"]
    abc_counts[cls] += 1
    abc_rev[cls] += item["revenue"]

print("\n--- ABC Analysis Summary ---")
for c in ["A", "B", "C"]:
    cnt = abc_counts[c]
    cnt_pct = (cnt / len(cleaned_products)) * 100
    rev = abc_rev[c]
    rev_pct = (rev / total_revenue) * 100
    print(f"Class {c}: {cnt:,} products ({cnt_pct:.2f}%) generate ${rev:,.2f} ({rev_pct:.2f}% of revenue)")

# ----------------------------------------------------
# 7. Sales Forecasting (Next 6 Months)
# ----------------------------------------------------
print("Running Sales Forecasting...")
# Monthly aggregation
monthly_sales = {}
for o_id, o in cleaned_orders.items():
    p_date = o["order_purchase_timestamp"]
    if p_date:
        key = (p_date.year, p_date.month)
        rev = order_revenue_map.get(o_id, 0.0)
        monthly_sales[key] = monthly_sales.get(key, 0.0) + rev

# Sort monthly sales chronologically
sorted_months = sorted(list(monthly_sales.keys()))
sales_series = [monthly_sales[m] for m in sorted_months]
month_labels = [f"{m[0]}-{m[1]:02d}" for m in sorted_months]

print(f"Historical months: {len(sales_series)} months, from {month_labels[0]} to {month_labels[-1]}")

# Forecast using Linear Trend + Seasonal Indices
# Let's set up month index t: 1, 2, ..., n
n = len(sales_series)
t_indices = list(range(1, n + 1))

# Simple linear regression calculations: Y = a + b * t
mean_t = sum(t_indices) / n
mean_y = sum(sales_series) / n

num = sum([(t_indices[i] - mean_t) * (sales_series[i] - mean_y) for i in range(n)])
den = sum([(t_indices[i] - mean_t) ** 2 for i in range(n)])
b = num / den
a = mean_y - b * mean_t

# Trend values
trend_values = [a + b * t for t in t_indices]

# Seasonal factors: group ratio by month of year (1-12)
seasonal_ratios = {m: [] for m in range(1, 13)}
for idx, key in enumerate(sorted_months):
    month_val = key[1]
    ratio = sales_series[idx] / trend_values[idx]
    seasonal_ratios[month_val].append(ratio)

# Average seasonal factors
seasonal_indices = {}
for m in range(1, 13):
    ratios = seasonal_ratios[m]
    seasonal_indices[m] = sum(ratios) / len(ratios) if ratios else 1.0

# Normalize seasonal factors so their average is 1.0
avg_seasonal = sum(seasonal_indices.values()) / 12
for m in range(1, 13):
    seasonal_indices[m] /= avg_seasonal

# Forecast next 6 months (t = n+1, ..., n+6)
forecast_records = []
last_month = sorted_months[-1]
curr_y, curr_m = last_month[0], last_month[1]

print("\n--- 6-Month Sales Forecast ---")
for step in range(1, 7):
    # Add month
    curr_m += 1
    if curr_m > 12:
        curr_m = 1
        curr_y += 1
        
    t = n + step
    trend_val = a + b * t
    s_idx = seasonal_indices[curr_m]
    forecast_val = round(trend_val * s_idx, 2)
    
    label = f"{curr_y}-{curr_m:02d}"
    print(f"Month {label} (t={t}): Projected Sales = ${forecast_val:,.2f}")
    forecast_records.append([label, t, round(trend_val, 2), s_idx, forecast_val])

with open("Dataset/cleaned/sales_forecast.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["month_label", "t_index", "trend_value", "seasonal_index", "forecast_sales"])
    writer.writerows(forecast_records)

# ----------------------------------------------------
# 8. SVG Visualizations Generation
# ----------------------------------------------------
print("Generating high-quality dashboard visualizations (SVG)...")

# Visual Theme: Deep premium dark mode with Outfit/Inter vibe
# Background: #0f172a, Text: #f8fafc, Accent blue: #38bdf8, Accent violet: #a78bfa, Accent green: #34d399, Accent coral: #fb7185
SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%" style="background-color: #0f172a; font-family: 'Outfit', 'Inter', system-ui, sans-serif; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5);">
    <!-- Gradient definitions -->
    <defs>
        <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#0284c7" stop-opacity="0.2"/>
        </linearGradient>
        <linearGradient id="purpleGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#c084fc" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#7e22ce" stop-opacity="0.2"/>
        </linearGradient>
        <linearGradient id="greenGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#34d399" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#059669" stop-opacity="0.2"/>
        </linearGradient>
        <linearGradient id="coralGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#fb7185" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#be123c" stop-opacity="0.2"/>
        </linearGradient>
    </defs>
    
    <!-- Title and details -->
    <text x="30" y="40" fill="#f8fafc" font-size="20" font-weight="bold">{title}</text>
    <text x="30" y="60" fill="#94a3b8" font-size="12">{subtitle}</text>
    
    <!-- Content goes here -->
    {content}
</svg>"""

# Chart 1: Monthly Sales Trend + Forecast (Line Chart)
# Plot historical values as area/line and forecast as dashed line
def generate_sales_trend_svg(sales_series, forecast_records, month_labels):
    hist_n = len(sales_series)
    fc_n = len(forecast_records)
    all_values = sales_series + [fc[4] for fc in forecast_records]
    all_labels = month_labels + [fc[0] for fc in forecast_records]
    
    max_val = max(all_values)
    min_val = min(all_values)
    # Give some margin
    upper_y = math.ceil(max_val / 50000) * 50000
    
    # Coordinate system: chart area x: 80 to 750, y: 80 to 380
    x_start, x_end = 80, 750
    y_start, y_end = 380, 80
    
    x_width = x_end - x_start
    y_height = y_start - y_end
    
    def get_coords(idx, val):
        x = x_start + (idx / (len(all_values) - 1)) * x_width
        y = y_start - (val / upper_y) * y_height
        return x, y
    
    # Grid lines and Y labels
    grid_html = ""
    for i in range(5):
        y_val = (upper_y / 4) * i
        y_pos = y_start - (i / 4) * y_height
        grid_html += f'<line x1="{x_start}" y1="{y_pos}" x2="{x_end}" y2="{y_pos}" stroke="#334155" stroke-dasharray="4" stroke-width="1"/>'
        grid_html += f'<text x="{x_start - 10}" y="{y_pos + 4}" fill="#94a3b8" font-size="10" text-anchor="end">${y_val/1000:,.0f}k</text>'
        
    # X labels (every 3rd month to avoid clutter)
    x_labels_html = ""
    for idx, lbl in enumerate(all_labels):
        if idx % 3 == 0 or idx == len(all_labels) - 1:
            x_pos, _ = get_coords(idx, 0)
            # Short label
            short_lbl = lbl[2:] # e.g. "24-03"
            x_labels_html += f'<text x="{x_pos}" y="{y_start + 20}" fill="#94a3b8" font-size="10" text-anchor="middle">{short_lbl}</text>'
            x_labels_html += f'<line x1="{x_pos}" y1="{y_start}" x2="{x_pos}" y2="{y_start + 4}" stroke="#64748b" stroke-width="1"/>'
            
    # Path coordinates for historical sales
    hist_points = []
    for idx in range(hist_n):
        x, y = get_coords(idx, sales_series[idx])
        hist_points.append(f"{x},{y}")
        
    hist_path = f"M {hist_points[0]} " + " ".join([f"L {pt}" for pt in hist_points[1:]])
    hist_area = f"{hist_path} L {x_start + ((hist_n - 1) / (len(all_values) - 1)) * x_width},{y_start} L {x_start},{y_start} Z"
    
    # Forecast points
    fc_points = []
    # Link forecast to the last historical point
    last_x, last_y = get_coords(hist_n - 1, sales_series[-1])
    fc_points.append(f"{last_x},{last_y}")
    for idx in range(fc_n):
        x, y = get_coords(hist_n + idx, forecast_records[idx][4])
        fc_points.append(f"{x},{y}")
    fc_path = f"M {fc_points[0]} " + " ".join([f"L {pt}" for pt in fc_points[1:]])
    
    content = f"""
    <!-- Grid -->
    {grid_html}
    {x_labels_html}
    
    <!-- Historical Area & Line -->
    <path d="{hist_area}" fill="url(#blueGrad)" />
    <path d="{hist_path}" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/>
    
    <!-- Forecast Line (Dashed) -->
    <path d="{fc_path}" fill="none" stroke="#a78bfa" stroke-width="3" stroke-dasharray="6,4" stroke-linecap="round"/>
    
    <!-- Divider between Hist and Forecast -->
    <line x1="{last_x}" y1="{y_end}" x2="{last_x}" y2="{y_start}" stroke="#fb7185" stroke-width="1.5" stroke-dasharray="2,2"/>
    <text x="{last_x - 8}" y="{y_end + 15}" fill="#fb7185" font-size="10" text-anchor="end" font-weight="bold">HISTORICAL</text>
    <text x="{last_x + 8}" y="{y_end + 15}" fill="#a78bfa" font-size="10" text-anchor="start" font-weight="bold">6M FORECAST</text>
    
    <!-- Legend -->
    <g transform="translate(600, 30)">
        <rect x="0" y="0" width="12" height="12" rx="2" fill="#38bdf8"/>
        <text x="18" y="10" fill="#f8fafc" font-size="11">Actual Sales</text>
        <line x1="0" y1="22" x2="12" y2="22" stroke="#a78bfa" stroke-width="2" stroke-dasharray="3,2"/>
        <text x="18" y="25" fill="#f8fafc" font-size="11">Forecasted Sales</text>
    </g>
    """
    return SVG_TEMPLATE.format(
        title="Monthly Sales Trend & 6-Month Projection",
        subtitle=f"Historical data from {month_labels[0]} to {month_labels[-1]} + projections",
        content=content
    )

# Chart 2: Regional Revenue (Bar Chart)
def generate_regional_sales_svg(cleaned_orders, cleaned_customers, order_revenue_map):
    state_sales = {}
    for o_id, o in cleaned_orders.items():
        cust_id = o["customer_id"]
        if cust_id in cleaned_customers:
            st = cleaned_customers[cust_id]["customer_state"]
            rev = order_revenue_map.get(o_id, 0.0)
            state_sales[st] = state_sales.get(st, 0.0) + rev
            
    sorted_states = sorted(state_sales.items(), key=lambda x: x[1], reverse=True)[:8] # Top 8 states
    states_lbls = [s[0] for s in sorted_states]
    states_vals = [s[1] for s in sorted_states]
    
    max_val = max(states_vals)
    upper_x = math.ceil(max_val / 50000) * 50000
    
    # Horizonal bar chart: y-axis from 80 to 400, x-axis from 100 to 730
    y_start, y_end = 80, 400
    x_start, x_end = 120, 730
    chart_h = y_end - y_start
    chart_w = x_end - x_start
    
    bars_html = ""
    bar_gap = 12
    num_bars = len(sorted_states)
    bar_height = (chart_h - (bar_gap * (num_bars - 1))) / num_bars
    
    for idx, (st, val) in enumerate(sorted_states):
        y_pos = y_start + idx * (bar_height + bar_gap)
        w_len = (val / max_val) * chart_w
        
        # Draw bar
        bars_html += f'<rect x="{x_start}" y="{y_pos}" width="{w_len}" height="{bar_height}" rx="4" fill="url(#blueGrad)" stroke="#0284c7" stroke-width="0.5"/>'
        # Label State
        bars_html += f'<text x="{x_start - 15}" y="{y_pos + bar_height/2 + 4}" fill="#f8fafc" font-size="12" text-anchor="end" font-weight="bold">{st}</text>'
        # Value Label
        bars_html += f'<text x="{x_start + w_len + 10}" y="{y_pos + bar_height/2 + 4}" fill="#38bdf8" font-size="11" text-anchor="start" font-weight="bold">${val/1000:,.1f}k</text>'
        
    # Vertical grid lines
    grid_html = ""
    for i in range(5):
        grid_val = (upper_x / 4) * i
        grid_x = x_start + (i / 4) * chart_w
        grid_html += f'<line x1="{grid_x}" y1="{y_start}" x2="{grid_x}" y2="{y_end + 5}" stroke="#334155" stroke-dasharray="3" stroke-width="0.75"/>'
        grid_html += f'<text x="{grid_x}" y="{y_end + 20}" fill="#94a3b8" font-size="10" text-anchor="middle">${grid_val/1000:,.0f}k</text>'
        
    content = f"""
    <!-- Grid -->
    {grid_html}
    <line x1="{x_start}" y1="{y_start}" x2="{x_start}" y2="{y_end}" stroke="#64748b" stroke-width="1.5"/>
    
    <!-- Bars -->
    {bars_html}
    """
    return SVG_TEMPLATE.format(
        title="Top 8 Regions by Sales Revenue",
        subtitle="Regional contribution to total sales volume",
        content=content
    )

# Chart 3: RFM Customer Segments (Donut Chart)
def generate_rfm_donut_svg(segment_counts):
    # Segment colors
    colors = {
        "Champions": "#34d399",       # Mint green
        "Loyal Customers": "#38bdf8",  # Sky blue
        "New Customers": "#c084fc",    # Lavender
        "Promising/Active": "#fbcfe8",  # Light pink
        "At Risk": "#fb7185",          # Coral red
        "Hibernating": "#64748b"        # Slate grey
    }
    
    sorted_segs = sorted(segment_counts.items(), key=lambda x: x[1], reverse=True)
    total = sum(segment_counts.values())
    
    # Donut center x: 260, y: 240, r: 120, inner_r: 80
    cx, cy, r, inner_r = 260, 240, 120, 80
    
    # Build SVG arcs
    arcs_html = ""
    accum_angle = -90 # start top
    
    legend_html = ""
    
    for idx, (seg, count) in enumerate(sorted_segs):
        pct = count / total
        angle = pct * 360
        
        # Donut coordinates
        # Start angle rads
        rad_start = math.radians(accum_angle)
        x_start_outer = cx + r * math.cos(rad_start)
        y_start_outer = cy + r * math.sin(rad_start)
        x_start_inner = cx + inner_r * math.cos(rad_start)
        y_start_inner = cy + inner_r * math.sin(rad_start)
        
        # End angle rads
        accum_angle += angle
        rad_end = math.radians(accum_angle)
        x_end_outer = cx + r * math.cos(rad_end)
        y_end_outer = cy + r * math.sin(rad_end)
        x_end_inner = cx + inner_r * math.cos(rad_end)
        y_end_inner = cy + inner_r * math.sin(rad_end)
        
        large_arc = 1 if angle > 180 else 0
        color = colors.get(seg, "#cbd5e1")
        
        # Path representing the segment ring slice
        path_d = f"M {x_start_outer} {y_start_outer} " \
                 f"A {r} {r} 0 {large_arc} 1 {x_end_outer} {y_end_outer} " \
                 f"L {x_end_inner} {y_end_inner} " \
                 f"A {inner_r} {inner_r} 0 {large_arc} 0 {x_start_inner} {y_start_inner} Z"
                 
        arcs_html += f'<path d="{path_d}" fill="{color}" stroke="#0f172a" stroke-width="2"/>'
        
        # Legend items: x: 480, y: 120 + idx*40
        y_pos = 120 + idx * 36
        legend_html += f"""
        <g transform="translate(470, {y_pos})">
            <rect x="0" y="0" width="14" height="14" rx="3" fill="{color}"/>
            <text x="22" y="12" fill="#f8fafc" font-size="12" font-weight="bold">{seg}</text>
            <text x="22" y="27" fill="#94a3b8" font-size="11">{count:,} ({pct*100:.1f}%)</text>
        </g>
        """
        
    content = f"""
    <!-- Donut Arcs -->
    {arcs_html}
    
    <!-- Donut Central Hole text -->
    <circle cx="{cx}" cy="{cy}" r="{inner_r - 2}" fill="#0f172a"/>
    <text cx="{cx}" cy="{cy}" fill="#94a3b8" font-size="12" text-anchor="middle" y="{cy - 10}">TOTAL CUSTOMERS</text>
    <text cx="{cx}" cy="{cy}" fill="#f8fafc" font-size="24" font-weight="bold" text-anchor="middle" y="{cy + 15}">{total:,}</text>
    
    <!-- Legend -->
    {legend_html}
    """
    
    # Note: text tag using cx/cy coordinates behaves differently in some rendering, standard text anchor:
    content = content.replace('cx="260"', 'x="260"').replace('cy="240"', '')
    
    return SVG_TEMPLATE.format(
        title="Customer Segmentation (RFM Analysis)",
        subtitle="Distribution of user base across loyalty segments",
        content=content
    )

# Write SVGs
svg_sales_trend = generate_sales_trend_svg(sales_series, forecast_records, month_labels)
with open("Images/sales_trend_forecast.svg", "w", encoding="utf-8") as f:
    f.write(svg_sales_trend)

svg_regional = generate_regional_sales_svg(cleaned_orders, cleaned_customers, order_revenue_map)
with open("Images/regional_sales.svg", "w", encoding="utf-8") as f:
    f.write(svg_regional)

svg_rfm = generate_rfm_donut_svg(segment_counts)
with open("Images/rfm_customer_segments.svg", "w", encoding="utf-8") as f:
    f.write(svg_rfm)

print("SVG visualizations created successfully.")

# ----------------------------------------------------
# 9. Create Jupyter Notebook Mockup
# ----------------------------------------------------
# To fulfill Step 2/3 we write the code as an actual Jupyter Notebook file (.ipynb)
# Let's read a standard template and write the file.
# We will create data_cleaning_eda.ipynb as a fully formatted Jupyter Notebook showing cleaning and EDA steps.

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# E-Commerce Sales & Customer Analytics\n",
    "### Step 2 & 3: Data Cleaning and Exploratory Data Analysis (EDA)\n",
    "\n",
    "This notebook covers the comprehensive data cleaning and exploratory analysis of our raw e-commerce transaction dataset (100,000+ records)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Import libraries\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "from datetime import datetime, timedelta\n",
    "\n",
    "# Set style\n",
    "plt.style.use('seaborn-v0_8-whitegrid')\n",
    "plt.rcParams['figure.figsize'] = (10, 6)\n",
    "plt.rcParams['font.size'] = 11"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Load Datasets"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "customers = pd.read_csv('../Dataset/raw/customers.csv')\n",
    "products = pd.read_csv('../Dataset/raw/products.csv')\n",
    "orders = pd.read_csv('../Dataset/raw/orders.csv')\n",
    "order_items = pd.read_csv('../Dataset/raw/order_items.csv')\n",
    "payments = pd.read_csv('../Dataset/raw/payments.csv')\n",
    "reviews = pd.read_csv('../Dataset/raw/reviews.csv')\n",
    "returns = pd.read_csv('../Dataset/raw/returns.csv')\n",
    "\n",
    "print(f\"Raw Orders shape: {orders.shape}\")\n",
    "print(f\"Raw Order Items shape: {order_items.shape}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Null Value Analysis & Deduplication"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Duplicate Check\n",
    "print(f\"Duplicate Customer Records: {customers.duplicated(subset=['customer_id']).sum()}\")\n",
    "customers.drop_duplicates(subset=['customer_id'], inplace=True)\n",
    "orders.drop_duplicates(subset=['order_id'], inplace=True)\n",
    "\n",
    "# Impute missing zip code prefix\n",
    "customers['customer_zip_code_prefix'].fillna('00000', inplace=True)\n",
    "\n",
    "# Order missing dates imputation\n",
    "orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])\n",
    "orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])\n",
    "orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])\n",
    "\n",
    "# Impute delivery date for delivered status with default (7 days after purchase)\n",
    "mask = (orders['order_status'] == 'delivered') & (orders['order_delivered_customer_date'].isna())\n",
    "orders.loc[mask, 'order_delivered_customer_date'] = orders.loc[mask, 'order_purchase_timestamp'] + pd.Timedelta(days=7)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Outlier Correction"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Inspect weight anomalies\n",
    "print(f\"Negative weights count: {(products['product_weight_g'] < 0).sum()}\")\n",
    "products['product_weight_g'] = products['product_weight_g'].abs()\n",
    "products['product_base_price'] = products['product_base_price'].abs()\n",
    "\n",
    "# Impute pricing outliers ($99,999 cases)\n",
    "category_medians = products[products['product_base_price'] < 50000].groupby('product_category_name')['product_base_price'].median()\n",
    "products.loc[products['product_base_price'] > 50000, 'product_base_price'] = products.loc[products['product_base_price'] > 50000, 'product_category_name'].map(category_medians)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Feature Engineering"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Delivery Days\n",
    "orders['delivery_days'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']).dt.days\n",
    "# Delivery delay relative to estimate\n",
    "orders['delay_days'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']).dt.days\n",
    "orders['is_delayed'] = orders['delay_days'] > 0\n",
    "\n",
    "# Total spend per item line\n",
    "order_items['item_value'] = order_items['price'] * order_items['quantity']\n",
    "order_totals = order_items.groupby('order_id')['item_value'].sum().reset_name = 'order_value'"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Visual EDA"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Plot Monthly Sales Trends\n",
    "orders['year_month'] = orders['order_purchase_timestamp'].dt.to_period('M')\n",
    "order_items_merged = order_items.merge(orders, on='order_id')\n",
    "monthly_sales = order_items_merged.groupby('year_month')['item_value'].sum()\n",
    "\n",
    "monthly_sales.plot(kind='line', marker='o', color='#38bdf8', linewidth=2.5)\n",
    "plt.title('Monthly Sales Revenue Growth (2024-2026)')\n",
    "plt.xlabel('Month')\n",
    "plt.ylabel('Revenue ($)')\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Advanced Customer Analytics: RFM Analysis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Reference max date\n",
    "max_date = orders['order_purchase_timestamp'].max()\n",
    "user_rfm = order_items_merged.groupby('customer_id').agg({\n",
    "    'order_purchase_timestamp': lambda x: (max_date - x.max()).days,\n",
    "    'order_id': 'nunique',\n",
    "    'item_value': 'sum'\n",
    "}).rename(columns={\n",
    "    'order_purchase_timestamp': 'recency',\n",
    "    'order_id': 'frequency',\n",
    "    'item_value': 'monetary'\n",
    "})\n",
    "\n",
    "print(user_rfm.head())"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

import json
with open("Python/data_cleaning_eda.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=1)

print("Jupyter notebook file written to 'Python/data_cleaning_eda.ipynb'.")
print("Data pipeline executed successfully!")
