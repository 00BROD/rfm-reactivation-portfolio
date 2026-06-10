-- ============================================================
--  Online Retail — Analyst SQL Showcase
--  Source: UCI Online Retail (UK e-commerce, Dec 2010–Dec 2011)
--  Table `sales` = real revenue rows (known customer, qty>0, price>0, not cancelled)
-- ============================================================

-- Q1 — Headline KPIs ----------------------------------------------------------
SELECT
  COUNT(DISTINCT InvoiceNo)                AS orders,
  COUNT(DISTINCT CustomerID)               AS customers,
  ROUND(SUM(Revenue), 0)                   AS revenue_gbp,
  ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 2) AS avg_order_value
FROM sales;

-- Q2 — Monthly revenue trend --------------------------------------------------
SELECT InvoiceMonth,
       ROUND(SUM(Revenue), 0)            AS revenue_gbp,
       COUNT(DISTINCT InvoiceNo)         AS orders,
       COUNT(DISTINCT CustomerID)        AS active_customers
FROM sales
GROUP BY InvoiceMonth
ORDER BY InvoiceMonth;

-- Q3 — Top 10 products by revenue ---------------------------------------------
SELECT StockCode, MAX(Description) AS product,
       ROUND(SUM(Revenue), 0)   AS revenue_gbp,
       SUM(Quantity)            AS units
FROM sales
GROUP BY StockCode
ORDER BY revenue_gbp DESC
LIMIT 10;

-- Q4 — Revenue concentration by country (UK vs rest) --------------------------
SELECT Country,
       ROUND(SUM(Revenue), 0)                                   AS revenue_gbp,
       ROUND(100.0 * SUM(Revenue) / (SELECT SUM(Revenue) FROM sales), 1) AS pct_of_total
FROM sales
GROUP BY Country
ORDER BY revenue_gbp DESC
LIMIT 10;

-- Q5 — Revenue Pareto: do 20% of customers drive 80% of revenue? --------------
WITH cust AS (
  SELECT CustomerID, SUM(Revenue) AS rev
  FROM sales GROUP BY CustomerID
),
ranked AS (
  SELECT CustomerID, rev,
         SUM(rev) OVER (ORDER BY rev DESC) AS running,
         SUM(rev) OVER ()                  AS total,
         ROW_NUMBER() OVER (ORDER BY rev DESC) AS rn,
         COUNT(*)    OVER ()               AS n
  FROM cust
)
SELECT ROUND(100.0 * rn / n, 0)          AS top_pct_customers,
       ROUND(100.0 * running / total, 0) AS pct_revenue_captured
FROM ranked
WHERE rn IN (CAST(n*0.1 AS INT), CAST(n*0.2 AS INT), CAST(n*0.5 AS INT));

-- Q6 — RFM customer segmentation ---------------------------------------------
--   Recency  = days since last purchase (snapshot = day after last invoice)
--   Frequency= distinct orders
--   Monetary = total revenue
--   Score each 1–4 by quartile, then label segments.
WITH snapshot AS (SELECT DATE(MAX(InvoiceDate), '+1 day') AS snap FROM sales),
rfm AS (
  SELECT CustomerID,
         CAST(julianday((SELECT snap FROM snapshot)) - julianday(MAX(InvoiceDate)) AS INT) AS recency,
         COUNT(DISTINCT InvoiceNo) AS frequency,
         ROUND(SUM(Revenue), 2)    AS monetary
  FROM sales GROUP BY CustomerID
),
scored AS (
  SELECT *,
         NTILE(4) OVER (ORDER BY recency DESC)   AS r,   -- recent => high
         NTILE(4) OVER (ORDER BY frequency ASC)  AS f,
         NTILE(4) OVER (ORDER BY monetary ASC)   AS m
  FROM rfm
)
SELECT
  CASE
    WHEN r>=3 AND f>=3 AND m>=3 THEN 'Champions'
    WHEN r>=3 AND f>=2          THEN 'Loyal'
    WHEN r>=3                   THEN 'Recent / New'
    WHEN r<=2 AND f>=3          THEN 'At Risk (was valuable)'
    ELSE                             'Lapsed / Low'
  END                              AS segment,
  COUNT(*)                         AS customers,
  ROUND(AVG(recency),0)            AS avg_recency_days,
  ROUND(AVG(frequency),1)          AS avg_orders,
  ROUND(SUM(monetary),0)           AS revenue_gbp
FROM scored
GROUP BY segment
ORDER BY revenue_gbp DESC;
