# Power BI DAX Measures & Power Query Documentation

This document lists the data transformations in Power Query and the catalog of calculated columns and DAX measures developed for the **E-Commerce Sales & Supply Chain Analytics** project.

---

## 1. Power Query Data Transformations (M Code)

To prepare the dataset for dimensional modeling, we executed the following steps in Power Query Editor:

### A. Date Dimension Creation (`Dim_Date`)
Generated a continuous date calendar dimension table linked to `orders[order_purchase_timestamp]`:
```powerquery
let
    StartDate = #date(2024, 1, 1),
    EndDate = #date(2026, 12, 31),
    NumberOfDays = Duration.Days(EndDate - StartDate) + 1,
    Source = List.Dates(StartDate, NumberOfDays, #duration(1, 0, 0, 0)),
    TableFromList = Table.FromList(Source, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    RenameDate = Table.RenameColumns(TableFromList,{{"Column1", "Date"}}),
    ChangeType = Table.TransformColumnTypes(RenameDate,{{"Date", type date}}),
    AddYear = Table.AddColumn(ChangeType, "Year", each Date.Year([Date]), Int64.Type),
    AddMonthNum = Table.AddColumn(AddYear, "Month Number", each Date.Month([Date]), Int64.Type),
    AddMonthName = Table.AddColumn(AddMonthNum, "Month Name", each Date.MonthName([Date]), type text),
    AddQuarter = Table.AddColumn(AddMonthName, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    AddDayOfWeek = Table.AddColumn(AddQuarter, "Day of Week", each Date.DayOfWeekName([Date]), type text),
    AddWeekdayNum = Table.AddColumn(AddDayOfWeek, "Weekday Number", each Date.DayOfWeek([Date]), Int64.Type),
    AddIsWeekend = Table.AddColumn(AddWeekdayNum, "Is Weekend", each if Date.DayOfWeek([Date]) = 5 or Date.DayOfWeek([Date]) = 6 then "Weekend" else "Weekday", type text)
in
    AddIsWeekend
```

### B. Cleaning & Conversions in Power Query
1. **Fact_Orders**:
   - Split date-time columns into Date types.
   - Replaced nulls in `order_delivered_customer_date` conditionally: If status is `delivered` and date is blank, impute with `order_purchase_timestamp` + 7 days.
2. **Dim_Products**:
   - Filtered out negative weight/dimensions rows (converted to absolute value in SQL/Python, verified absolute values in Power Query).
   - Replaced price outlier `$99,999` with category median.

---

## 2. Model Relationships (Star Schema)

* **Fact_Orders** `(1) <---> (*) Fact_Order_Items` on `order_id` (Active, 1-to-many, bidirectional)
* **Dim_Customers** `(1) <---> (*) Fact_Orders` on `customer_id` (Active, 1-to-many)
* **Dim_Products** `(1) <---> (*) Fact_Order_Items` on `product_id` (Active, 1-to-many)
* **Dim_Sellers** `(1) <---> (*) Fact_Order_Items` on `seller_id` (Active, 1-to-many)
* **Dim_Date** `(1) <---> (*) Fact_Orders` on `Date` <---> `order_purchase_timestamp` (Active, 1-to-many)
* **Fact_Orders** `(1) <---> (0..1) Fact_Shipping` on `order_id` (Active, 1-to-1)
* **Fact_Orders** `(1) <---> (*) Fact_Payments` on `order_id` (Active, 1-to-many)
* **Fact_Orders** `(1) <---> (*) Fact_Reviews` on `order_id` (Active, 1-to-many)
* **Fact_Orders** `(1) <---> (*) Fact_Returns` on `order_id` (Active, 1-to-many)

---

## 3. Calculated Columns (DAX)

### A. Dim_Customers
* **Customer Segment (RFM)** (Used to store the customer cohort groups calculated during Python pipeline):
  ```dax
  RFM_Segment = RELATED(rfm_analysis[segment])
  ```

### B. Fact_Orders
* **Delivery Days**: Calculates actual transit duration:
  ```dax
  Delivery_Days = DATEDIFF(Fact_Orders[order_purchase_timestamp], Fact_Orders[order_delivered_customer_date], DAY)
  ```
* **Logistics Performance**: Checks if order was delivered late:
  ```dax
  Delivery_Status = 
  IF(
      ISBLANK(Fact_Orders[order_delivered_customer_date]),
      "Pending",
      IF(Fact_Orders[order_delivered_customer_date] <= Fact_Orders[order_estimated_delivery_date], "On Time", "Delayed")
  )
  ```

---

## 4. Calculated Measures (DAX)

### A. Sales & Revenue KPIs
* **Total Product Revenue**: Cumulative revenue excluding shipping freight.
  ```dax
  Total Product Revenue = SUMX(Fact_Order_Items, Fact_Order_Items[price] * Fact_Order_Items[quantity])
  ```
* **Total Shipping Freight**: Cumulative shipping fees paid.
  ```dax
  Total Shipping Freight = SUM(Fact_Order_Items[freight_value])
  ```
* **Total Revenue**: Comprehensive gross revenue.
  ```dax
  Total Revenue = [Total Product Revenue] + [Total Shipping Freight]
  ```
* **Total Cost of Goods Sold (COGS)**: Simulated cost at 65% of item value.
  ```dax
  Total COGS = [Total Product Revenue] * 0.65
  ```
* **Total Gross Profit**: Financial return.
  ```dax
  Total Gross Profit = [Total Product Revenue] - [Total COGS]
  ```
* **Gross Profit Margin %**:
  ```dax
  Gross Profit Margin % = DIVIDE([Total Gross Profit], [Total Product Revenue], 0)
  ```
* **Average Order Value (AOV)**: Average spend per order ID.
  ```dax
  Average Order Value = DIVIDE([Total Product Revenue], DISTINCTCOUNT(Fact_Orders[order_id]), 0)
  ```

### B. Customer Performance KPIs
* **Total Customers**: Count of unique active shoppers.
  ```dax
  Total Customers = DISTINCTCOUNT(Dim_Customers[customer_unique_id])
  ```
* **Repeat Customers**: Customers who have ordered more than once.
  ```dax
  Repeat Customers = 
  CALCULATE(
      DISTINCTCOUNT(Dim_Customers[customer_unique_id]),
      FILTER(
          VALUES(Dim_Customers[customer_unique_id]),
          CALCULATE(DISTINCTCOUNT(Fact_Orders[order_id])) > 1
      )
  )
  ```
* **Repeat Customer Rate %**: Percentage of active base that returns.
  ```dax
  Repeat Customer Rate % = DIVIDE([Repeat Customers], [Total Customers], 0)
  ```
* **Customer Retention Rate %**: Percentage of active base in previous year retained in current period.
  ```dax
  Customer Retention Rate % = 
  VAR CustomersPriorYear = 
      CALCULATETABLE(
          VALUES(Dim_Customers[customer_unique_id]),
          SAMEPERIODLASTYEAR(Dim_Date[Date])
      )
  VAR CustomersCurrentYear = 
      VALUES(Dim_Customers[customer_unique_id])
  VAR RetainedCustomers = 
      INTERSECT(CustomersPriorYear, CustomersCurrentYear)
  RETURN
      DIVIDE(COUNTROWS(RetainedCustomers), COUNTROWS(CustomersPriorYear), 0)
  ```
* **Churn Rate %**: Lost customer rate.
  ```dax
  Churn Rate % = 1 - [Customer Retention Rate %]
  ```
* **Customer Lifetime Value (CLV)**: Average value multiplied by purchase frequency and average lifespan (assumed 2.5 years).
  ```dax
  Customer Lifetime Value (CLV) = 
  VAR AvgPurchaseFrequency = DIVIDE(DISTINCTCOUNT(Fact_Orders[order_id]), [Total Customers], 0)
  RETURN
      [Average Order Value] * AvgPurchaseFrequency * 2.5
  ```

### C. Operations & Quality KPIs
* **Average Delivery Days**:
  ```dax
  Average Delivery Days = AVERAGE(Fact_Orders[Delivery_Days])
  ```
* **Delayed Delivery Rate %**:
  ```dax
  Delayed Delivery Rate % = 
  DIVIDE(
      CALCULATE(COUNT(Fact_Orders[order_id]), Fact_Orders[Delivery_Status] = "Delayed"),
      CALCULATE(COUNT(Fact_Orders[order_id]), Fact_Orders[Delivery_Status] <> "Pending"),
      0
  )
  ```
* **Order Return Rate %**:
  ```dax
  Order Return Rate % = DIVIDE(COUNT(Fact_Returns[return_id]), COUNT(Fact_Order_Items[order_item_id]), 0)
  ```
* **Average Review Score**: Average CSAT rating.
  ```dax
  Average Review Score = AVERAGE(Fact_Reviews[review_score])
  ```
* **Net Promoter Score (NPS) / Satisfaction Index**:
  ```dax
  Net Promoter Score = 
  VAR Promoters = CALCULATE(COUNT(Fact_Reviews[review_id]), Fact_Reviews[review_score] >= 5)
  VAR Detractors = CALCULATE(COUNT(Fact_Reviews[review_id]), Fact_Reviews[review_score] <= 3)
  VAR TotalReviews = COUNT(Fact_Reviews[review_id])
  RETURN
      DIVIDE(Promoters - Detractors, TotalReviews, 0) * 100
  ```

### D. Supply Chain & Logistics KPIs
* **On-Time In-Full Rate (OTIF %)**: Percentage of shipments delivered on or before promised delivery date.
  ```dax
  OTIF % = 
  DIVIDE(
      CALCULATE(COUNT(Fact_Shipping[shipping_id]), Fact_Shipping[is_on_time] = 1),
      COUNT(Fact_Shipping[shipping_id]),
      0
  )
  ```
* **Carrier SLA Breach Rate %**: Percentage of carrier shipments experiencing SLA delays.
  ```dax
  Carrier SLA Breach Rate % = 1 - [OTIF %]
  ```
* **Freight-to-Revenue Ratio %**: Percentage of gross revenue spent on freight & logistics.
  ```dax
  Freight-to-Revenue Ratio % = DIVIDE([Total Shipping Freight], [Total Revenue], 0)
  ```
* **Average Carrier Lead Time (Days)**: Average calendar days elapsed from purchase to carrier delivery.
  ```dax
  Avg Carrier Lead Time = AVERAGE(Fact_Shipping[delivery_lead_days])
  ```

