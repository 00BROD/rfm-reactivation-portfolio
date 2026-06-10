"""ETL: Online Retail.xlsx -> SQLite. Run once; ~60s (Excel parse is the cost)."""
import pandas as pd, sqlite3, pathlib, sys

SRC = "data/Online Retail.xlsx"
DB  = "data/retail.db"

def main():
    print("loading excel (slow, one-time)...", flush=True)
    df = pd.read_excel(SRC, engine="openpyxl")
    df.columns = [c.strip() for c in df.columns]

    # Clean / enrich
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Revenue"]     = df["Quantity"] * df["UnitPrice"]
    df["IsCancelled"] = df["InvoiceNo"].astype(str).str.startswith("C")
    df["InvoiceDay"]  = df["InvoiceDate"].dt.date.astype(str)
    df["InvoiceMonth"]= df["InvoiceDate"].dt.to_period("M").astype(str)

    # 'clean' = real sales: paying customer known, positive qty & price, not a cancellation
    clean = df[(~df.IsCancelled) & (df.Quantity > 0) & (df.UnitPrice > 0)
               & (df.CustomerID.notna())].copy()
    clean["CustomerID"] = clean.CustomerID.astype(int)

    con = sqlite3.connect(DB)
    df.to_sql("raw",   con, if_exists="replace", index=False)
    clean.to_sql("sales", con, if_exists="replace", index=False)
    con.executescript("""
      CREATE INDEX IF NOT EXISTS ix_sales_cust  ON sales(CustomerID);
      CREATE INDEX IF NOT EXISTS ix_sales_month ON sales(InvoiceMonth);
      CREATE INDEX IF NOT EXISTS ix_sales_stock ON sales(StockCode);
    """)
    con.commit()
    n_raw  = con.execute("SELECT COUNT(*) FROM raw").fetchone()[0]
    n_sale = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    rev    = con.execute("SELECT ROUND(SUM(Revenue),2) FROM sales").fetchone()[0]
    con.close()
    print(f"raw={n_raw:,}  sales={n_sale:,}  revenue=£{rev:,.0f}  -> {DB}")

if __name__ == "__main__":
    main()
