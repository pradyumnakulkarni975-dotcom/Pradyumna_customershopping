from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import pyodbc
import os
import csv
import io
import hashlib
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "server":   "localhost\\SQLEXPRESS",
    "database": "master",
    "driver":   "{ODBC Driver 17 for SQL Server}"
}

TABLES = {
    "customers":  {"sql": "Customer",  "cols": ["Id","FirstName","LastName","City","Country","Phone"], "default_sort": "Id"},
    "orders":     {"sql": "[Order]",   "cols": ["Id","OrderDate","OrderNumber","CustomerId","TotalAmount"], "default_sort": "Id"},
    "orderitems": {"sql": "OrderItem", "cols": ["Id","OrderId","ProductId","UnitPrice","Quantity"], "default_sort": "Id"},
    "products":   {"sql": "Product",   "cols": ["Id","ProductName","SupplierId","UnitPrice","Package","IsDiscontinued"], "default_sort": "Id"},
    "suppliers":  {"sql": "Supplier",  "cols": ["Id","CompanyName","ContactName","ContactTitle","City","Country","Phone","Fax"], "default_sort": "Id"},
    "accounts":   {"sql": "Accounts",  "cols": ["Id","Email","FirstName","LastName","CustomerId","CreatedAt"], "default_sort": "Id"},
    "shippers":   {"sql": "Shippers",  "cols": ["Id","CompanyName","Phone","DeliveryDays"], "default_sort": "Id"},
}

def get_connection():
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def hash_pw(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Create Accounts table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Accounts' AND xtype='U')
            CREATE TABLE Accounts (
                Id INT IDENTITY(1,1) PRIMARY KEY, Email NVARCHAR(255) NOT NULL UNIQUE,
                Password NVARCHAR(255) NOT NULL, FirstName NVARCHAR(100) NOT NULL,
                LastName NVARCHAR(100) NOT NULL, CustomerId INT, CreatedAt DATETIME DEFAULT GETDATE()
            )""")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Shippers' AND xtype='U')
            CREATE TABLE Shippers (
                Id INT IDENTITY(1,1) PRIMARY KEY, CompanyName NVARCHAR(255) NOT NULL,
                Phone NVARCHAR(50), DeliveryDays INT DEFAULT 5
            )""")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Cart' AND xtype='U')
            CREATE TABLE Cart (
                Id INT IDENTITY(1,1) PRIMARY KEY, AccountId INT NOT NULL,
                ProductId INT NOT NULL, Quantity INT DEFAULT 1
            )""")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='OrderShipping' AND xtype='U')
            CREATE TABLE OrderShipping (
                Id INT IDENTITY(1,1) PRIMARY KEY, OrderId INT NOT NULL,
                ShipperId INT NOT NULL, EstimatedDelivery DATETIME, CreatedAt DATETIME DEFAULT GETDATE()
            )""")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Reviews' AND xtype='U')
            CREATE TABLE Reviews (
                Id INT IDENTITY(1,1) PRIMARY KEY, AccountId INT NOT NULL,
                ProductId INT NOT NULL, Rating INT NOT NULL,
                Comment NVARCHAR(MAX), CreatedAt DATETIME DEFAULT GETDATE()
            )""")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='SupplyOrders' AND xtype='U')
            CREATE TABLE SupplyOrders (
                Id INT IDENTITY(1,1) PRIMARY KEY, ProductId INT NOT NULL,
                Quantity INT NOT NULL, CostPerUnit DECIMAL(10,2) NOT NULL,
                TotalCost DECIMAL(10,2) NOT NULL, PurchasedAt DATETIME DEFAULT GETDATE()
            )""")
        conn.commit()

        # Seed Shippers if empty
        cursor.execute("SELECT COUNT(*) FROM Shippers")
        if cursor.fetchone()[0] == 0:
            for s in [
                ("QuickShip Express", "(555) 100-2000", 2),
                ("Standard Logistics", "(555) 200-3000", 5),
                ("Economy Delivery Co.", "(555) 300-4000", 10),
                ("Premium Same-Day", "(555) 400-5000", 1),
            ]:
                cursor.execute("INSERT INTO Shippers (CompanyName, Phone, DeliveryDays) VALUES (?, ?, ?)", *s)
            conn.commit()

        # Seed electronics suppliers if Supplier table is empty
        cursor.execute("SELECT COUNT(*) FROM Supplier")
        if cursor.fetchone()[0] == 0:
            suppliers = [
                ("NovaByte Computing", "James Chen", "Sales Director", "San Jose", "USA", "(408) 555-1001", "(408) 555-1002"),
                ("CloudPeak Systems", "Sarah Mitchell", "VP Sales", "Seattle", "USA", "(206) 555-2001", "(206) 555-2002"),
                ("PixelForge Displays", "Park Min-jun", "Account Manager", "Seoul", "South Korea", "+82-2-555-3001", "+82-2-555-3002"),
                ("SwiftGear Peripherals", "Lisa Hoffman", "Sales Lead", "Munich", "Germany", "+49-89-555-4001", "+49-89-555-4002"),
                ("VoltEdge Components", "Raj Patel", "Head of Sales", "Taipei", "Taiwan", "+886-2-555-5001", "+886-2-555-5002"),
                ("TitanCore Hardware", "Marco Rossi", "Director", "Milan", "Italy", "+39-02-555-6001", "+39-02-555-6002"),
                ("BrightWave Audio", "Yuki Tanaka", "Sales Manager", "Tokyo", "Japan", "+81-3-555-7001", "+81-3-555-7002"),
                ("NetVault Networking", "Emily Carter", "Account Exec", "Austin", "USA", "(512) 555-8001", "(512) 555-8002"),
            ]
            for s in suppliers:
                cursor.execute("INSERT INTO Supplier (CompanyName, ContactName, ContactTitle, City, Country, Phone, Fax) VALUES (?, ?, ?, ?, ?, ?, ?)", *s)
            conn.commit()
            print("   📦 Seeded 8 electronics suppliers.")

        # Seed electronics products if Product table is empty
        cursor.execute("SELECT COUNT(*) FROM Product")
        if cursor.fetchone()[0] == 0:
            products = [
                # (ProductName, SupplierId, UnitPrice, Package, IsDiscontinued)
                # ── LAPTOPS (Supplier 1: NovaByte) ──
                ("ProBook Ultra 14-inch Laptop", 1, 899.99, "1 unit — 14\" FHD, 16GB RAM, 512GB SSD", 0),
                ("GameStorm 15.6-inch Gaming Laptop", 1, 1499.99, "1 unit — RTX GPU, 32GB RAM, 1TB SSD", 0),
                ("AirSlim 13-inch Ultrabook", 1, 1099.99, "1 unit — 13.3\" OLED, 16GB RAM, 512GB SSD", 0),
                ("WorkStation X17 Laptop", 1, 2299.99, "1 unit — 17.3\" 4K, 64GB RAM, 2TB SSD", 0),
                ("StudentBook 15-inch Laptop", 1, 549.99, "1 unit — 15.6\" FHD, 8GB RAM, 256GB SSD", 0),
                ("CreatorPro 16-inch OLED Laptop", 1, 1899.99, "1 unit — 16\" OLED, 32GB RAM, 1TB SSD", 0),
                ("ChromeBook Essentials 14-inch", 1, 299.99, "1 unit — 14\" FHD, 4GB RAM, 64GB eMMC", 0),
                # ── DESKTOPS & WORKSTATIONS (Supplier 2: CloudPeak) ──
                ("TowerMax Gaming Desktop", 2, 1299.99, "1 unit — RTX GPU, 32GB RAM, 1TB SSD", 0),
                ("AI WorkStation Pro", 2, 3499.99, "1 unit — Dual GPU, 128GB RAM, 4TB NVMe", 0),
                ("MiniPC Compact Desktop", 2, 499.99, "1 unit — Small form, 16GB RAM, 512GB SSD", 0),
                ("OfficeDesk Standard PC", 2, 699.99, "1 unit — 16GB RAM, 512GB SSD, Wi-Fi 6", 0),
                ("RenderBeast Creator Desktop", 2, 2799.99, "1 unit — Pro GPU, 64GB RAM, 2TB NVMe", 0),
                ("BudgetBox Entry Desktop", 2, 399.99, "1 unit — 8GB RAM, 256GB SSD", 0),
                # ── MONITORS (Supplier 3: PixelForge) ──
                ("UltraWide 34-inch Curved Monitor", 3, 599.99, "1 unit — 34\" UWQHD 3440x1440, 144Hz", 0),
                ("4K ProDisplay 27-inch Monitor", 3, 449.99, "1 unit — 27\" 4K UHD, IPS, 99% sRGB", 0),
                ("Gaming Monitor 27-inch 165Hz", 3, 349.99, "1 unit — 27\" QHD, 165Hz, 1ms response", 0),
                ("Portable Monitor 15.6-inch USB-C", 3, 199.99, "1 unit — 15.6\" FHD, USB-C powered", 0),
                ("Studio Display 32-inch 4K", 3, 799.99, "1 unit — 32\" 4K, HDR600, USB-C hub", 0),
                ("Budget Monitor 24-inch FHD", 3, 149.99, "1 unit — 24\" 1080p, 75Hz, HDMI", 0),
                ("Dual Monitor 24-inch Pack", 3, 279.99, "2 units — 24\" FHD IPS, VESA mount", 0),
                # ── KEYBOARDS (Supplier 4: SwiftGear) ──
                ("Mechanical RGB Gaming Keyboard", 4, 129.99, "1 unit — Cherry MX switches, per-key RGB", 0),
                ("Wireless Compact Keyboard", 4, 79.99, "1 unit — 65% layout, Bluetooth + 2.4GHz", 0),
                ("Gaming Keyboard Pro TKL", 4, 169.99, "1 unit — Hot-swap, aluminum frame, RGB", 0),
                ("Ergonomic Split Keyboard", 4, 149.99, "1 unit — Split design, tented, wrist rest", 0),
                ("Budget Membrane Keyboard", 4, 29.99, "1 unit — Full-size, spill-resistant, USB", 0),
                ("75% Hot-Swap Mechanical Keyboard", 4, 99.99, "1 unit — Gasket mount, PBT keycaps", 0),
                ("Wireless Numpad", 4, 34.99, "1 unit — Bluetooth, 22 keys, rechargeable", 0),
                # ── MICE (Supplier 4: SwiftGear) ──
                ("Wireless Gaming Mouse", 4, 79.99, "1 unit — 25K DPI, 70hr battery, 58g", 0),
                ("Ergonomic Vertical Mouse", 4, 49.99, "1 unit — Vertical grip, 6 buttons, wireless", 0),
                ("Ultra-Light Pro Gaming Mouse", 4, 129.99, "1 unit — 49g, PAW3950 sensor, wireless", 0),
                ("Budget Wireless Mouse", 4, 19.99, "1 unit — 3 buttons, 1200 DPI, AA battery", 0),
                ("Trackball Mouse Pro", 4, 69.99, "1 unit — Thumb trackball, 8 buttons, wireless", 0),
                # ── PHONES & TABLETS (Supplier 1: NovaByte) ──
                ("SmartPhone Pro Max 256GB", 1, 1199.99, "1 unit — 6.7\" OLED, 256GB, 5G", 0),
                ("SmartPhone Lite 128GB", 1, 499.99, "1 unit — 6.1\" LCD, 128GB, 5G", 0),
                ("SmartPhone Ultra 512GB", 1, 899.99, "1 unit — 6.5\" AMOLED, 512GB, 5G", 0),
                ("Budget SmartPhone SE 64GB", 1, 299.99, "1 unit — 6.0\" LCD, 64GB, 4G", 0),
                ("TabPro 12.9-inch Tablet", 1, 799.99, "1 unit — 12.9\" 120Hz, 256GB, Wi-Fi+5G", 0),
                ("TabLite 10.5-inch Tablet", 1, 349.99, "1 unit — 10.5\" LCD, 64GB, Wi-Fi", 0),
                # ── GPUs (Supplier 5: VoltEdge) ──
                ("ProGraphics RTX 12GB GPU", 5, 699.99, "1 unit — 12GB GDDR6X, PCIe 4.0", 0),
                ("ProGraphics RTX 16GB GPU", 5, 999.99, "1 unit — 16GB GDDR6X, PCIe 5.0", 0),
                ("ProGraphics RTX 24GB GPU", 5, 1599.99, "1 unit — 24GB GDDR6X, PCIe 5.0", 0),
                ("Entry Graphics 8GB GPU", 5, 299.99, "1 unit — 8GB GDDR6, PCIe 4.0", 0),
                ("AI Accelerator 48GB GPU", 5, 2499.99, "1 unit — 48GB HBM3, AI/ML optimized", 0),
                # ── CPUs (Supplier 5: VoltEdge) ──
                ("Octa-Core Desktop Processor", 5, 329.99, "1 unit — 8 cores, 16 threads, 5.2GHz", 0),
                ("16-Core Pro Processor", 5, 549.99, "1 unit — 16 cores, 32 threads, 5.6GHz", 0),
                ("24-Core Elite Processor", 5, 799.99, "1 unit — 24 cores, 48 threads, 5.8GHz", 0),
                ("Budget Quad-Core Processor", 5, 149.99, "1 unit — 4 cores, 8 threads, 4.5GHz", 0),
                # ── RAM & STORAGE (Supplier 6: TitanCore) ──
                ("32GB DDR5 RAM Kit (2x16GB)", 6, 119.99, "1 kit — DDR5-6000, CL30, RGB", 0),
                ("16GB DDR5 RAM Kit (2x8GB)", 6, 69.99, "1 kit — DDR5-5600, CL36", 0),
                ("64GB DDR5 RAM Kit (2x32GB)", 6, 229.99, "1 kit — DDR5-6000, CL30, RGB", 0),
                ("1TB NVMe Gen4 SSD", 6, 89.99, "1 unit — 7000MB/s read, PCIe 4.0", 0),
                ("2TB NVMe Gen5 SSD", 6, 169.99, "1 unit — 12000MB/s read, PCIe 5.0", 0),
                ("4TB External HDD USB 3.0", 6, 99.99, "1 unit — Portable, USB 3.0, bus powered", 0),
                ("500GB Portable SSD USB-C", 6, 59.99, "1 unit — 1050MB/s, USB-C, pocket size", 0),
                # ── AUDIO (Supplier 7: BrightWave) ──
                ("Noise-Cancelling Headphones", 7, 299.99, "1 unit — ANC, 40hr battery, Bluetooth 5.3", 0),
                ("Gaming Headset 7.1 Surround", 7, 99.99, "1 unit — Virtual 7.1, detachable mic, RGB", 0),
                ("Wireless Earbuds Pro ANC", 7, 149.99, "1 pair — ANC, 30hr total battery, IPX5", 0),
                ("Studio Monitor Speakers (Pair)", 7, 249.99, "2 units — 5\" woofer, Bluetooth + aux", 0),
                ("Budget Wired Earbuds USB-C", 7, 24.99, "1 pair — Hi-Res audio, inline mic, USB-C", 0),
                ("Streaming Microphone USB", 7, 89.99, "1 unit — Condenser, cardioid, USB-C, mute", 0),
                ("Podcast Microphone Kit", 7, 159.99, "1 kit — XLR mic, boom arm, pop filter", 0),
                # ── NETWORKING (Supplier 8: NetVault) ──
                ("WiFi 7 Gaming Router", 8, 299.99, "1 unit — Tri-band, 10Gbps, 8 antennas", 0),
                ("Mesh WiFi System 3-Pack", 8, 249.99, "3 units — WiFi 6E, covers 6000 sq ft", 0),
                ("Gigabit Ethernet Switch 8-Port", 8, 49.99, "1 unit — 8 ports, metal housing, silent", 0),
                ("USB-C to Ethernet Adapter", 8, 19.99, "1 unit — 2.5Gbps, USB-C, plug and play", 0),
                # ── ACCESSORIES (Supplier 4: SwiftGear) ──
                ("USB-C Hub 7-in-1", 4, 49.99, "1 unit — HDMI, USB-A, SD, USB-C PD", 0),
                ("Webcam 4K HDR", 4, 129.99, "1 unit — 4K30fps, autofocus, privacy cover", 0),
                ("Desk Mat XXL (900x400mm)", 4, 34.99, "1 unit — Stitched edges, non-slip rubber", 0),
                ("Dual Monitor Arm Mount", 4, 79.99, "1 unit — Gas spring, VESA 75/100, clamp", 0),
                ("Laptop Stand Aluminum", 4, 44.99, "1 unit — Foldable, adjustable, ventilated", 0),
                ("Cable Management Kit", 4, 24.99, "1 kit — Clips, sleeves, ties, labels", 0),
                ("Wireless Charging Pad 15W", 4, 29.99, "1 unit — Qi2, 15W fast charge, LED ring", 0),
                ("Laptop Backpack 17-inch", 4, 59.99, "1 unit — Padded, USB port, water resistant", 0),
            ]
            for p in products:
                cursor.execute("INSERT INTO Product (ProductName, SupplierId, UnitPrice, Package, IsDiscontinued) VALUES (?, ?, ?, ?, ?)", *p)
            conn.commit()
            print(f"   🖥️  Seeded {len(products)} electronics products.")

        # Create accounts for ALL customers who don't have one yet
        cursor.execute("SELECT Id, FirstName, LastName FROM Customer")
        all_customers = cursor.fetchall()
        new_accounts = 0
        for cust in all_customers:
            cust_id = cust[0]
            fn = (cust[1] or "").strip()
            ln = (cust[2] or "").strip()
            if not fn or not ln: continue
            cursor.execute("SELECT COUNT(*) FROM Accounts WHERE CustomerId = ?", cust_id)
            if cursor.fetchone()[0] > 0: continue
            email_name = fn.replace(" ", "") + ln.replace(" ", "")
            email = f"{email_name}@FastOrder.com"
            cursor.execute("SELECT COUNT(*) FROM Accounts WHERE Email = ?", email)
            if cursor.fetchone()[0] > 0:
                email = f"{email_name}{cust_id}@FastOrder.com"
            password = fn.lower().replace(" ", "") + "123"
            cursor.execute("INSERT INTO Accounts (Email, Password, FirstName, LastName, CustomerId) VALUES (?, ?, ?, ?, ?)",
                email, hash_pw(password), fn, ln, cust_id)
            new_accounts += 1
        conn.commit()
        conn.close()

        print("✅ Database ready.")
        if new_accounts > 0:
            print(f"📧 Created {new_accounts} new customer accounts.")
        print("📧 Login: FirstNameLastName@FastOrder.com / firstname123")
    except Exception as e:
        print(f"⚠️  DB init warning: {e}")

# ─── HELPERS ───────────────────────────────────────────────
def build_where(args, columns):
    where_parts, params = [], []
    for c in columns:
        v = args.get(c, "").strip()
        if v:
            where_parts.append(f"CAST({c} AS NVARCHAR(MAX)) LIKE ?")
            params.append(f"%{v}%")
    where_sql = " WHERE " + " AND ".join(where_parts) if where_parts else ""
    return where_sql, params

def get_sort(args, columns, default):
    sort = args.get("sort", default)
    order = (args.get("order", "DESC") or "DESC").upper()
    if sort not in columns: sort = default
    if order not in ("ASC", "DESC"): order = "DESC"
    return sort, order

def get_paging(args):
    try: page = max(1, int(args.get("page", 1)))
    except: page = 1
    try: limit = min(500, max(1, int(args.get("limit", 50))))
    except: limit = 50
    return page, limit

def fetch_rows_and_total(tab, args, want_all=False):
    meta = TABLES[tab]
    cols = meta["cols"]
    where_sql, params = build_where(args, cols)
    sort_col, order = get_sort(args, cols, meta["default_sort"])
    conn = get_connection(); cursor = conn.cursor()
    count_sql = f"SELECT COUNT(*) FROM {meta['sql']}{where_sql}"
    cursor.execute(count_sql, *params) if params else cursor.execute(count_sql)
    total = cursor.fetchone()[0]
    col_list = ", ".join(cols)
    if want_all:
        sql = f"SELECT {col_list} FROM {meta['sql']}{where_sql} ORDER BY {sort_col} {order}"
        cursor.execute(sql, *params) if params else cursor.execute(sql)
    else:
        page, limit = get_paging(args)
        offset = (page - 1) * limit
        sql = (f"SELECT {col_list} FROM {meta['sql']}{where_sql}"
               f" ORDER BY {sort_col} {order} OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY")
        cursor.execute(sql, *params) if params else cursor.execute(sql)
    raw = cursor.fetchall(); conn.close()
    rows = [dict(zip(cols, row)) for row in raw]
    for r in rows:
        for k, v in list(r.items()):
            if hasattr(v, "isoformat"): r[k] = str(v)
            elif v is None: r[k] = ""
            else:
                try:
                    if hasattr(v, "as_tuple"): r[k] = float(v)
                except: pass
    return rows, total

# ─── PAGE SERVING ──────────────────────────────────────────
@app.route("/")
def serve_admin():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "index.html")

@app.route("/shop")
def serve_shop():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "customer.html")

# ─── GENERIC ADMIN LIST / EXPORT ───────────────────────────
@app.route("/<tab>", methods=["GET"])
def list_records(tab):
    if tab not in TABLES: return jsonify({"error": "Unknown table."}), 404
    try:
        rows, total = fetch_rows_and_total(tab, request.args)
        return jsonify({"rows": rows, "total": total})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route("/<tab>/export", methods=["GET"])
def export_csv(tab):
    if tab not in TABLES: return jsonify({"error": "Unknown table."}), 404
    try:
        rows, _ = fetch_rows_and_total(tab, request.args, want_all=True)
        cols = TABLES[tab]["cols"]
        buf = io.StringIO(); writer = csv.writer(buf)
        writer.writerow(cols)
        for r in rows: writer.writerow([r.get(c, "") for c in cols])
        return Response(buf.getvalue(), mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={tab}_export.csv"})
    except Exception as e: return jsonify({"error": str(e)}), 500

# ─── DASHBOARD STATS ───────────────────────────────────────
@app.route("/stats", methods=["GET"])
def stats():
    try:
        conn = get_connection(); cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Customer");   tc = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM [Order]");    to = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Product");    tp = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Supplier");   ts = cursor.fetchone()[0]
        cursor.execute("SELECT ISNULL(SUM(TotalAmount),0) FROM [Order]"); tr = float(cursor.fetchone()[0] or 0)
        cursor.execute("SELECT COUNT(*) FROM Product WHERE IsDiscontinued = 1"); td = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Accounts"); ta = cursor.fetchone()[0]
        cursor.execute("""SELECT TOP 5 c.Id, c.FirstName, c.LastName, COUNT(o.Id) AS OC, ISNULL(SUM(o.TotalAmount),0) AS Rev
            FROM Customer c LEFT JOIN [Order] o ON o.CustomerId = c.Id GROUP BY c.Id, c.FirstName, c.LastName ORDER BY Rev DESC""")
        top_cust = [{"Id":r[0],"Name":f"{r[1] or ''} {r[2] or ''}".strip(),"OrderCount":r[3],"Revenue":float(r[4] or 0)} for r in cursor.fetchall()]
        cursor.execute("""SELECT TOP 5 p.Id, p.ProductName, ISNULL(SUM(oi.Quantity),0) AS TQ
            FROM Product p LEFT JOIN OrderItem oi ON oi.ProductId = p.Id GROUP BY p.Id, p.ProductName ORDER BY TQ DESC""")
        top_prod = [{"Id":r[0],"Name":r[1] or "","Quantity":int(r[2] or 0)} for r in cursor.fetchall()]
        cursor.execute("""SELECT TOP 8 o.Id, o.OrderDate, o.OrderNumber, o.TotalAmount,
            c.FirstName+' '+c.LastName AS CN FROM [Order] o LEFT JOIN Customer c ON c.Id=o.CustomerId ORDER BY o.OrderDate DESC, o.Id DESC""")
        recent = [{"Id":r[0],"OrderDate":str(r[1]) if r[1] else "","OrderNumber":r[2] or "","TotalAmount":float(r[3] or 0),"CustomerName":r[4] or ""} for r in cursor.fetchall()]
        cursor.execute("SELECT TOP 6 ISNULL(Country,'') AS C, COUNT(*) AS N FROM Customer GROUP BY Country ORDER BY N DESC")
        by_country = [{"Country":r[0],"Count":r[1]} for r in cursor.fetchall()]
        conn.close()
        return jsonify({"totals":{"customers":tc,"orders":to,"products":tp,"suppliers":ts,"revenue":tr,"discontinued":td,"accounts":ta},
            "top_customers":top_cust,"top_products":top_prod,"recent_orders":recent,"customers_by_country":by_country})
    except Exception as e: return jsonify({"error": str(e)}), 500

# ─── ADMIN CRUD ────────────────────────────────────────────
@app.route("/customers", methods=["POST"])
def add_customer():
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT INTO Customer (FirstName,LastName,City,Country,Phone) OUTPUT INSERTED.Id VALUES (?,?,?,?,?)",
            d.get("FirstName",""),d.get("LastName",""),d.get("City",""),d.get("Country",""),d.get("Phone",""))
        nid = c.fetchone()[0]; conn.commit(); conn.close(); return jsonify({"Id":nid}), 201
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/customers/<int:cid>", methods=["PUT"])
def update_customer(cid):
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE Customer SET FirstName=?,LastName=?,City=?,Country=?,Phone=? WHERE Id=?",
            d.get("FirstName",""),d.get("LastName",""),d.get("City",""),d.get("Country",""),d.get("Phone",""),cid)
        conn.commit(); conn.close(); return jsonify({"message":"Updated."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/customers/<int:cid>", methods=["DELETE"])
def delete_customer(cid):
    try:
        conn = get_connection(); c = conn.cursor(); c.execute("DELETE FROM Customer WHERE Id=?",cid)
        conn.commit(); conn.close(); return jsonify({"message":"Deleted."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/orders", methods=["POST"])
def add_order():
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT INTO [Order] (OrderDate,OrderNumber,CustomerId,TotalAmount) OUTPUT INSERTED.Id VALUES (GETDATE(),?,?,?)",
            d.get("OrderNumber",""),d.get("CustomerId",0),d.get("TotalAmount",0))
        nid = c.fetchone()[0]; conn.commit(); conn.close(); return jsonify({"Id":nid}), 201
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/orders/<int:oid>", methods=["PUT"])
def update_order(oid):
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE [Order] SET OrderNumber=?,CustomerId=?,TotalAmount=? WHERE Id=?",
            d.get("OrderNumber",""),d.get("CustomerId",0),d.get("TotalAmount",0),oid)
        conn.commit(); conn.close(); return jsonify({"message":"Updated."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/orders/<int:oid>", methods=["DELETE"])
def delete_order(oid):
    try:
        conn = get_connection(); c = conn.cursor(); c.execute("DELETE FROM [Order] WHERE Id=?",oid)
        conn.commit(); conn.close(); return jsonify({"message":"Deleted."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/orderitems", methods=["POST"])
def add_orderitem():
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT INTO OrderItem (OrderId,ProductId,UnitPrice,Quantity) OUTPUT INSERTED.Id VALUES (?,?,?,?)",
            d.get("OrderId",0),d.get("ProductId",0),d.get("UnitPrice",0),d.get("Quantity",0))
        nid = c.fetchone()[0]; conn.commit(); conn.close(); return jsonify({"Id":nid}), 201
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/orderitems/<int:iid>", methods=["PUT"])
def update_orderitem(iid):
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE OrderItem SET OrderId=?,ProductId=?,UnitPrice=?,Quantity=? WHERE Id=?",
            d.get("OrderId",0),d.get("ProductId",0),d.get("UnitPrice",0),d.get("Quantity",0),iid)
        conn.commit(); conn.close(); return jsonify({"message":"Updated."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/orderitems/<int:iid>", methods=["DELETE"])
def delete_orderitem(iid):
    try:
        conn = get_connection(); c = conn.cursor(); c.execute("DELETE FROM OrderItem WHERE Id=?",iid)
        conn.commit(); conn.close(); return jsonify({"message":"Deleted."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/products", methods=["POST"])
def add_product():
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT INTO Product (ProductName,SupplierId,UnitPrice,Package,IsDiscontinued) OUTPUT INSERTED.Id VALUES (?,?,?,?,?)",
            d.get("ProductName",""),d.get("SupplierId",0),d.get("UnitPrice",0),d.get("Package",""),d.get("IsDiscontinued",0))
        nid = c.fetchone()[0]; conn.commit(); conn.close(); return jsonify({"Id":nid}), 201
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/products/<int:pid>", methods=["PUT"])
def update_product(pid):
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE Product SET ProductName=?,SupplierId=?,UnitPrice=?,Package=?,IsDiscontinued=? WHERE Id=?",
            d.get("ProductName",""),d.get("SupplierId",0),d.get("UnitPrice",0),d.get("Package",""),d.get("IsDiscontinued",0),pid)
        conn.commit(); conn.close(); return jsonify({"message":"Updated."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/products/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    try:
        conn = get_connection(); c = conn.cursor(); c.execute("DELETE FROM Product WHERE Id=?",pid)
        conn.commit(); conn.close(); return jsonify({"message":"Deleted."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/suppliers", methods=["POST"])
def add_supplier():
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT INTO Supplier (CompanyName,ContactName,ContactTitle,City,Country,Phone,Fax) OUTPUT INSERTED.Id VALUES (?,?,?,?,?,?,?)",
            d.get("CompanyName",""),d.get("ContactName",""),d.get("ContactTitle",""),d.get("City",""),d.get("Country",""),d.get("Phone",""),d.get("Fax",""))
        nid = c.fetchone()[0]; conn.commit(); conn.close(); return jsonify({"Id":nid}), 201
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/suppliers/<int:sid>", methods=["PUT"])
def update_supplier(sid):
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE Supplier SET CompanyName=?,ContactName=?,ContactTitle=?,City=?,Country=?,Phone=?,Fax=? WHERE Id=?",
            d.get("CompanyName",""),d.get("ContactName",""),d.get("ContactTitle",""),d.get("City",""),d.get("Country",""),d.get("Phone",""),d.get("Fax",""),sid)
        conn.commit(); conn.close(); return jsonify({"message":"Updated."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/suppliers/<int:sid>", methods=["DELETE"])
def delete_supplier(sid):
    try:
        conn = get_connection(); c = conn.cursor(); c.execute("DELETE FROM Supplier WHERE Id=?",sid)
        conn.commit(); conn.close(); return jsonify({"message":"Deleted."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/accounts/<int:aid>", methods=["DELETE"])
def delete_account(aid):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("DELETE FROM Cart WHERE AccountId=?",aid)
        c.execute("DELETE FROM Accounts WHERE Id=?",aid)
        conn.commit(); conn.close(); return jsonify({"message":"Deleted."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/shippers", methods=["POST"])
def add_shipper():
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT INTO Shippers (CompanyName,Phone,DeliveryDays) OUTPUT INSERTED.Id VALUES (?,?,?)",
            d.get("CompanyName",""),d.get("Phone",""),d.get("DeliveryDays",5))
        nid = c.fetchone()[0]; conn.commit(); conn.close(); return jsonify({"Id":nid}), 201
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/shippers/<int:sid>", methods=["PUT"])
def update_shipper(sid):
    d = request.get_json()
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE Shippers SET CompanyName=?,Phone=?,DeliveryDays=? WHERE Id=?",
            d.get("CompanyName",""),d.get("Phone",""),d.get("DeliveryDays",5),sid)
        conn.commit(); conn.close(); return jsonify({"message":"Updated."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/shippers/<int:sid>", methods=["DELETE"])
def delete_shipper(sid):
    try:
        conn = get_connection(); c = conn.cursor(); c.execute("DELETE FROM Shippers WHERE Id=?",sid)
        conn.commit(); conn.close(); return jsonify({"message":"Deleted."})
    except Exception as e: return jsonify({"error":str(e)}), 500

# ═══════════════════════════════════════════════════════════
# ═══ CUSTOMER SHOP API ════════════════════════════════════
# ═══════════════════════════════════════════════════════════

@app.route("/api/signup", methods=["POST"])
def signup():
    d = request.get_json()
    email = (d.get("email") or "").strip(); password = (d.get("password") or "").strip()
    fn = (d.get("firstName") or "").strip(); ln = (d.get("lastName") or "").strip()
    if not email or not password or not fn or not ln: return jsonify({"error":"All fields are required."}), 400
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM Accounts WHERE Email=?", email)
        if c.fetchone()[0] > 0: conn.close(); return jsonify({"error":"An account with this email already exists."}), 400
        c.execute("INSERT INTO Customer (FirstName,LastName,City,Country,Phone) OUTPUT INSERTED.Id VALUES (?,?,'','','')", fn, ln)
        cust_id = c.fetchone()[0]
        c.execute("INSERT INTO Accounts (Email,Password,FirstName,LastName,CustomerId) OUTPUT INSERTED.Id VALUES (?,?,?,?,?)",
            email, hash_pw(password), fn, ln, cust_id)
        acc_id = c.fetchone()[0]; conn.commit(); conn.close()
        return jsonify({"id":acc_id,"email":email,"firstName":fn,"lastName":ln,"customerId":cust_id}), 201
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/api/login", methods=["POST"])
def login():
    d = request.get_json()
    email = (d.get("email") or "").strip(); password = (d.get("password") or "").strip()
    if not email or not password: return jsonify({"error":"Email and password are required."}), 400
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT Id,Email,Password,FirstName,LastName,CustomerId FROM Accounts WHERE Email=?", email)
        row = c.fetchone(); conn.close()
        if not row: return jsonify({"error":"No account found with this email."}), 404
        if row[2] != hash_pw(password): return jsonify({"error":"Incorrect password."}), 401
        return jsonify({"id":row[0],"email":row[1],"firstName":row[3],"lastName":row[4],"customerId":row[5]})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/api/products", methods=["GET"])
def shop_products():
    search = request.args.get("search","").strip()
    brand = request.args.get("brand","").strip()
    category = request.args.get("category","").strip()
    min_price = request.args.get("minPrice","").strip()
    max_price = request.args.get("maxPrice","").strip()
    min_rating = request.args.get("minRating","").strip()
    sort = request.args.get("sort","featured").strip()
    try:
        conn = get_connection(); c = conn.cursor()
        where = ["p.IsDiscontinued=0"]; params = []
        if search: where.append("(p.ProductName LIKE ? OR p.Package LIKE ?)"); params += [f"%{search}%", f"%{search}%"]
        if brand:
            brands = brand.split(","); ph = ",".join(["?" for _ in brands])
            where.append(f"s.CompanyName IN ({ph})"); params += brands
        if category: where.append("p.Package LIKE ?"); params.append(f"%Category: {category}%")
        if min_price:
            try: where.append("p.UnitPrice >= ?"); params.append(float(min_price))
            except: pass
        if max_price:
            try: where.append("p.UnitPrice <= ?"); params.append(float(max_price))
            except: pass
        w = " WHERE " + " AND ".join(where)
        sort_map = {"featured":"p.ProductName ASC","price_asc":"p.UnitPrice ASC","price_desc":"p.UnitPrice DESC","newest":"p.Id DESC","name_asc":"p.ProductName ASC","name_desc":"p.ProductName DESC"}
        order = sort_map.get(sort, "p.ProductName ASC")
        sql = f"SELECT p.Id,p.ProductName,p.SupplierId,p.UnitPrice,p.Package,p.IsDiscontinued,s.CompanyName,ISNULL(p.Stock,0) FROM Product p LEFT JOIN Supplier s ON s.Id=p.SupplierId{w} ORDER BY {order}"
        c.execute(sql, *params) if params else c.execute(sql)
        rows = c.fetchall()
        c.execute("SELECT ProductId,AVG(CAST(Rating AS FLOAT)),COUNT(*) FROM Reviews GROUP BY ProductId")
        ratings = {r[0]:{"avg":round(r[1],1),"count":r[2]} for r in c.fetchall()}
        conn.close()
        result = []
        for r in rows:
            rat = ratings.get(r[0],{"avg":0,"count":0})
            cat = ""
            for part in (r[4] or "").split(";"): 
                pt = part.strip()
                if pt.startswith("Category:"): cat = pt.replace("Category:","").strip(); break
            result.append({"Id":r[0],"ProductName":r[1],"SupplierId":r[2],"UnitPrice":float(r[3] or 0),"Package":r[4] or "","IsDiscontinued":r[5],"Brand":r[6] or "","Stock":r[7],"Category":cat,"Rating":rat["avg"],"ReviewCount":rat["count"]})
        if min_rating:
            try: mr = float(min_rating); result = [p for p in result if p["Rating"] >= mr]
            except: pass
        if sort == "rating": result.sort(key=lambda x: x["Rating"], reverse=True)
        return jsonify(result)
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/api/filter-options", methods=["GET"])
def filter_options():
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT DISTINCT s.CompanyName FROM Product p JOIN Supplier s ON s.Id=p.SupplierId WHERE p.IsDiscontinued=0 ORDER BY s.CompanyName")
        brands = [r[0] for r in c.fetchall()]
        c.execute("SELECT Package FROM Product WHERE IsDiscontinued=0")
        cats = set()
        for r in c.fetchall():
            for part in (r[0] or "").split(";"):
                pt = part.strip()
                if pt.startswith("Category:"): cats.add(pt.replace("Category:","").strip())
        c.execute("SELECT MIN(UnitPrice),MAX(UnitPrice) FROM Product WHERE IsDiscontinued=0")
        pr = c.fetchone(); conn.close()
        return jsonify({"brands":brands,"categories":sorted(list(cats)),"priceRange":{"min":float(pr[0] or 0),"max":float(pr[1] or 0)}})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/api/product/<int:pid>", methods=["GET"])
def product_detail(pid):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT p.Id,p.ProductName,p.SupplierId,p.UnitPrice,p.Package,p.IsDiscontinued,s.CompanyName,ISNULL(p.Stock,0) FROM Product p LEFT JOIN Supplier s ON s.Id=p.SupplierId WHERE p.Id=?",pid)
        r = c.fetchone()
        if not r: conn.close(); return jsonify({"error":"Not found."}),404
        c.execute("SELECT r.Id,r.Rating,r.Comment,r.CreatedAt,a.FirstName,a.LastName FROM Reviews r JOIN Accounts a ON a.Id=r.AccountId WHERE r.ProductId=? ORDER BY r.CreatedAt DESC",pid)
        reviews = [{"Id":rv[0],"Rating":rv[1],"Comment":rv[2] or "","CreatedAt":str(rv[3]) if rv[3] else "","Author":f"{rv[4] or ''} {rv[5] or ''}".strip()} for rv in c.fetchall()]
        avg_rat = sum(rv["Rating"] for rv in reviews)/len(reviews) if reviews else 0
        conn.close()
        return jsonify({"Id":r[0],"ProductName":r[1],"SupplierId":r[2],"UnitPrice":float(r[3] or 0),"Package":r[4] or "","Brand":r[6] or "","Stock":r[7],"Rating":round(avg_rat,1),"ReviewCount":len(reviews),"Reviews":reviews})
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/reviews/<int:pid>", methods=["POST"])
def add_review(pid):
    d = request.get_json(); aid = d.get("accountId",0); rating = d.get("rating",5); comment = (d.get("comment") or "").strip()
    if rating<1 or rating>5: return jsonify({"error":"Rating 1-5."}),400
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM Reviews WHERE AccountId=? AND ProductId=?",aid,pid)
        if c.fetchone()[0]>0: conn.close(); return jsonify({"error":"Already reviewed."}),400
        c.execute("INSERT INTO Reviews(AccountId,ProductId,Rating,Comment) VALUES(?,?,?,?)",aid,pid,rating,comment)
        conn.commit(); conn.close(); return jsonify({"message":"Review added!"}),201
    except Exception as e: return jsonify({"error":str(e)}),500

# ── SUPPLY MANAGEMENT ────────────────────
@app.route("/supply")
def serve_supply():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "supply.html")

@app.route("/api/supply/products", methods=["GET"])
def supply_products():
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT p.Id,p.ProductName,p.UnitPrice,ISNULL(p.Stock,0),s.CompanyName FROM Product p LEFT JOIN Supplier s ON s.Id=p.SupplierId WHERE p.IsDiscontinued=0 ORDER BY p.ProductName")
        rows = c.fetchall()
        c.execute("SELECT ISNULL(SUM(TotalAmount),0) FROM [Order]")
        revenue = float(c.fetchone()[0] or 0)
        c.execute("SELECT ISNULL(SUM(TotalCost),0) FROM SupplyOrders")
        supply_cost = float(c.fetchone()[0] or 0)
        conn.close()
        return jsonify({"products":[{"Id":r[0],"ProductName":r[1],"UnitPrice":float(r[2] or 0),"Stock":r[3],"Brand":r[4] or ""} for r in rows],
            "revenue":revenue,"supplyCost":supply_cost,"balance":revenue-supply_cost})
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/supply/buy", methods=["POST"])
def supply_buy():
    d = request.get_json(); pid = d.get("productId",0); qty = d.get("quantity",0)
    if qty < 1: return jsonify({"error":"Quantity must be at least 1."}),400
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT UnitPrice,ProductName FROM Product WHERE Id=?",pid)
        prod = c.fetchone()
        if not prod: conn.close(); return jsonify({"error":"Product not found."}),404
        cost_per_unit = float(prod[0] or 0) * 0.6  # Buy at 60% of retail price (wholesale)
        total_cost = cost_per_unit * qty
        # Check if we have enough balance
        c.execute("SELECT ISNULL(SUM(TotalAmount),0) FROM [Order]")
        revenue = float(c.fetchone()[0] or 0)
        c.execute("SELECT ISNULL(SUM(TotalCost),0) FROM SupplyOrders")
        spent = float(c.fetchone()[0] or 0)
        balance = revenue - spent
        if total_cost > balance:
            conn.close(); return jsonify({"error":f"Not enough balance. You have ${balance:.2f} but need ${total_cost:.2f}"}),400
        # Record purchase
        c.execute("INSERT INTO SupplyOrders(ProductId,Quantity,CostPerUnit,TotalCost) VALUES(?,?,?,?)",pid,qty,cost_per_unit,total_cost)
        # Increase stock
        c.execute("UPDATE Product SET Stock=ISNULL(Stock,0)+? WHERE Id=?",qty,pid)
        conn.commit(); conn.close()
        return jsonify({"message":f"Bought {qty}x {prod[1]} for ${total_cost:.2f}","totalCost":total_cost,"newBalance":balance-total_cost})
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/cart/<int:aid>", methods=["GET"])
def get_cart(aid):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT c.Id,c.ProductId,c.Quantity,p.ProductName,p.UnitPrice FROM Cart c JOIN Product p ON p.Id=c.ProductId WHERE c.AccountId=?", aid)
        rows = c.fetchall(); conn.close()
        return jsonify([{"Id":r[0],"ProductId":r[1],"Quantity":r[2],"ProductName":r[3],"UnitPrice":float(r[4] or 0)} for r in rows])
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/api/cart/<int:aid>", methods=["POST"])
def add_to_cart(aid):
    d = request.get_json(); pid = d.get("productId",0); qty = d.get("quantity",1)
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT Id,Quantity FROM Cart WHERE AccountId=? AND ProductId=?", aid, pid)
        ex = c.fetchone()
        if ex: c.execute("UPDATE Cart SET Quantity=Quantity+? WHERE Id=?", qty, ex[0])
        else: c.execute("INSERT INTO Cart (AccountId,ProductId,Quantity) VALUES (?,?,?)", aid, pid, qty)
        conn.commit(); conn.close(); return jsonify({"message":"Added to cart."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/api/cart/<int:aid>/item/<int:cid>", methods=["DELETE"])
def remove_from_cart(aid, cid):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("DELETE FROM Cart WHERE Id=? AND AccountId=?", cid, aid)
        conn.commit(); conn.close(); return jsonify({"message":"Removed."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/api/cart/<int:aid>/update/<int:cid>", methods=["PUT"])
def update_cart_qty(aid, cid):
    d = request.get_json(); qty = max(1, d.get("quantity",1))
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("UPDATE Cart SET Quantity=? WHERE Id=? AND AccountId=?", qty, cid, aid)
        conn.commit(); conn.close(); return jsonify({"message":"Updated."})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/api/checkout/<int:aid>", methods=["POST"])
def checkout(aid):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT CustomerId FROM Accounts WHERE Id=?", aid)
        acc = c.fetchone()
        if not acc: return jsonify({"error":"Account not found."}), 404
        c.execute("SELECT c.ProductId,c.Quantity,p.UnitPrice,p.ProductName,ISNULL(p.Stock,0) FROM Cart c JOIN Product p ON p.Id=c.ProductId WHERE c.AccountId=?", aid)
        items = c.fetchall()
        if not items: conn.close(); return jsonify({"error":"Your cart is empty."}), 400
        # Check stock for all items
        for i in items:
            if i[4] < i[1]:
                conn.close(); return jsonify({"error":f"Not enough stock for {i[3]}. Only {i[4]} left."}), 400
        total = sum(r[1]*float(r[2] or 0) for r in items)
        order_num = f"ORD-{random.randint(100000,999999)}"
        c.execute("INSERT INTO [Order] (OrderDate,OrderNumber,CustomerId,TotalAmount) OUTPUT INSERTED.Id VALUES (GETDATE(),?,?,?)",
            order_num, acc[0], total)
        oid = c.fetchone()[0]
        for i in items:
            c.execute("INSERT INTO OrderItem (OrderId,ProductId,UnitPrice,Quantity) VALUES (?,?,?,?)", oid, i[0], float(i[2] or 0), i[1])
            c.execute("UPDATE Product SET Stock=Stock-? WHERE Id=?", i[1], i[0])
        c.execute("SELECT TOP 1 Id,CompanyName,DeliveryDays FROM Shippers ORDER BY NEWID()")
        sh = c.fetchone(); sname="Standard Shipping"; ddays=5
        if sh:
            ddays=sh[2]; sname=sh[1]
            c.execute("INSERT INTO OrderShipping (OrderId,ShipperId,EstimatedDelivery) VALUES (?,?,?)", oid, sh[0], datetime.now()+timedelta(days=ddays))
        c.execute("DELETE FROM Cart WHERE AccountId=?", aid)
        conn.commit(); conn.close()
        return jsonify({"orderId":oid,"orderNumber":order_num,"total":total,"itemCount":len(items),
            "shipper":sname,"estimatedDelivery":(datetime.now()+timedelta(days=ddays)).strftime("%B %d, %Y"),"deliveryDays":ddays})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/api/buy-now/<int:aid>", methods=["POST"])
def buy_now(aid):
    d = request.get_json(); pid = d.get("productId",0); qty = d.get("quantity",1)
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT CustomerId FROM Accounts WHERE Id=?", aid)
        acc = c.fetchone()
        if not acc: return jsonify({"error":"Account not found."}), 404
        c.execute("SELECT UnitPrice,ProductName,ISNULL(Stock,0) FROM Product WHERE Id=?", pid)
        prod = c.fetchone()
        if not prod: return jsonify({"error":"Product not found."}), 404
        if prod[2] < qty: conn.close(); return jsonify({"error":f"Not enough stock. Only {prod[2]} left."}), 400
        price = float(prod[0] or 0); total = price*qty
        onum = f"ORD-{random.randint(100000,999999)}"
        c.execute("INSERT INTO [Order] (OrderDate,OrderNumber,CustomerId,TotalAmount) OUTPUT INSERTED.Id VALUES (GETDATE(),?,?,?)", onum, acc[0], total)
        oid = c.fetchone()[0]
        c.execute("INSERT INTO OrderItem (OrderId,ProductId,UnitPrice,Quantity) VALUES (?,?,?,?)", oid, pid, price, qty)
        c.execute("UPDATE Product SET Stock=Stock-? WHERE Id=?", qty, pid)
        c.execute("SELECT TOP 1 Id,CompanyName,DeliveryDays FROM Shippers ORDER BY NEWID()")
        sh = c.fetchone(); sname="Standard Shipping"; ddays=5
        if sh:
            ddays=sh[2]; sname=sh[1]
            c.execute("INSERT INTO OrderShipping (OrderId,ShipperId,EstimatedDelivery) VALUES (?,?,?)", oid, sh[0], datetime.now()+timedelta(days=ddays))
        conn.commit(); conn.close()
        return jsonify({"orderId":oid,"orderNumber":onum,"total":total,"productName":prod[1],"quantity":qty,
            "shipper":sname,"estimatedDelivery":(datetime.now()+timedelta(days=ddays)).strftime("%B %d, %Y"),"deliveryDays":ddays})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/api/my-orders/<int:aid>", methods=["GET"])
def my_orders(aid):
    try:
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT CustomerId FROM Accounts WHERE Id=?", aid)
        acc = c.fetchone()
        if not acc: return jsonify({"error":"Account not found."}), 404
        c.execute("""SELECT o.Id,o.OrderDate,o.OrderNumber,o.TotalAmount,s.CompanyName,os.EstimatedDelivery
            FROM [Order] o LEFT JOIN OrderShipping os ON os.OrderId=o.Id LEFT JOIN Shippers s ON s.Id=os.ShipperId
            WHERE o.CustomerId=? ORDER BY o.OrderDate DESC, o.Id DESC""", acc[0])
        orders = []
        for r in c.fetchall():
            c2 = conn.cursor()
            c2.execute("SELECT oi.Quantity,oi.UnitPrice,p.ProductName FROM OrderItem oi JOIN Product p ON p.Id=oi.ProductId WHERE oi.OrderId=?", r[0])
            items = [{"Quantity":i[0],"UnitPrice":float(i[1] or 0),"ProductName":i[2]} for i in c2.fetchall()]
            est = ""
            if r[5]:
                try: est = r[5].strftime("%B %d, %Y")
                except: est = str(r[5])
            orders.append({"Id":r[0],"OrderDate":str(r[1]) if r[1] else "","OrderNumber":r[2] or "",
                "TotalAmount":float(r[3] or 0),"Shipper":r[4] or "","EstimatedDelivery":est,"Items":items})
        conn.close(); return jsonify(orders)
    except Exception as e: return jsonify({"error":str(e)}), 500

if __name__ == "__main__":
    init_db()
    print("🚀 Flask server running at http://localhost:5000")
    print("   Admin:  http://localhost:5000")
    print("   Shop:   http://localhost:5000/shop")
    app.run(debug=True, port=5000)
