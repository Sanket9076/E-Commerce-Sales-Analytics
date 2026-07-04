"""
E-Commerce Sales & Customer Analytics
Interactive HTML Dashboard Builder
Generates a single self-contained dashboard.html file
"""

import sqlite3
import json
import os
from datetime import datetime

# ── Path Setup ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "SQL", "ecommerce_analytics.db")
OUT_PATH = os.path.join(BASE_DIR, "dashboard.html")

print("=" * 60)
print("  E-Commerce Dashboard Builder")
print("=" * 60)
print(f"  Database : {DB_PATH}")
print(f"  Output   : {OUT_PATH}")
print()

# ── Load Data from SQLite ──────────────────────────────────────────────────────
con = sqlite3.connect(DB_PATH)
cur = con.cursor()

# KPIs
cur.execute("SELECT ROUND(SUM(payment_value),2) FROM payments")
total_revenue = cur.fetchone()[0] or 0

cur.execute("SELECT COUNT(DISTINCT order_id) FROM orders")
total_orders = cur.fetchone()[0] or 0

cur.execute("SELECT COUNT(DISTINCT customer_id) FROM customers")
total_customers = cur.fetchone()[0] or 0

cur.execute("SELECT ROUND(AVG(payment_value),2) FROM payments")
avg_order_value = cur.fetchone()[0] or 0

cur.execute("SELECT ROUND(AVG(review_score),2) FROM reviews")
avg_review = cur.fetchone()[0] or 0

# Monthly Revenue
cur.execute("""
    SELECT SUBSTR(o.order_purchase_timestamp,1,7) AS month,
           ROUND(SUM(p.payment_value),2) AS revenue
    FROM orders o
    JOIN payments p ON o.order_id = p.order_id
    GROUP BY month
    ORDER BY month
""")
monthly = cur.fetchall()
months_x  = [r[0] for r in monthly]
revenue_y = [r[1] for r in monthly]

# Monthly Orders
cur.execute("""
    SELECT SUBSTR(order_purchase_timestamp,1,7) AS month,
           COUNT(DISTINCT order_id) AS cnt
    FROM orders
    GROUP BY month ORDER BY month
""")
mo = cur.fetchall()
months_ord  = [r[0] for r in mo]
orders_cnt  = [r[1] for r in mo]

# Top 10 Categories
cur.execute("""
    SELECT c.product_category_name_english,
           ROUND(SUM(p.payment_value),2) AS rev
    FROM categories c
    JOIN products pr ON c.product_category_name = pr.product_category_name
    JOIN order_items oi ON pr.product_id = oi.product_id
    JOIN payments p  ON oi.order_id = p.order_id
    GROUP BY c.product_category_name_english
    ORDER BY rev DESC LIMIT 10
""")
cats = cur.fetchall()
cat_names = [r[0] for r in cats]
cat_rev   = [r[1] for r in cats]

# Payment Types
cur.execute("""
    SELECT payment_type, ROUND(SUM(payment_value),2)
    FROM payments GROUP BY payment_type ORDER BY 2 DESC
""")
pay = cur.fetchall()
pay_types = [r[0] for r in pay]
pay_vals  = [r[1] for r in pay]

# Order Status
cur.execute("""
    SELECT order_status, COUNT(*) FROM orders
    GROUP BY order_status ORDER BY 2 DESC
""")
status = cur.fetchall()
status_labels = [r[0] for r in status]
status_counts = [r[1] for r in status]

# Review Scores
cur.execute("""
    SELECT review_score, COUNT(*) FROM reviews
    GROUP BY review_score ORDER BY review_score
""")
revs = cur.fetchall()
rev_scores = [str(r[0]) for r in revs]
rev_counts = [r[1] for r in revs]

# Top 10 States by Revenue
cur.execute("""
    SELECT cu.customer_state,
           ROUND(SUM(p.payment_value),2) AS rev
    FROM customers cu
    JOIN orders o ON cu.customer_id = o.customer_id
    JOIN payments p ON o.order_id = p.order_id
    GROUP BY cu.customer_state
    ORDER BY rev DESC LIMIT 10
""")
states = cur.fetchall()
state_names = [r[0] for r in states]
state_rev   = [r[1] for r in states]

# Top 10 Products
cur.execute("""
    SELECT pr.product_id,
           ROUND(SUM(oi.price * oi.quantity),2) AS rev
    FROM products pr
    JOIN order_items oi ON pr.product_id = oi.product_id
    GROUP BY pr.product_id
    ORDER BY rev DESC LIMIT 10
""")
prods = cur.fetchall()
prod_ids  = [r[0][:12] for r in prods]
prod_revs = [r[1] for r in prods]

# Shipping Status counts
cur.execute("""
    SELECT shipping_status, COUNT(*) FROM shipping
    GROUP BY shipping_status ORDER BY 2 DESC
""")
ship_status = cur.fetchall()
ship_labels = [r[0] for r in ship_status]
ship_counts = [r[1] for r in ship_status]

# Sellers Revenue
cur.execute("""
    SELECT s.seller_state,
           ROUND(SUM(oi.price),2) AS rev
    FROM sellers s
    JOIN order_items oi ON s.seller_id = oi.seller_id
    GROUP BY s.seller_state
    ORDER BY rev DESC LIMIT 10
""")
sellers = cur.fetchall()
seller_states = [r[0] for r in sellers]
seller_rev    = [r[1] for r in sellers]

con.close()
print("  [OK] Data loaded from database")

# ── Plotly JSON helpers ────────────────────────────────────────────────────────
def line_chart(x, y, title, color="#00d4ff", fill=True):
    return {
        "data": [{
            "x": x, "y": y, "type": "scatter", "mode": "lines+markers",
            "line": {"color": color, "width": 3},
            "marker": {"size": 6, "color": color},
            "fill": "tozeroy" if fill else "none",
            "fillcolor": color.replace(")", ",0.15)").replace("rgb", "rgba") if color.startswith("rgb") else color + "26",
            "name": title
        }],
        "layout": base_layout(title)
    }

def bar_chart(x, y, title, color="#7c3aed", horizontal=False):
    trace = {"type": "bar", "marker": {"color": color, "opacity": 0.85}, "name": title}
    if horizontal:
        trace["x"] = y; trace["y"] = x; trace["orientation"] = "h"
    else:
        trace["x"] = x; trace["y"] = y
    layout = base_layout(title)
    return {"data": [trace], "layout": layout}

def pie_chart(labels, values, title, colors=None):
    c = colors or ["#00d4ff","#7c3aed","#10b981","#f59e0b","#ef4444","#8b5cf6"]
    return {
        "data": [{"type": "pie", "labels": labels, "values": values,
                  "hole": 0.4, "marker": {"colors": c},
                  "textinfo": "label+percent", "textfont": {"color": "#fff"}}],
        "layout": base_layout(title)
    }

def base_layout(title):
    return {
        "title": {"text": title, "font": {"color": "#e2e8f0", "size": 16, "family": "Inter, sans-serif"}, "x": 0.02},
        "paper_bgcolor": "#1e293b",
        "plot_bgcolor":  "#0f172a",
        "font":  {"color": "#94a3b8", "family": "Inter, sans-serif"},
        "xaxis": {"gridcolor": "#334155", "linecolor": "#334155", "tickfont": {"color": "#94a3b8"}},
        "yaxis": {"gridcolor": "#334155", "linecolor": "#334155", "tickfont": {"color": "#94a3b8"}},
        "margin": {"l": 50, "r": 20, "t": 50, "b": 50},
        "legend": {"bgcolor": "#1e293b", "font": {"color": "#94a3b8"}},
        "showlegend": False
    }

# Build chart JSONs
charts = {
    "monthly_revenue": line_chart(months_x, revenue_y, "Monthly Revenue Trend ($)", "#00d4ff"),
    "monthly_orders":  line_chart(months_ord, orders_cnt, "Monthly Order Volume", "#10b981"),
    "top_categories":  bar_chart(cat_names, cat_rev, "Top 10 Categories by Revenue ($)", "#7c3aed", horizontal=True),
    "payment_types":   pie_chart(pay_types, pay_vals, "Revenue by Payment Method"),
    "order_status":    pie_chart(status_labels, status_counts, "Order Status Distribution",
                                  ["#10b981","#f59e0b","#ef4444","#6366f1","#8b5cf6"]),
    "review_scores":   bar_chart(rev_scores, rev_counts, "Review Score Distribution", "#f59e0b"),
    "top_states":      bar_chart(state_names, state_rev, "Top 10 States by Revenue ($)", "#00d4ff", horizontal=True),
    "top_products":    bar_chart(prod_ids, prod_revs, "Top 10 Products by Revenue ($)", "#10b981", horizontal=True),
    "seller_states":   bar_chart(seller_states, seller_rev, "Top Seller States by Revenue ($)", "#f59e0b"),
}

charts_json = json.dumps(charts)
print("  [OK] Charts prepared")

# ── HTML Template ──────────────────────────────────────────────────────────────
kpi_fmt = lambda v: f"${v:,.0f}" if v > 1000 else f"${v:,.2f}"

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>E-Commerce Sales & Customer Analytics Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg-primary:   #0f172a;
    --bg-card:      #1e293b;
    --bg-hover:     #273549;
    --accent-blue:  #00d4ff;
    --accent-purple:#7c3aed;
    --accent-green: #10b981;
    --accent-amber: #f59e0b;
    --accent-red:   #ef4444;
    --text-primary: #e2e8f0;
    --text-muted:   #94a3b8;
    --border:       #334155;
    --radius:       12px;
  }}
  body {{
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
  }}

  /* ── Header ── */
  .header {{
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border-bottom: 1px solid var(--border);
    padding: 24px 32px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .header-left h1 {{
    font-size: 1.75rem; font-weight: 700;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }}
  .header-left p {{ color: var(--text-muted); font-size: 0.875rem; margin-top: 4px; }}
  .header-right {{ text-align: right; }}
  .header-right span {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 20px; padding: 6px 16px;
    font-size: 0.8rem; color: var(--text-muted);
  }}

  /* ── Nav Tabs ── */
  .nav {{
    display: flex; gap: 4px;
    background: var(--bg-card);
    border-bottom: 1px solid var(--border);
    padding: 0 24px; overflow-x: auto;
  }}
  .nav-tab {{
    padding: 16px 20px; cursor: pointer;
    font-size: 0.875rem; font-weight: 500;
    color: var(--text-muted);
    border-bottom: 3px solid transparent;
    white-space: nowrap; transition: all 0.2s;
  }}
  .nav-tab:hover {{ color: var(--text-primary); background: var(--bg-hover); }}
  .nav-tab.active {{ color: var(--accent-blue); border-bottom-color: var(--accent-blue); }}

  /* ── Main Content ── */
  .main {{ padding: 24px 32px; }}
  .page {{ display: none; }}
  .page.active {{ display: block; }}

  /* ── KPI Cards ── */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px; margin-bottom: 24px;
  }}
  .kpi-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 24px;
    position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
  }}
  .kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
  }}
  .kpi-card::before {{
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
  }}
  .kpi-card.blue::before   {{ background: var(--accent-blue); }}
  .kpi-card.purple::before {{ background: var(--accent-purple); }}
  .kpi-card.green::before  {{ background: var(--accent-green); }}
  .kpi-card.amber::before  {{ background: var(--accent-amber); }}
  .kpi-card.red::before    {{ background: var(--accent-red); }}
  .kpi-label {{ font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }}
  .kpi-value {{ font-size: 1.75rem; font-weight: 700; color: var(--text-primary); line-height: 1; }}
  .kpi-icon  {{ position: absolute; right: 20px; top: 50%; transform: translateY(-50%); font-size: 2rem; opacity: 0.15; }}

  /* ── Chart Grid ── */
  .chart-grid {{ display: grid; gap: 20px; margin-bottom: 20px; }}
  .chart-grid.cols-2 {{ grid-template-columns: 1fr 1fr; }}
  .chart-grid.cols-3 {{ grid-template-columns: 1fr 1fr 1fr; }}
  .chart-grid.cols-1 {{ grid-template-columns: 1fr; }}
  .chart-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 8px; overflow: hidden;
    transition: box-shadow 0.2s;
  }}
  .chart-card:hover {{ box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
  .chart-card.wide {{ grid-column: 1 / -1; }}

  /* ── Section Title ── */
  .section-title {{
    font-size: 0.7rem; font-weight: 600;
    color: var(--text-muted); text-transform: uppercase;
    letter-spacing: 0.08em; margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
  }}
  .section-title::after {{
    content: ''; flex: 1; height: 1px; background: var(--border);
  }}

  /* ── Footer ── */
  .footer {{
    text-align: center; padding: 24px;
    color: var(--text-muted); font-size: 0.8rem;
    border-top: 1px solid var(--border);
    margin-top: 32px;
  }}

  @media (max-width: 768px) {{
    .header {{ flex-direction: column; gap: 12px; padding: 16px; }}
    .main {{ padding: 16px; }}
    .chart-grid.cols-2, .chart-grid.cols-3 {{ grid-template-columns: 1fr; }}
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
  }}
</style>
</head>
<body>

<!-- Header -->
<header class="header">
  <div class="header-left">
    <h1>🛒 E-Commerce Sales Analytics</h1>
    <p>Interactive Business Intelligence Dashboard &nbsp;|&nbsp; 100,000+ Transactions Analyzed</p>
  </div>
  <div class="header-right">
    <span>📅 Last Updated: {datetime.now().strftime('%d %b %Y')}</span>
  </div>
</header>

<!-- Navigation -->
<nav class="nav">
  <div class="nav-tab active" onclick="showPage('executive')">📊 Executive Summary</div>
  <div class="nav-tab" onclick="showPage('sales')">📈 Sales Trends</div>
  <div class="nav-tab" onclick="showPage('customers')">👥 Customer Analytics</div>
  <div class="nav-tab" onclick="showPage('products')">📦 Product Analytics</div>
  <div class="nav-tab" onclick="showPage('regional')">🗺️ Regional Analytics</div>
</nav>

<!-- Main Content -->
<main class="main">

  <!-- PAGE 1: Executive Summary -->
  <div class="page active" id="page-executive">

    <div class="section-title">Key Performance Indicators</div>
    <div class="kpi-grid">
      <div class="kpi-card blue">
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">${total_revenue:,.0f}</div>
        <div class="kpi-icon">💰</div>
      </div>
      <div class="kpi-card purple">
        <div class="kpi-label">Total Orders</div>
        <div class="kpi-value">{total_orders:,}</div>
        <div class="kpi-icon">📦</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-label">Total Customers</div>
        <div class="kpi-value">{total_customers:,}</div>
        <div class="kpi-icon">👥</div>
      </div>
      <div class="kpi-card amber">
        <div class="kpi-label">Avg Order Value</div>
        <div class="kpi-value">${avg_order_value:,.2f}</div>
        <div class="kpi-icon">💳</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-label">Avg Review Score</div>
        <div class="kpi-value">{avg_review} / 5</div>
        <div class="kpi-icon">⭐</div>
      </div>
    </div>

    <div class="section-title">Revenue & Orders Trend</div>
    <div class="chart-grid cols-1">
      <div class="chart-card"><div id="ch-monthly-revenue" style="height:320px"></div></div>
    </div>

    <div class="chart-grid cols-2">
      <div class="chart-card"><div id="ch-order-status" style="height:300px"></div></div>
      <div class="chart-card"><div id="ch-payment-types" style="height:300px"></div></div>
    </div>
  </div>

  <!-- PAGE 2: Sales Trends -->
  <div class="page" id="page-sales">
    <div class="section-title">Sales Performance Over Time</div>
    <div class="chart-grid cols-1">
      <div class="chart-card"><div id="ch-monthly-orders" style="height:300px"></div></div>
    </div>
    <div class="section-title">Revenue by Category</div>
    <div class="chart-grid cols-1">
      <div class="chart-card"><div id="ch-top-categories" style="height:420px"></div></div>
    </div>
  </div>

  <!-- PAGE 3: Customer Analytics -->
  <div class="page" id="page-customers">
    <div class="section-title">Customer Satisfaction & Feedback</div>
    <div class="chart-grid cols-2">
      <div class="chart-card"><div id="ch-review-scores" style="height:300px"></div></div>
      <div class="chart-card"><div id="ch-payment-types-2" style="height:300px"></div></div>
    </div>
    <div class="section-title">Geographic Distribution</div>
    <div class="chart-grid cols-1">
      <div class="chart-card"><div id="ch-top-states-cust" style="height:380px"></div></div>
    </div>
  </div>

  <!-- PAGE 4: Product Analytics -->
  <div class="page" id="page-products">
    <div class="section-title">Top Performing Products</div>
    <div class="chart-grid cols-1">
      <div class="chart-card"><div id="ch-top-products" style="height:380px"></div></div>
    </div>
    <div class="section-title">Category Performance</div>
    <div class="chart-grid cols-1">
      <div class="chart-card"><div id="ch-top-categories-2" style="height:400px"></div></div>
    </div>
  </div>

  <!-- PAGE 5: Regional Analytics -->
  <div class="page" id="page-regional">
    <div class="section-title">Revenue by Region</div>
    <div class="chart-grid cols-1">
      <div class="chart-card"><div id="ch-top-states" style="height:380px"></div></div>
    </div>
    <div class="section-title">Seller Distribution</div>
    <div class="chart-grid cols-1">
      <div class="chart-card"><div id="ch-seller-states" style="height:320px"></div></div>
    </div>
  </div>

</main>

<footer class="footer">
  Built with Python &amp; Plotly &nbsp;|&nbsp; E-Commerce Sales &amp; Customer Analytics Portfolio Project &nbsp;|&nbsp; Data Analyst Fresher Portfolio
</footer>

<script>
// ── Chart Data ──────────────────────────────────────────────────────────────
const CHARTS = {charts_json};

function cfg(data, layout) {{
  return {{ data: data, layout: layout, config: {{ responsive: true, displayModeBar: false }} }};
}}

function renderChart(divId, chartKey) {{
  const c = CHARTS[chartKey];
  Plotly.newPlot(divId, c.data, c.layout, {{ responsive: true, displayModeBar: false }});
}}

// ── Page Navigation ─────────────────────────────────────────────────────────
function showPage(name) {{
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  event.target.classList.add('active');
  renderAllCharts(name);
}}

function renderAllCharts(page) {{
  if (page === 'executive') {{
    renderChart('ch-monthly-revenue', 'monthly_revenue');
    renderChart('ch-order-status',    'order_status');
    renderChart('ch-payment-types',   'payment_types');
  }} else if (page === 'sales') {{
    renderChart('ch-monthly-orders',    'monthly_orders');
    renderChart('ch-top-categories',    'top_categories');
  }} else if (page === 'customers') {{
    renderChart('ch-review-scores',     'review_scores');
    renderChart('ch-payment-types-2',   'payment_types');
    renderChart('ch-top-states-cust',   'top_states');
  }} else if (page === 'products') {{
    renderChart('ch-top-products',      'top_products');
    renderChart('ch-top-categories-2',  'top_categories');
  }} else if (page === 'regional') {{
    renderChart('ch-top-states',        'top_states');
    renderChart('ch-seller-states',     'seller_states');
  }}
}}

// ── Initial Render ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {{
  renderAllCharts('executive');
}});
</script>
</body>
</html>
"""

# Write file
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"  [OK] Dashboard saved to:")
print(f"       {OUT_PATH}")
print()
print("  Open this file in Chrome/Edge to view your dashboard!")
print("=" * 60)
