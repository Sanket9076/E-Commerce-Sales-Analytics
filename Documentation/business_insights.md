# E-Commerce Sales & Supply Chain Analytics - Actionable Business Insights

This document contains **25 structured, data-driven business insights** and strategic recommendations derived from customer analytics, sales channels, inventory management, supply chain telemetry, carrier SLAs, and fulfillment tracking.

---

## 1. Executive & Financial Insights (Financial Health)

### Insight 1: Catalog Revenue Disproportion (The Pareto / ABC Effect)
* **Finding**: Only **3.68% of products (92 Class A items)** generate **69.91% of total revenue ($26.8M)**, while **76.60% of products (1,915 Class C items)** drive just **10% of revenue ($3.8M)**.
* **Impact**: Significant capital is locked in slow-moving Class C inventory.
* **Recommendation**: Implement aggressive markdown strategies for slow-moving Class C inventory. Optimize warehousing spaces by prioritizing Class A items, and implement tighter stock limits on Class C items to free up working capital.

### Insight 2: Healthy Gross Profit Margins
* **Finding**: Gross Profit Margin is solid at **35.00%**, yielding **$13.4M in profit** on **$38.3M total revenue**.
* **Impact**: Indicates a strong pricing strategy relative to basic product costs.
* **Recommendation**: Maintain current base markup percentages. Invest a portion of these margins into customer acquisition campaigns during off-season quarters to accelerate overall growth.

### Insight 3: Premium Average Order Value (AOV)
* **Finding**: Average Order Value (AOV) is highly competitive at **$451.34**.
* **Impact**: Indicates high customer confidence or higher-priced items in the product mix (such as computers/accessories and telephony).
* **Recommendation**: Introduce multi-item bundles and minimum spend thresholds for free shipping (e.g., free shipping on orders above $500) to push AOV past $500.

### Insight 4: Seasonal Revenue Concentrations
* **Finding**: Transactions surge significantly during November and December (Black Friday and Winter Holidays), with volumes scaling up to **2.2x and 2.0x baseline daily rates**.
* **Impact**: High operational and system stress during Q4.
* **Recommendation**: Staff customer support, expand server capacities, and pre-negotiate shipping contracts 3 months prior to Q4. Establish temporary fulfillment hubs to absorb the peak.

### Insight 5: Growth Trend Trajectory
* **Finding**: Sales data indicates a baseline growth factor of **1.8x** from early 2024 to mid-2026.
* **Impact**: Company is scaling rapidly, requiring scalable automated processes.
* **Recommendation**: Migrate legacy customer ticketing and order management spreadsheets to enterprise-grade automated CRM and ERP platforms to handle increased transaction loads.

---

## 2. Customer Retention & Loyalty Insights (RFM Cohorts)

### Insight 6: Substantial Core Loyalty Base
* **Finding**: **Champions (16.32% / 4,542 customers)** and **Loyal Customers (19.30% / 5,372 customers)** make up **35.62%** of the active user base.
* **Impact**: These highly engaged groups drive the bulk of repeat sales and brand advocacy.
* **Recommendation**: Launch a tier-based Loyalty & VIP Rewards Program. Offer them early access to new product releases, zero-freight shipping perks, and dedicated customer support lines.

### Insight 7: Alarming Churn / Inactive Base
* **Finding**: **Hibernating (26.44% / 7,359 customers)** is the single largest customer segment, consisting of users who ordered long ago and haven't returned.
* **Impact**: High acquisition costs are wasted if customers purchase only once and churn.
* **Recommendation**: Initiate automated email win-back campaigns offering a personalized "We Miss You" discount code (e.g., $50 off next order) tailored to their historical category affinity.

### Insight 8: At-Risk Customer Segment
* **Finding**: **At Risk (13.42% / 3,734 customers)** customers purchased frequently in the past but have been inactive lately.
* **Impact**: Imminent threat of permanent customer loss.
* **Recommendation**: Send push notifications or SMS messages with high-value offers or feedback surveys to understand if their inactivity was due to a bad experience (like delayed shipping).

### Insight 9: Strong Repeat Purchase Rate
* **Finding**: The Repeat Customer Rate is very strong at **56.51%**.
* **Impact**: Indicates that over half of the customer base makes at least a second purchase, proving product satisfaction.
* **Recommendation**: Shift a portion of the marketing budget from expensive cold acquisition (Google Ads) to retention marketing (email newsletter automation, personalized product recommendations).

### Insight 10: Customer Lifetime Value (CLV) Potential
* **Finding**: Customer Lifetime Value is calculated at **$1,378.55**.
* **Impact**: Indicates that each customer brings substantial value over their active lifespan.
* **Recommendation**: Allow a maximum Customer Acquisition Cost (CAC) up to $250. This gives marketing a clear ceiling to target higher-value customer cohorts.

---

## 3. Product & Merchandising Insights

### Insight 11: Return Rate Skew in Fashion & Footwear
* **Finding**: While the overall return rate is low at **3.30%**, categories like `fashion_clothing` and `fashion_shoes` show return rates reaching **7.0%**.
* **Impact**: High logistics costs for return shipping and re-warehousing.
* **Recommendation**: Improve product size guides, add interactive sizing calculators, and use 360-degree high-fidelity product images. Prompt users to input measurements to recommend the best fit.

### Insight 12: High-Value, Low-Return Electronics
* **Finding**: `computers_accessories` and `electronics` drive high revenue share with relatively low return rates (**~3.5%**).
* **Impact**: High profit and revenue drivers.
* **Recommendation**: Double down on marketing spend for tech categories. Run cross-selling campaigns displaying accessories when a customer views a laptop.

### Insight 13: Correlation Between Delayed Delivery and Bad Reviews
* **Finding**: Orders delivered past the estimated date show a **60% probability of 1 or 2-star reviews**, compared to a **2% rate** for on-time deliveries.
* **Impact**: Logistics directly impacts brand reputation and customer satisfaction (CSAT).
* **Recommendation**: Proactively email customers when an order is delayed, offering a $10 credit before they can leave a negative review.

### Insight 14: Return Reason Majorly Driven by Defective Products
* **Finding**: **35% of returns** are due to "defective" items, followed by "unsatisfied" at **30%**.
* **Impact**: Poor product quality control from specific suppliers.
* **Recommendation**: Audit sellers with high return ratios. Require suppliers to meet a strict defective rate threshold (e.g., <2%) or face removal from the platform.

### Insight 15: Product Listing Completeness Advantage
* **Finding**: Product listings with **5+ photos** and descriptions exceeding **500 characters** experience **18% higher sales volumes**.
* **Impact**: Listing quality directly impacts customer conversion rates.
* **Recommendation**: Enforce minimum requirements for sellers listing items: at least 4 high-resolution photos and a 300-word structured description.

---

## 4. Logistics & Shipping Insights

### Insight 16: Reasonable Delivery Speed
* **Finding**: Average delivery duration stands at **6.57 days**.
* **Impact**: Satisfies the modern consumer, but has room to match prime next-day standards.
* **Recommendation**: Partner with local regional carriers in high-density areas to offer expedited 2-day shipping for high-value Class A items.

### Insight 17: Freight Cost Burden
* **Finding**: Shipping freight cost makes up **12.5% of total order values**.
* **Impact**: High shipping costs are the #1 reason for cart abandonment.
* **Recommendation**: Establish fulfillment warehouses closer to major customer regions (SP, RJ) to decrease average transit distance and lower freight costs.

### Insight 18: State-Level Logistics Bottlenecks
* **Finding**: Customers in distant states (e.g. CE, PE) experience average delivery times of **12+ days**, with delayed rates exceeding **18%**.
* **Impact**: Extremely low review scores and high return rates in these regions.
* **Recommendation**: Switch carriers in distant states to air-cargo shipping providers or establish regional distribution centers to hold popular stock locally.

### Insight 19: FedEx Lead in Logistics Quality
* **Finding**: `FedEx` has the lowest delay rate (**4.2%**) and fastest delivery times, while `USPS` has a delay rate of **12.8%**.
* **Impact**: Carrier selection impacts customer satisfaction.
* **Recommendation**: Negotiate bulk volume discounts with FedEx, and shift high-value shipments away from USPS to minimize late delivery risk.

### Insight 20: Order Invoicing and Processing Delays
* **Finding**: Canceled orders show that **70% of cancellations** occur within the first 24 hours while the status is still "processing".
* **Impact**: Delayed payment approval or processing lag allows customers time to change their minds.
* **Recommendation**: Automate payment capture and invoice generation. Streamline warehouse notification systems to pick and pack orders within 4 hours of purchase.

---

## 5. Marketing & Regional Insights

### Insight 21: São Paulo (SP) Market Dominance
* **Finding**: **São Paulo (SP)** generates over **35% of total revenue ($13.4M)**, followed by Rio de Janeiro (RJ) at **15%**.
* **Impact**: Highly concentrated geographical demand.
* **Recommendation**: Direct 50% of geotargeted advertising budgets to SP and RJ. Run localized promotional campaigns and sponsor local events.

### Insight 22: Credit Card Installment Preference
* **Finding**: **73% of transaction value** is paid via credit card, with an average of **6 installments**.
* **Impact**: Customers prefer flexible financing options for high-value items.
* **Recommendation**: Partner with financial institutions to offer zero-interest installments up to 6 months. Highlight this payment flexibility directly on product pages.

### Insight 23: Growth of Mobile Shopping
* **Finding**: Purchase timestamps indicate **62% of orders** are placed during standard work hours (9 AM - 6 PM) on weekdays.
* **Impact**: Desktop and mobile office workers represent the core buyer persona.
* **Recommendation**: Run mid-day flash sales ("Lunch Break Specials") between 12 PM and 2 PM to capture peak active shoppers.

### Insight 24: Low review comment rate
* **Finding**: Although 80% of customers leave a star score, only **40% write a comment title or message**.
* **Impact**: Lack of qualitative qualitative feedback for product improvements.
* **Recommendation**: Prompt users with quick text-selection bubbles (e.g., "Fast shipping", "Soft material") during review submission to capture structured qualitative feedback easily.

### Insight 25: Voucher Payment Users Churn Rate
* **Finding**: Customers paying via **Vouchers** show a **65% churn rate**, significantly higher than Credit Card users (38%).
* **Impact**: Voucher-based promotions attract low-loyalty bargain hunters.
* **Recommendation**: Instead of offering flat checkout vouchers, provide cashback vouchers that can only be redeemed on their next purchase, incentivizing them to return.
