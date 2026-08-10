# Data Dictionary - E-Commerce Sales & Supply Chain Analytics Database

This document provides a detailed layout, data types, constraints, and descriptions for all tables in the relational database model of the **E-Commerce Sales & Supply Chain Analytics** project.

---

## 1. Table: `categories`
*Contains the product category name in native Portuguese (or standard identifiers) and its English translation.*

| Column Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `product_category_name` | VARCHAR(100) | PK, Not Null | Native category code name (e.g. `electronics`). |
| `product_category_name_english` | VARCHAR(100) | Not Null | English translation of the category (e.g. `Electronics`). |

---

## 2. Table: `sellers`
*Contains profiles of sellers supplying products in the e-commerce marketplace.*

| Column Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `seller_id` | VARCHAR(50) | PK, Not Null | Unique identifier for each seller. |
| `seller_zip_code_prefix` | VARCHAR(10) | Nullable | Zip code prefix of the seller's primary warehouse location. |
| `seller_city` | VARCHAR(100) | Nullable | City where the seller is located. |
| `seller_state` | VARCHAR(10) | Nullable | State code where the seller is located. |

---

## 3. Table: `customers`
*Contains demographic profiles and locations of registered customers.*

| Column Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `customer_id` | VARCHAR(50) | PK, Not Null | Unique ID identifying a customer delivery address profile. |
| `customer_unique_id` | VARCHAR(50) | Not Null, Index | Master User ID. A user can have multiple customer_ids for separate addresses. |
| `customer_zip_code_prefix` | VARCHAR(10) | Nullable | Zip code prefix of the customer. |
| `customer_city` | VARCHAR(100) | Nullable | City where the customer lives. |
| `customer_state` | VARCHAR(10) | Nullable | State code where the customer lives. |

---

## 4. Table: `products`
*Contains dimensional characteristics and base pricing for catalog items.*

| Column Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `product_id` | VARCHAR(50) | PK, Not Null | Unique identifier for each product. |
| `product_category_name` | VARCHAR(100) | FK, Nullable | Foreign key referencing `categories(product_category_name)`. |
| `product_name_length` | INT | Nullable | Number of characters in the product name. |
| `product_description_length` | INT | Nullable | Number of characters in the product description. |
| `product_photos_qty` | INT | Nullable | Number of photos available for the product listing. |
| `product_weight_g` | DECIMAL(10,2) | Nullable, Non-negative | Weight of the product in grams. |
| `product_length_cm` | INT | Nullable | Length of the product packaging in centimeters. |
| `product_height_cm` | INT | Nullable | Height of the product packaging in centimeters. |
| `product_width_cm` | INT | Nullable | Width of the product packaging in centimeters. |
| `product_base_price` | DECIMAL(10,2) | Not Null, Non-negative | Standard catalog selling price for the product. |

---

## 5. Table: `orders`
*Core transaction header recording customer purchases and logistics progress timestamps.*

| Column Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `order_id` | VARCHAR(50) | PK, Not Null | Unique identifier for each order. |
| `customer_id` | VARCHAR(50) | FK, Not Null, Index | Foreign key referencing `customers(customer_id)`. |
| `order_status` | VARCHAR(20) | Not Null | Order status: `delivered`, `shipped`, `processing`, `canceled`, `invoiced`, `unavailable`. |
| `order_purchase_timestamp` | DATETIME | Not Null, Index | Date and time the order was placed. |
| `order_approved_at` | DATETIME | Nullable | Date and time payment was approved. |
| `order_delivered_carrier_date` | DATETIME | Nullable | Date and time the order was handed over to the carrier. |
| `order_delivered_customer_date` | DATETIME | Nullable | Date and time the order was delivered to the customer. |
| `order_estimated_delivery_date` | DATETIME | Not Null | Promised delivery deadline given to the customer at checkout. |

---

## 6. Table: `order_items`
*Contains transaction line items details indicating products, quantities, prices, and shipping fees.*

| Column Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `order_item_id` | INT | PK, Not Null | Unique line item ID. |
| `order_id` | VARCHAR(50) | FK, Not Null, Index | Foreign key referencing `orders(order_id)`. |
| `product_id` | VARCHAR(50) | FK, Not Null, Index | Foreign key referencing `products(product_id)`. |
| `seller_id` | VARCHAR(50) | FK, Not Null | Foreign key referencing `sellers(seller_id)`. |
| `price` | DECIMAL(10,2) | Not Null, Non-negative | Actual unit price paid (excluding shipping). |
| `freight_value` | DECIMAL(10,2) | Not Null, Non-negative | Shipping fee allocated to this item. |
| `quantity` | INT | Not Null, Default 1 | Quantity of this product ordered in this item line. |

---

## 7. Table: `payments`
*Records the method and details of payments linked to each transaction.*

| Column Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `order_id` | VARCHAR(50) | Composite PK, FK | Foreign key referencing `orders(order_id)`. |
| `payment_sequential` | INT | Composite PK, Default 1 | Payment split sequence index (e.g. 1, 2, ...). |
| `payment_type` | VARCHAR(30) | Not Null | Payment method: `credit_card`, `boleto`, `voucher`, `debit_card`. |
| `payment_installments` | INT | Not Null, Default 1 | Number of installment payments (Credit Card only). |
| `payment_value` | DECIMAL(10,2) | Not Null, Non-negative | Amount of money paid in this installment. |

---

## 8. Table: `shipping`
*Tracks carrier and logistics details for each shipment.*

| Column Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `shipping_id` | VARCHAR(50) | PK, Not Null | Unique identifier for the shipping profile. |
| `order_id` | VARCHAR(50) | FK, Not Null, Index | Foreign key referencing `orders(order_id)`. |
| `shipping_carrier` | VARCHAR(50) | Not Null | Logistics carrier company (e.g. `FedEx`, `DHL`). |
| `shipping_tracking_number` | VARCHAR(50) | Not Null | Shipping tracking number. |
| `shipping_estimated_delivery_date`| DATETIME | Not Null | Expected delivery date. |
| `shipping_actual_delivery_date` | DATETIME | Nullable | Real carrier delivery confirmation timestamp. |
| `shipping_status` | VARCHAR(20) | Not Null | Status: `pending`, `in_transit`, `delivered`, `failed`. |

---

## 9. Table: `reviews`
*Contains satisfaction scores and text reviews left by customers after purchase.*

| Column Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `review_id` | VARCHAR(50) | PK, Not Null | Unique identifier for the review. |
| `order_id` | VARCHAR(50) | FK, Not Null, Index | Foreign key referencing `orders(order_id)`. |
| `review_score` | INT | Not Null | Customer satisfaction score (1 to 5 stars). |
| `review_comment_title` | VARCHAR(200) | Nullable | Review title. |
| `review_comment_message` | TEXT | Nullable | Full review comments text. |
| `review_creation_date` | DATETIME | Not Null | Date and time the review survey was created. |
| `review_answer_timestamp` | DATETIME | Nullable | Date and time the review was submitted. |

---

## 10. Table: `returns`
*Tracks product returns, reasons, and approval status.*

| Column Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `return_id` | VARCHAR(50) | PK, Not Null | Unique identifier for each return request. |
| `order_id` | VARCHAR(50) | FK, Not Null, Index | Foreign key referencing `orders(order_id)`. |
| `product_id` | VARCHAR(50) | FK, Not Null | Foreign key referencing `products(product_id)`. |
| `return_reason` | VARCHAR(50) | Not Null | Return reason: `defective`, `wrong_item`, `unsatisfied`, `delayed_delivery`. |
| `return_date` | DATETIME | Not Null | Date the return request was filed. |
| `return_status` | VARCHAR(20) | Not Null | Status: `approved`, `rejected`, `pending`. |
