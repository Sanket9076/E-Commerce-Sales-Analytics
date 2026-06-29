# Power BI Dashboard Visual Design Specification

This document details the visual layouts, design system, theme tokens, and interactive setups for the 5 pages of the **E-Commerce Sales & Customer Analytics** interactive dashboard.

---

## 1. Visual Theme & Styling Guidelines

* **Theme**: Deep Premium Dark Mode (Glassmorphism & Neon Accents)
* **Color Palette**:
  - **Background**: `#0f172a` (Slate 900)
  - **Cards / Containers**: `#1e293b` (Slate 800) with 60% opacity (Glassmorphism effect) and a subtle border `#334155` (Slate 700).
  - **Primary Metric (Sales/Revenue)**: `#38bdf8` (Sky Blue)
  - **Secondary Metric (Profit/Growth)**: `#a78bfa` (Purple)
  - **Success/On-Time (KPIs)**: `#34d399` (Emerald Green)
  - **Warning/Late/Returns**: `#fb7185` (Coral Red)
  - **Text Colors**: `#f8fafc` (Title text, active metrics) and `#94a3b8` (Labels, tooltips, secondary descriptions).
* **Typography**:
  - **Font Family**: Inter, Outfit, or Segoe UI.
  - **Headers**: 20pt Bold (Page Titles), 14pt Semi-bold (Section Titles).
  - **KPI Numbers**: 28pt Bold (Glowing effect enabled).

---

## 2. Interactive Navigation & Layout Structure

A persistent left navigation sidebar or a floating header navigation bar is configured using Power BI **Bookmarks & Buttons**:
- **Sidebar Icons**:
  - 🏠 **Executive Summary** (Links to Page 1)
  - 📈 **Sales Performance** (Links to Page 2)
  - 👥 **Customer Analytics** (Links to Page 3)
  - 📦 **Product Deep Dive** (Links to Page 4)
  - 🗺️ **Regional Insights** (Links to Page 5)

---

## 3. Detailed Page Layout Specs

### Page 1: Executive Summary
*Designed for C-suite decision-makers. Provides a high-level view of company health, revenue, and core growth trends.*

```
+--------------------------------------------------------------------------------------+
|  [LOGO] E-COMMERCE EXECUTIVE SUMMARY                                   [Date Slicer] |
+--------------------------------------------------------------------------------------+
|  +------------------+  +------------------+  +------------------+  +--------------+  |
|  | TOTAL REVENUE    |  | PROFIT MARGIN    |  | ACTIVE CUSTOMERS |  | AVG CSAT     |  |
|  | $38.36M          |  | 35.00%           |  | 27,829           |  | 4.37 / 5.0   |  |
|  | (+12% YoY)       |  | (Target: 32%)    |  | (+8.5% YoY)      |  | (+2% MoM)    |  |
|  +------------------+  +------------------+  +------------------+  +--------------+  |
+--------------------------------------------------------------------------------------+
|  +--------------------------------------------+  +--------------------------------+  |
|  | Monthly Sales Revenue Trend & Forecast      |  | Customer RFM Segments Share    |  |
|  | (Line chart + 6-month projected forecast)   |  | (Donut chart showing Champions |  |
|  | Axis: Month; Values: Revenue & Forecast     |  | Active, Loyal, At Risk, Churn) |  |
|  +--------------------------------------------+  +--------------------------------+  |
+--------------------------------------------------------------------------------------+
|  +--------------------------------------------+  +--------------------------------+  |
|  | Top 5 Sales Categories                      |  | Delivery Performance Gauge     |  |
|  | (Horizontal bar chart: Electronics, etc.)   |  | On-time: 91.5% | Delayed: 8.5% |  |
|  +--------------------------------------------+  +--------------------------------+  |
+--------------------------------------------------------------------------------------+
```

---

### Page 2: Sales Performance Dashboard
*Designed for Sales and Marketing managers. Analyzes trends, order value distribution, and transaction volumes.*

* **KPI Cards**:
  - Total Orders: `85,000`
  - Total Revenue: `$38.36M`
  - Average Order Value (AOV): `$451.34`
* **Visuals**:
  - **Sales Revenue by Day of Week** (Bar Chart): Shows order concentration during Monday–Wednesday.
  - **Orders and AOV by Month** (Combo Chart: Columns for order count, Line for AOV): Highlights seasonal purchase value changes.
  - **Payment Method Split** (Treemap): Interactive breakdown of Credit Card (73%), Boleto (19%), Voucher (5%), and Debit Card (3%).
  - **Sales Value Table**: Interactive table for scrolling orders, status, payment sequence, and total transaction values.

---

### Page 3: Customer Analytics
*Designed for Customer Success and Retention teams. Focuses on loyalty cohorts, RFM scoring, and spend distribution.*

* **KPI Cards**:
  - Customer Lifetime Value (CLV): `$1,378.55`
  - Repeat Customer Rate: `56.51%`
  - Retention Rate: `59.02%` (Churn Rate: `40.98%`)
* **Visuals**:
  - **Pareto Spend Analysis Chart** (Combo Chart): Line representing cumulative spend percentage, bars representing sorted customer monetary value. Visually shows that 29.5% of customers drive 80% of revenue.
  - **RFM Customer Segments Matrix** (Heatmap / Treemap): Breakdown of segment populations (Champions, Loyal, Hibernating, At Risk, New).
  - **Customer Cohort Retention Curve** (Line Chart): Displays month-by-month retention rates for customer cohorts across 2024 and 2025.
  - **Customer Search / Details Drill-through Table**: Shows individual customer details, signup dates, orders count, spend, and their RFM loyalty score.

---

### Page 4: Product Deep Dive
*Designed for Category Managers and Product merchandisers. Details item categories, pricing classes, and logistics quality.*

* **KPI Cards**:
  - Total Products Catalog: `2,500`
  - Overall Return Rate: `3.30%`
  - Average Review Score: `4.37`
* **Visuals**:
  - **ABC Category Distribution** (Grouped Bar Chart): Shows Class A (3.7% products making 69.9% sales), Class B (19.7% products making 20.1% sales), and Class C (76.6% products making 10.0% sales).
  - **Top 10 Selling Products** (Horizontal Bar Chart / Table): Dynamic table containing product ID, English category name, total quantities sold, return count, and gross profit.
  - **Average review score by Product Category** (Bar Chart): Highlights customer rating gaps across product lines.
  - **Returns by Reason** (Pie Chart): Defective (35%), wrong item (25%), unsatisfied (30%), delayed delivery (10%).

---

### Page 5: Regional Logistics Dashboard
*Designed for Operations and Supply Chain coordinators. Displays regional sales distribution, delivery performance, and delays.*

* **KPI Cards**:
  - Avg Delivery Time: `6.57 days`
  - Delayed Orders Count: `7,225 orders`
  - Shipping Cost Ratio (Freight / Revenue): `12.5%`
* **Visuals**:
  - **US / Brazil Regional Sales Map** (Choropleth Map): Visualizes state sales density, highlighting São Paulo (SP), Rio de Janeiro (RJ), and Minas Gerais (MG) as top hubs.
  - **Top States by Revenue** (Horizontal Bar Chart): Ranks states SP, RJ, MG, RS, PR, etc., with sales value labels.
  - **Average Shipping Duration by State** (Bar Chart): Identifies regions with logistically delayed carrier transit.
  - **Delayed Delivery Rate Trend** (Line Chart): Month-over-month rate of orders arriving past their estimated delivery date.

---

## 4. Advanced Interactive Features

### A. Slicers & Filters
- **Persistent Header Filter Row**:
  - **Date Slicer**: Relative date slider (e.g. Last 12 Months) or a calendar date picker.
  - **State Slicer**: Multiselect list of customer states (SP, RJ, MG, etc.).
  - **Category Slicer**: Dropdown containing product categories.

### B. Tooltips
- **Custom Tooltip Pages**:
  - Hovering over any category on the Executive or Product page shows a custom visual tooltip page containing:
    1. Top 3 selling products in that category.
    2. Category return rate and average rating.
  - Hovering over a state on the map displays its top seller city and delayed shipment count.

### C. Drill-Through Path
- **Customer Analysis Path**:
  - Users can right-click a segment on the RFM Donut chart on Page 3 and select **"Drill Through -> Customer Loyalty Details Table"** to view a filtered list of all customers belonging to that specific segment.
- **Product Category Path**:
  - Right-clicking on a product category on Page 4 opens the detailed product table page showing only items in that category.
