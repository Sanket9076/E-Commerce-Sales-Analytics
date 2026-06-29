import os
import sqlite3

DB_PATH = "SQL/ecommerce_analytics.db"

# Sample list of 10 key business queries adapted for SQLite to show off the project
QUERIES = {
    1: (
        "Business KPIs Summary (Revenue, Profit, AOV, Returns)",
        """
        SELECT 
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(SUM(oi.price * oi.quantity), 2) AS product_revenue,
            ROUND(SUM(oi.freight_value), 2) AS total_freight,
            ROUND(SUM(oi.price * oi.quantity) * 0.35, 2) AS gross_profit,
            ROUND(SUM(oi.price * oi.quantity) / COUNT(DISTINCT o.order_id), 2) AS average_order_value,
            (SELECT COUNT(*) FROM returns) AS total_returns
        FROM orders o
        INNER JOIN order_items oi ON o.order_id = oi.order_id;
        """
    ),
    2: (
        "Top 10 Selling Products by Revenue",
        """
        SELECT 
            oi.product_id,
            p.product_category_name AS category,
            SUM(oi.quantity) AS qty_sold,
            ROUND(SUM(oi.price * oi.quantity), 2) AS revenue
        FROM order_items oi
        INNER JOIN products p ON oi.product_id = p.product_id
        GROUP BY oi.product_id, p.product_category_name
        ORDER BY revenue DESC
        LIMIT 10;
        """
    ),
    3: (
        "Customer Lifetime Value (CLV) & Spend Statistics",
        """
        WITH CustomerStats AS (
            SELECT 
                c.customer_unique_id,
                COUNT(o.order_id) AS total_orders,
                SUM(oi.price * oi.quantity) AS total_spend
            FROM orders o
            INNER JOIN customers c ON o.customer_id = c.customer_id
            INNER JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_unique_id
        )
        SELECT 
            ROUND(AVG(total_orders), 2) AS avg_orders_per_customer,
            ROUND(AVG(total_spend), 2) AS avg_spend_per_customer,
            ROUND(MAX(total_spend), 2) AS max_single_customer_spend
        FROM CustomerStats;
        """
    ),
    4: (
        "Repeat Purchase Rate (Loyalty Metric)",
        """
        WITH UserOrderCounts AS (
            SELECT c.customer_unique_id, COUNT(o.order_id) AS order_count
            FROM orders o
            INNER JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY c.customer_unique_id
        )
        SELECT 
            COUNT(CASE WHEN order_count > 1 THEN 1 END) AS repeat_customers_count,
            COUNT(*) AS total_customers,
            ROUND((COUNT(CASE WHEN order_count > 1 THEN 1 END) * 100.0 / COUNT(*)), 2) AS repeat_customer_rate_pct
        FROM UserOrderCounts;
        """
    ),
    5: (
        "Pareto 80/20 Spend Distribution Validation",
        """
        WITH CustomerSales AS (
            SELECT c.customer_unique_id, SUM(oi.price * oi.quantity) AS spend
            FROM orders o
            INNER JOIN customers c ON o.customer_id = c.customer_id
            INNER JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_unique_id
        ),
        RunningSales AS (
            SELECT 
                customer_unique_id,
                spend,
                SUM(spend) OVER (ORDER BY spend DESC) AS cumulative_spend,
                (SELECT SUM(price * quantity) FROM order_items) AS total_revenue,
                ROW_NUMBER() OVER (ORDER BY spend DESC) AS row_num,
                (SELECT COUNT(DISTINCT customer_unique_id) FROM customers) AS total_customers
            FROM CustomerSales
        )
        SELECT 
            row_num AS customer_rank,
            ROUND(row_num * 100.0 / total_customers, 2) AS customer_pct,
            ROUND(spend, 2) AS individual_spend,
            ROUND(cumulative_spend * 100.0 / total_revenue, 2) AS cumulative_revenue_pct
        FROM RunningSales
        WHERE cumulative_revenue_pct <= 80.05
        ORDER BY row_num DESC
        LIMIT 1;
        """
    ),
    6: (
        "ABC Inventory Classification",
        """
        WITH ProductRevenue AS (
            SELECT product_id, SUM(price * quantity) AS revenue
            FROM order_items
            GROUP BY product_id
        ),
        ProductCumulative AS (
            SELECT 
                product_id, revenue,
                SUM(revenue) OVER (ORDER BY revenue DESC) AS cum_revenue,
                (SELECT SUM(price * quantity) FROM order_items) AS total_revenue
            FROM ProductRevenue
        ),
        ABCClassification AS (
            SELECT 
                product_id, revenue,
                CASE 
                    WHEN (cum_revenue / total_revenue) <= 0.70 THEN 'A (Top 70% Revenue)'
                    WHEN (cum_revenue / total_revenue) <= 0.90 THEN 'B (Next 20% Revenue)'
                    ELSE 'C (Bottom 10% Revenue)'
                END AS abc_class
            FROM ProductCumulative
        )
        SELECT 
            abc_class,
            COUNT(product_id) AS product_count,
            ROUND(COUNT(product_id) * 100.0 / (SELECT COUNT(*) FROM products), 2) AS product_pct,
            ROUND(SUM(revenue), 2) AS class_revenue,
            ROUND(SUM(revenue) * 100.0 / (SELECT SUM(price * quantity) FROM order_items), 2) AS revenue_pct
        FROM ABCClassification
        GROUP BY abc_class
        ORDER BY abc_class;
        """
    ),
    7: (
        "Top 10 Regions (States) by Revenue",
        """
        SELECT 
            c.customer_state AS state,
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(SUM(oi.price * oi.quantity), 2) AS revenue,
            ROUND(AVG(oi.price * oi.quantity), 2) AS avg_order_value
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.order_id
        INNER JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_state
        ORDER BY revenue DESC
        LIMIT 10;
        """
    ),
    8: (
        "Month-over-Month Revenue Growth",
        """
        WITH MonthlySales AS (
            SELECT 
                STRFTIME('%Y-%m', order_purchase_timestamp) AS sale_month,
                SUM(price * quantity) AS revenue
            FROM orders o
            INNER JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY STRFTIME('%Y-%m', order_purchase_timestamp)
        ),
        MonthlyComparisons AS (
            SELECT 
                sale_month,
                revenue,
                LAG(revenue) OVER (ORDER BY sale_month) AS prev_month_revenue
            FROM MonthlySales
        )
        SELECT 
            sale_month,
            ROUND(revenue, 2) AS current_month_revenue,
            ROUND(prev_month_revenue, 2) AS previous_month_revenue,
            ROUND(((revenue - prev_month_revenue) * 100.0 / prev_month_revenue), 2) AS mom_growth_rate_pct
        FROM MonthlyComparisons
        WHERE prev_month_revenue IS NOT NULL
        ORDER BY sale_month
        LIMIT 10;
        """
    ),
    9: (
        "Average Delivery Time and Logistics Status by Shipping Carrier",
        """
        SELECT 
            sh.shipping_carrier,
            COUNT(o.order_id) AS total_shipments,
            ROUND(AVG(JULIANDAY(sh.shipping_actual_delivery_date) - JULIANDAY(o.order_purchase_timestamp)), 2) AS avg_delivery_days,
            COUNT(CASE WHEN sh.shipping_actual_delivery_date > sh.shipping_estimated_delivery_date THEN 1 END) AS late_deliveries_count,
            ROUND((COUNT(CASE WHEN sh.shipping_actual_delivery_date > sh.shipping_estimated_delivery_date THEN 1 END) * 100.0 / COUNT(o.order_id)), 2) AS delay_rate_pct
        FROM shipping sh
        INNER JOIN orders o ON sh.order_id = o.order_id
        WHERE sh.shipping_status = 'delivered'
        GROUP BY sh.shipping_carrier
        ORDER BY avg_delivery_days ASC;
        """
    ),
    10: (
        "Customer Reviews Sentiment & CSAT Analysis",
        """
        SELECT 
            review_score AS rating,
            COUNT(*) AS review_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews), 2) AS review_pct
        FROM reviews
        GROUP BY review_score
        ORDER BY review_score DESC;
        """
    )
}

def print_table(headers, rows):
    # Determine column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val if val is not None else "")))
            
    # Print header separator
    sep = "+" + "+".join(["-" * (w + 2) for w in widths]) + "+"
    print(sep)
    
    # Print headers
    header_str = "|" + "|".join([f" {headers[i]:<{widths[i]}} " for i in range(len(headers))]) + "|"
    print(header_str)
    print(sep)
    
    # Print rows
    for row in rows:
        row_str = "|" + "|".join([f" {str(val if val is not None else ''):<{widths[idx]}} " for idx, val in enumerate(row)]) + "|"
        print(row_str)
        
    print(sep)

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}. Please run load_to_sqlite.py first.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n=======================================================")
    print("  E-Commerce Sales & Customer Analytics Query Runner")
    print("=======================================================")
    
    while True:
        print("\nSelect a business query to execute against the SQLite database:")
        for k, v in QUERIES.items():
            print(f" [{k}] {v[0]}")
        print(" [0] Exit Query Runner")
        
        choice = input("\nEnter query number (0-10): ").strip()
        
        if choice == "0":
            break
            
        try:
            num = int(choice)
            if num not in QUERIES:
                print("Invalid selection. Please choose a number between 0 and 10.")
                continue
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
            
        title, query = QUERIES[num]
        print(f"\nExecuting Query: {title}")
        print("-" * 50)
        
        try:
            cursor.execute(query)
            headers = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            # Format float columns for nicer display
            formatted_rows = []
            for row in rows:
                formatted_row = []
                for val in row:
                    if isinstance(val, float):
                        formatted_row.append(f"{val:,.2f}")
                    elif isinstance(val, int) and "revenue" in title.lower() and val > 1000:
                        formatted_row.append(f"{val:,}")
                    else:
                        formatted_row.append(val)
                formatted_rows.append(formatted_row)
                
            print_table(headers, formatted_rows)
            print(f"Returned {len(rows)} row(s).")
            
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            
    conn.close()
    print("\nExited query runner. Thank you!")

if __name__ == "__main__":
    main()
