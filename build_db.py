"""
ETL: Online Retail.xlsx -> SQLite. Run once; ~60s (Excel parse is the cost).
Auto-downloads the source if missing, so `git clone && python build_db.py` works clean.

Cleaning decisions (documented because they change the headline numbers):
  - drop cancellations (InvoiceNo starts 'C'), non-positive qty/price, unknown customer
  - drop NON-PRODUCT service lines (postage, manual adjustments, bank charges, samples...)
    -> they are not sales and were inflating revenue + polluting "top products"
  - flag wholesale/anomaly line items (Quantity >= 5000) and EXCLUDE from `sales`
    -> two single orders (80,995 + 74,215 units) were ~2.7% of revenue on their own
  - keep a `raw` table untouched for auditing
"""
import pandas as pd, sqlite3, pathlib, urllib.request, zipfile, io

URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
SRC = pathlib.Path("data/Online Retail.xlsx")
DB  = "data/retail.db"

# Non-product stock codes: services / fees / adjustments, not merchandise.
SERVICE_CODES = {"POST","DOT","M","C2","BANK CHARGES","PADS","CRUK","AMAZONFEE","S","B","D","GIFT"}
QTY_ANOMALY = 5000   # a gift-retailer line item this large is wholesale/error, not retail demand

def ensure_source():
    if SRC.exists():
        return
    SRC.parent.mkdir(exist_ok=True)
    print("source missing -> downloading from UCI...", flush=True)
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(URL, timeout=120).read()))
    z.extract("Online Retail.xlsx", SRC.parent)
    print("downloaded.", flush=True)

def main():
    ensure_source()
    print("loading excel (slow, one-time)...", flush=True)
    df = pd.read_excel(SRC, engine="openpyxl")
    df.columns = [c.strip() for c in df.columns]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Revenue"]     = df["Quantity"] * df["UnitPrice"]
    df["IsCancelled"] = df["InvoiceNo"].astype(str).str.startswith("C")
    df["InvoiceDay"]  = df["InvoiceDate"].dt.date.astype(str)
    df["InvoiceMonth"]= df["InvoiceDate"].dt.to_period("M").astype(str)
    code = df["StockCode"].astype(str).str.upper().str.strip()
    df["IsService"] = code.isin(SERVICE_CODES)
    df["IsAnomaly"] = df["Quantity"] >= QTY_ANOMALY

    clean = df[(~df.IsCancelled) & (df.Quantity > 0) & (df.UnitPrice > 0)
               & (df.CustomerID.notna()) & (~df.IsService) & (~df.IsAnomaly)].copy()
    clean["CustomerID"] = clean.CustomerID.astype(int)

    con = sqlite3.connect(DB)
    df.to_sql("raw", con, if_exists="replace", index=False)
    clean.to_sql("sales", con, if_exists="replace", index=False)
    con.executescript("""
      CREATE INDEX IF NOT EXISTS ix_sales_cust  ON sales(CustomerID);
      CREATE INDEX IF NOT EXISTS ix_sales_month ON sales(InvoiceMonth);
      CREATE INDEX IF NOT EXISTS ix_sales_stock ON sales(StockCode);
    """)
    con.commit()
    drop_svc = int(df.IsService.sum()); drop_anom = int(df.IsAnomaly.sum())
    n_sale = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    rev    = con.execute("SELECT ROUND(SUM(Revenue),2) FROM sales").fetchone()[0]
    con.close()
    print(f"sales={n_sale:,}  revenue=£{rev:,.0f}  (excluded {drop_svc:,} service + {drop_anom} anomaly lines)  -> {DB}")

if __name__ == "__main__":
    main()
