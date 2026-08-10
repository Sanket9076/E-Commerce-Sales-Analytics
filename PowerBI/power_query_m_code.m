// Power Query M Transformation Scripts & ETL Pipeline
// Project: E-Commerce Sales & Supply Chain Analytics

// ==========================================
// 1. Dim_Date (Dynamic Calendar Generator)
// ==========================================
let
    StartDate = #date(2024, 1, 1),
    EndDate = #date(2026, 12, 31),
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    Source = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    #"Converted to Table" = Table.FromList(Source, Splitter.SplitByNothing(), {"Date"}, null, ExtraValues.Error),
    #"Changed Type" = Table.TransformColumnTypes(#"Converted to Table",{{"Date", type date}}),
    #"Added Year" = Table.AddColumn(#"Changed Type", "Year", each Date.Year([Date]), Int64.Type),
    #"Added Quarter" = Table.AddColumn(#"Added Year", "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    #"Added Month" = Table.AddColumn(#"Added Quarter", "MonthNo", each Date.Month([Date]), Int64.Type),
    #"Added Month Name" = Table.AddColumn(#"Added Month", "MonthName", each Date.MonthName([Date]), type text),
    #"Added Day of Week" = Table.AddColumn(#"Added Month Name", "DayOfWeek", each Date.DayOfWeekName([Date]), type text),
    #"Added IsWeekend" = Table.AddColumn(#"Added Day of Week", "IsWeekend", each if Date.DayOfWeek([Date], Day.Monday) >= 5 then 1 else 0, Int64.Type)
in
    #"Added IsWeekend"

// ==========================================
// 2. Fact_OrderItems ETL & Transformation
// ==========================================
let
    Source = Csv.Document(File.Contents(FolderPath & "\Fact_OrderItems.csv"),[Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"order_item_id", Int64.Type}, 
        {"order_id", type text}, 
        {"product_id", type text}, 
        {"seller_id", type text}, 
        {"customer_id", type text}, 
        {"order_date", type date}, 
        {"unit_price", Currency.Type}, 
        {"freight_value", Currency.Type}, 
        {"quantity", Int64.Type}, 
        {"item_revenue", Currency.Type}, 
        {"estimated_gross_profit", Currency.Type}
    })
in
    #"Changed Type"

// ==========================================
// 3. Fact_Shipping (Supply Chain Telemetry)
// ==========================================
let
    Source = Csv.Document(File.Contents(FolderPath & "\Fact_Shipping.csv"),[Delimiter=",", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"shipping_id", type text},
        {"order_id", type text},
        {"customer_id", type text},
        {"shipping_carrier", type text},
        {"shipping_tracking_number", type text},
        {"shipping_status", type text},
        {"purchase_date", type date},
        {"shipping_estimated_delivery_date", type datetime},
        {"shipping_actual_delivery_date", type datetime},
        {"delivery_lead_days", type number},
        {"delivery_delay_days", type number},
        {"is_on_time", Int64.Type}
    }),
    #"Added SLA Category" = Table.AddColumn(#"Changed Type", "SLA_Status", each if [is_on_time] = 1 then "On-Time" else "Delayed", type text)
in
    #"Added SLA Category"

// ==========================================
// 4. Data Model Relationships (Star Schema)
// ==========================================
/*
1. Fact_OrderItems[product_id]  -->  Dim_Product[product_id] (Many-to-One)
2. Fact_OrderItems[customer_id] -->  Dim_Customer[customer_id] (Many-to-One)
3. Fact_OrderItems[seller_id]   -->  Dim_Seller[seller_id] (Many-to-One)
4. Fact_OrderItems[order_date]  -->  Dim_Date[Date] (Many-to-One)
5. Fact_Shipping[order_id]      -->  Fact_OrderItems[order_id] (One-to-Many)
6. Fact_Shipping[purchase_date] -->  Dim_Date[Date] (Many-to-One)
*/
