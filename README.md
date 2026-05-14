# ⚡ FastOrder — Full-Stack Electronics E-Commerce Platform

A complete e-commerce web application built from scratch using **Python Flask**, **SQL Server (SSMS)**, and **HTML/CSS/JavaScript**. FastOrder is a fully functional electronics shop with an admin panel, customer storefront, and supply chain management — all connected to a real SQL Server database.

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web_Framework-black?logo=flask)
![SQL Server](https://img.shields.io/badge/SQL_Server-Express-red?logo=microsoftsqlserver&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-CSS3-orange?logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow?logo=javascript&logoColor=black)

---

## 🎬 Demo Video

https://github.com/YOUR_USERNAME/FastOrder/blob/main/FastOrder_Demo__3-in-1_E-Commerce_App.mp4

> *Full walkthrough of the Customer Shop, Admin Panel, and Supply Manager*

---

## 🎯 What This Project Does

FastOrder is a **3-in-1 web application** that simulates a real electronics e-commerce business:

1. **Customer Shop** — Browse, search, filter, and buy 96+ real-brand electronics products
2. **Admin Dashboard** — Manage all database tables, view analytics, export data
3. **Supply Manager** — Restock inventory, track revenue vs supply costs

---

## 🖥️ Live Pages

| Page | URL | Purpose |
|------|-----|---------|
| Admin Panel | `http://127.0.0.1:5000` | Database management + dashboard |
| Customer Shop | `http://127.0.0.1:5000/shop` | Customer-facing storefront |
| Supply Manager | `http://127.0.0.1:5000/supply` | Inventory restocking system |

---

## 🛍️ Customer Shop Features

### Product Catalog
- **96+ real-brand products** from Apple, Samsung, Dell, ASUS, Logitech, NVIDIA, AMD, Intel, Sony, Corsair, Razer, Bose, and more
- **Real product images** via Bing Image Search API — actual product photos on white backgrounds
- **13 product categories**: Laptop, Desktop, Monitor, Keyboard, Mouse, Phone, Tablet, GPU, CPU, Audio, Storage, Networking, Built PC
- **8 pre-built PC configurations** with full component breakdowns (Budget Starter ₹66,753 to AI Workstation ₹2,92,117)

### Search, Filter & Sort (Amazon/Flipkart Style)
- **Search bar** with live search across product names and specs
- **Filter sidebar** with:
  - Category filter (radio buttons)
  - Brand filter (multi-select checkboxes)
  - Price range presets (Under ₹8,350 / ₹8,350–₹41,750 / ₹41,750–₹83,500 / ₹83,500–₹1,67,000 / ₹1,67,000+)
  - Custom min/max price inputs in ₹
  - Customer rating filter (★★★★ & up, ★★★ & up, etc.)
  - Clear All button to reset filters
- **Active filter tags** showing applied filters with ✕ to remove individually
- **Sort options**: Featured, Price Low→High, Price High→Low, Avg. Reviews, Newest, Name A-Z, Name Z-A

### Product Detail Page
- Click any product to open a **side-by-side detail modal**
- Large product image + full specifications grid
- Star rating and review count
- Stock availability indicator
- Delivery estimate
- Add to Cart / Buy Now buttons
- **Built PCs** show full component breakdown (CPU, GPU, RAM, Storage, etc.)

### Customer Reviews
- **Star rating system** (1-5 stars)
- Written comments
- One review per customer per product
- Reviews display with author name and date

### Shopping Cart & Checkout
- Add to cart with quantity controls (+/−)
- Real-time cart total calculation
- **Stock validation** — can't buy more than available stock
- Checkout creates a real order in the database
- Random shipper assignment with estimated delivery date
- Order confirmation modal with shipping details

### Order History
- View all past orders with order number, date, and total
- Item breakdown per order
- Shipping company and estimated delivery date

### Stock/Inventory System
- **Green text**: "✓ In Stock (50)" — plenty available
- **Red text**: "⚠️ 4 left in stock! — order soon!" — 10 or fewer remaining
- **Disabled**: "❌ Out of Stock" — buttons greyed out, card faded, customers can't buy

### Multi-Language Support
- **4 languages**: English 🇬🇧, Hindi 🇮🇳, Tamil 🇮🇳, Spanish 🇪🇸
- Language dropdown in the header
- All UI text translates (buttons, labels, messages, filters)
- Language preference saved to browser — persists across sessions

### Currency
- All prices converted from **USD to INR** (₹) at 83.50 exchange rate
- Indian number formatting (₹1,67,000 not ₹167,000)
- Conversion applied across Shop, Admin Panel, and Supply Manager

### Authentication
- **Sign Up** with first name, last name, email, password
- **Log In** with email and password (SHA-256 hashed)
- **Remember Me** checkbox — stays logged in until explicit logout
- Auto-login on page load if Remember Me was used
- Login format: `FirstNameLastName@FastOrder.com` / `firstname123`

---

## 🗂️ Admin Panel Features

- **Interactive Dashboard** with:
  - Total customers, orders, products, suppliers, revenue stats
  - Top 5 customers by revenue
  - Top 5 products by quantity sold
  - Customers by country chart
  - Recent orders list
- **5 database tables** with full CRUD (Create, Read, Update, Delete):
  - Customers, Orders, Order Items, Products, Suppliers
- **Per-column search filters** on every table
- **Sortable columns** — click any header to sort ASC/DESC
- **Pagination** — 50 rows per page with navigation
- **CSV export** — download any table as a spreadsheet
- **3-dot menu** on each row for inline edit and delete
- All prices displayed in **₹ (INR)**

---

## 📦 Supply Manager Features

- **Product inventory table** showing all products with current stock levels
- **+/− quantity controls** and **+10 bulk button** for setting purchase quantity
- **Wholesale pricing** at 60% of retail (simulated supplier cost)
- **Live cost preview** — see total cost before confirming purchase
- **Balance system**: Revenue from customer orders − Supply costs = Available balance
- **Stock badges**: OK (green), Low (red), OUT (red)
- **Buy Stock button** — deducts from balance, increases product stock
- All prices in **₹ (INR)**

---

## 🗄️ Database Schema

Built on **SQL Server Express** with the following tables:

| Table | Purpose |
|-------|---------|
| `Customer` | Customer profiles (name, city, country, phone) |
| `[Order]` | Orders with date, number, customer ID, total |
| `OrderItem` | Line items linking orders to products |
| `Product` | Products with name, supplier, price, specs, stock |
| `Supplier` | Brand/supplier companies |
| `Accounts` | Login accounts (email, hashed password, linked to customer) |
| `Shippers` | Shipping companies with delivery times |
| `Cart` | Shopping cart items per account |
| `OrderShipping` | Shipping assignments with estimated delivery |
| `Reviews` | Product reviews with rating and comments |
| `SupplyOrders` | Supply purchase history with costs |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.14 + Flask |
| **Database** | Microsoft SQL Server Express (via SSMS) |
| **DB Connector** | pyodbc with ODBC Driver 17 |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6+) |
| **Fonts** | Google Fonts (Outfit + JetBrains Mono) |
| **Images** | Bing Image Search (live product photos) |
| **Auth** | SHA-256 password hashing |
| **Session** | localStorage for Remember Me + language preference |

---

## 📁 Project Structure

```
entry-manager/
├── app.py                      # Flask backend — all API routes
├── index.html                  # Admin panel (dashboard + tables)
├── customer.html               # Customer shop (storefront)
├── supply.html                 # Supply manager (inventory)
├── seed_techshop_products.py   # Product seeder script (96 products)
└── create_customer.py          # Auto-generates customer.html
```

---

## 🚀 How to Run

### Prerequisites
- Python 3.x installed
- SQL Server Express + SSMS installed
- ODBC Driver 17 for SQL Server

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/FastOrder.git
   cd FastOrder
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask flask-cors pyodbc
   ```

3. **Set up the database** — Open SSMS and run:
   ```sql
   ALTER TABLE master.dbo.Product ADD Stock INT DEFAULT 0
   UPDATE master.dbo.Product SET Stock = 50
   ALTER TABLE master.dbo.Product ALTER COLUMN Package NVARCHAR(MAX)
   ```

4. **Seed products** (first time only):
   ```bash
   python seed_techshop_products.py
   ```

5. **Start the server**
   ```bash
   python app.py
   ```

6. **Open in browser**
   - Admin: `http://127.0.0.1:5000`
   - Shop: `http://127.0.0.1:5000/shop`
   - Supply: `http://127.0.0.1:5000/supply`

---

## 📸 Screenshots

### Customer Shop
> Browse 96+ real electronics with filters, sort, and live search

### Product Detail
> Side-by-side layout with specs, reviews, stock status, and buy options

### Admin Dashboard
> Revenue stats, top customers, top products, recent orders

### Supply Manager
> Dark-themed inventory management with stock controls and balance tracking

---

## 🔑 Default Login

| Field | Value |
|-------|-------|
| Email | `FirstNameLastName@FastOrder.com` |
| Password | `firstname123` |
| Example | `PradyumnaSmith@FastOrder.com` / `pradyumna123` |

---

## 📝 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | Log in with email/password |
| POST | `/api/signup` | Create new account |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List products (with filters, sort, search) |
| GET | `/api/product/:id` | Product detail with reviews |
| GET | `/api/filter-options` | Get brands, categories, price range |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reviews/:productId` | Submit a review (1-5 stars + comment) |

### Cart & Checkout
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cart/:accountId` | Get cart items |
| POST | `/api/cart/:accountId` | Add item to cart |
| PUT | `/api/cart/:accountId/update/:cartId` | Update quantity |
| DELETE | `/api/cart/:accountId/item/:cartId` | Remove from cart |
| POST | `/api/checkout/:accountId` | Place order from cart |
| POST | `/api/buy-now/:accountId` | Instant purchase |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/my-orders/:accountId` | Order history with shipping |

### Supply Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/supply/products` | All products with stock + balance |
| POST | `/api/supply/buy` | Buy stock (deducts from revenue) |

### Admin CRUD
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/:table` | List records (paginated, filtered, sorted) |
| POST | `/:table` | Create new record |
| PUT | `/:table/:id` | Update record |
| DELETE | `/:table/:id` | Delete record |
| GET | `/:table/export` | Export as CSV |
| GET | `/stats` | Dashboard statistics |

---

## 🙏 Acknowledgments

- **Product data**: Real brand names and specifications from Apple, Samsung, Dell, ASUS, Logitech, NVIDIA, AMD, Intel, Sony, Corsair, Razer, Bose, and more
- **Product images**: Bing Image Search API for real product photographs
- **Fonts**: [Outfit](https://fonts.google.com/specimen/Outfit) and [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) from Google Fonts

---

## 📄 License

This project was built as a learning project for full-stack web development with Flask and SQL Server.

---

*Built with ❤️ using Python, Flask, SQL Server, and vanilla JavaScript*
