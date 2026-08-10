"""
Power BI Star-Schema Exporter Script
Project: E-Commerce Sales & Supply Chain Analytics

This script extracts data from the local SQLite database (`SQL/ecommerce_analytics.db`)
and exports clean, normalized Star-Schema tables for seamless 1-click import into Power BI Desktop.
"""

import os
import sqlite3
import pandas as pd

def export_powerbi_data_model():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'SQL', 'ecommerce_analytics.db')
    output_dir = os.path.join(base_dir, 'PowerBI', 'Data_Model')
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)

    # 1. Fact_OrderItems (Fact Table: Sales & Revenues)
    print("Exporting Fact_OrderItems...")
    query_fact_order_items = """
    SELECT 
        oi.order_item_id,
        oi.order_id,
        oi.product_id,
        oi.seller_id,
        o.customer_id,
        DATE(o.order_purchase_timestamp) AS order_date,
        oi.price AS unit_price,
        oi.freight_value,
        oi.quantity,
        (oi.price * oi.quantity) AS item_revenue,
        (oi.price * oi.quantity * 0.35) AS estimated_gross_profit
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    """
    df_fact_order_items = pd.read_sql_query(query_fact_order_items, conn)
    df_fact_order_items.to_csv(os.path.join(output_dir, 'Fact_OrderItems.csv'), index=False)

    # 2. Fact_Shipping (Fact Table: Logistics & SLA Telemetry)
    print("Exporting Fact_Shipping...")
    query_fact_shipping = """
    SELECT 
        s.shipping_id,
        s.order_id,
        o.customer_id,
        s.shipping_carrier,
        s.shipping_tracking_number,
        s.shipping_status,
        DATE(o.order_purchase_timestamp) AS purchase_date,
        s.shipping_estimated_delivery_date,
        s.shipping_actual_delivery_date,
        CAST((JULIANDAY(s.shipping_actual_delivery_date) - JULIANDAY(o.order_purchase_timestamp)) AS REAL) AS delivery_lead_days,
        CAST((JULIANDAY(s.shipping_actual_delivery_date) - JULIANDAY(s.shipping_estimated_delivery_date)) AS REAL) AS delivery_delay_days,
        CASE WHEN JULIANDAY(s.shipping_actual_delivery_date) <= JULIANDAY(s.shipping_estimated_delivery_date) THEN 1 ELSE 0 END AS is_on_time
    FROM shipping s
    JOIN orders o ON s.order_id = o.order_id
    """
    df_fact_shipping = pd.read_sql_query(query_fact_shipping, conn)
    df_fact_shipping.to_csv(os.path.join(output_dir, 'Fact_Shipping.csv'), index=False)

    # 3. Dim_Customer
    print("Exporting Dim_Customer...")
    df_dim_customer = pd.read_sql_query("SELECT customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state FROM customers", conn)
    df_dim_customer.to_csv(os.path.join(output_dir, 'Dim_Customer.csv'), index=False)

    # 4. Dim_Product
    print("Exporting Dim_Product...")
    query_dim_product = """
    SELECT 
        p.product_id,
        p.product_category_name,
        COALESCE(c.product_category_name_english, p.product_category_name) AS category_name_english,
        p.product_base_price,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm
    FROM products p
    LEFT JOIN categories c ON p.product_category_name = c.product_category_name
    """
    df_dim_product = pd.read_sql_query(query_dim_product, conn)
    df_dim_product.to_csv(os.path.join(output_dir, 'Dim_Product.csv'), index=False)

    # 5. Dim_Seller
    print("Exporting Dim_Seller...")
    df_dim_seller = pd.read_sql_query("SELECT seller_id, seller_zip_code_prefix, seller_city, seller_state FROM sellers", conn)
    df_dim_seller.to_csv(os.path.join(output_dir, 'Dim_Seller.csv'), index=False)

    # 6. Dim_Date
    print("Exporting Dim_Date...")
    dates = pd.date_range(start='2024-01-01', end='2026-12-31', freq='D')
    df_dim_date = pd.DataFrame({'Date': dates})
    df_dim_date['DateKey'] = df_dim_date['Date'].dt.strftime('%Y%m%d').astype(int)
    df_dim_date['Year'] = df_dim_date['Date'].dt.year
    df_dim_date['Quarter'] = 'Q' + df_dim_date['Date'].dt.quarter.astype(str)
    df_dim_date['MonthNo'] = df_dim_date['Date'].dt.month
    df_dim_date['MonthName'] = df_dim_date['Date'].dt.strftime('%B')
    df_dim_date['DayOfWeek'] = df_dim_date['Date'].dt.strftime('%A')
    df_dim_date['IsWeekend'] = df_dim_date['Date'].dt.dayofweek.isin([5, 6]).astype(int)
    df_dim_date.to_csv(os.path.join(output_dir, 'Dim_Date.csv'), index=False)

    conn.close()
    print(f"Successfully exported all Star-Schema Power BI tables to: {output_dir}")

if __name__ == '__main__':
    export_powerbi_data_model()
