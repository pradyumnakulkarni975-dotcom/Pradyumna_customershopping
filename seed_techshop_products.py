import json

import pyodbc

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=master;"
    "Trusted_Connection=yes;"
)

PRODUCTS = [
    ("Apple", "MacBook Air 13 M3", "Laptop", 1099, "13.6-inch Liquid Retina; Apple M3; 8GB unified memory; 256GB SSD; Integrated 10-core GPU; Up to 18 hours"),
    ("Apple", "MacBook Pro 14 M3 Pro", "Laptop", 1999, "14.2-inch Liquid Retina XDR; Apple M3 Pro; 18GB unified memory; 512GB SSD; 18-core GPU; Up to 18 hours"),
    ("Dell", "XPS 13 Plus", "Laptop", 1299, "13.4-inch OLED; Intel Core Ultra 7; 16GB LPDDR5x; 1TB SSD; Intel Arc graphics; 55Wh battery"),
    ("HP", "Spectre x360 14", "Laptop", 1249, "14-inch OLED touch; Intel Core Ultra 7; 16GB RAM; 1TB SSD; Intel Arc graphics; 68Wh battery"),
    ("Lenovo", "ThinkPad X1 Carbon Gen 12", "Laptop", 1699, "14-inch 2.8K OLED; Intel Core Ultra 7; 32GB RAM; 1TB SSD; Intel Arc graphics; 57Wh battery"),
    ("ASUS", "ROG Zephyrus G14", "Laptop", 1599, "14-inch OLED 120Hz; AMD Ryzen 9; 32GB RAM; 1TB SSD; NVIDIA RTX 4070; 73Wh battery"),
    ("MSI", "Stealth 16 AI Studio", "Laptop", 2199, "16-inch QHD+ 240Hz; Intel Core Ultra 9; 32GB RAM; 2TB SSD; NVIDIA RTX 4080; 99Wh battery"),
    ("Acer", "Swift Go 14 OLED", "Laptop", 849, "14-inch OLED; Intel Core Ultra 5; 16GB RAM; 512GB SSD; Intel Arc graphics; 65Wh battery"),
    ("Samsung", "Galaxy Book4 Pro", "Laptop", 1449, "14-inch AMOLED; Intel Core Ultra 7; 16GB RAM; 1TB SSD; Intel Arc graphics; 63Wh battery"),
    ("Microsoft", "Surface Laptop 6", "Laptop", 1199, "13.5-inch PixelSense; Intel Core Ultra 5; 16GB RAM; 512GB SSD; Intel graphics; Up to 18 hours"),
    ("Apple", "iMac 24 M3", "Desktop", 1299, "Apple M3; 10-core GPU; 8GB unified memory; 256GB SSD; Quiet thermal system; 143W adapter"),
    ("Dell", "Alienware Aurora R16", "Desktop", 2199, "Intel Core i9; NVIDIA RTX 4080; 32GB DDR5; 2TB SSD; Liquid cooling; 1000W PSU"),
    ("HP", "OMEN 45L Gaming Desktop", "Desktop", 2499, "Intel Core i9; NVIDIA RTX 4090; 64GB DDR5; 2TB SSD; Cryo chamber cooling; 1200W PSU"),
    ("Lenovo", "Legion Tower 7i", "Desktop", 1999, "Intel Core i7; NVIDIA RTX 4070 Ti; 32GB DDR5; 1TB SSD; Air cooling; 850W PSU"),
    ("ASUS", "ROG G22CH Compact", "Desktop", 1799, "Intel Core i7; NVIDIA RTX 4070; 32GB DDR5; 1TB SSD; Compact cooling; 600W PSU"),
    ("MSI", "Aegis RS 14th", "Desktop", 2299, "Intel Core i9; NVIDIA RTX 4080 Super; 32GB DDR5; 2TB SSD; Liquid cooling; 850W PSU"),
    ("Acer", "Predator Orion 5000", "Desktop", 1899, "Intel Core i7; NVIDIA RTX 4070; 32GB DDR5; 1TB SSD; Air cooling; 800W PSU"),
    ("Intel", "NUC 13 Pro Mini PC", "Desktop", 699, "Intel Core i7; Intel Iris Xe; 16GB DDR4; 512GB SSD; Silent fan; 120W adapter"),
    ("Apple", "Studio Display 27", "Monitor", 1599, "27 inch; 5K Retina; 60Hz; IPS; 600 nits; Thunderbolt 3"),
    ("Samsung", "Odyssey OLED G9", "Monitor", 1299, "49 inch; 5120 x 1440; 240Hz; OLED; HDR True Black; HDMI 2.1, DisplayPort"),
    ("LG", "UltraGear 27 OLED", "Monitor", 799, "27 inch; 2560 x 1440; 240Hz; OLED; HDR10; HDMI, DisplayPort"),
    ("Dell", "UltraSharp U2723QE", "Monitor", 579, "27 inch; 4K UHD; 60Hz; IPS Black; HDR400; USB-C hub"),
    ("ASUS", "ProArt Display PA279CRV", "Monitor", 469, "27 inch; 4K UHD; 60Hz; IPS; HDR10; USB-C, HDMI, DP"),
    ("Acer", "Nitro XV272U", "Monitor", 249, "27 inch; QHD; 180Hz; IPS; HDR10; HDMI, DP"),
    ("MSI", "MAG 274QRF QD", "Monitor", 349, "27 inch; QHD; 165Hz; Quantum Dot IPS; HDR Ready; HDMI, DP"),
    ("BenQ", "MOBIUZ EX3210U", "Monitor", 899, "32 inch; 4K UHD; 144Hz; IPS; HDR600; HDMI 2.1"),
    ("Logitech", "MX Keys S", "Keyboard", 109, "Scissor switches; Full size; Bluetooth/Logi Bolt; White backlight; Up to 10 days; Aluminum top case"),
    ("Apple", "Magic Keyboard Touch ID", "Keyboard", 149, "Scissor switches; Compact; Bluetooth; No backlight; Rechargeable; Aluminum"),
    ("Razer", "BlackWidow V4 Pro", "Keyboard", 229, "Mechanical green/yellow; Full size; USB-C; RGB; Wired; Aluminum plate"),
    ("Corsair", "K70 RGB Pro", "Keyboard", 159, "Cherry MX; Full size; USB-C; RGB; Wired; Aluminum frame"),
    ("Keychron", "Q1 Max", "Keyboard", 219, "Hot-swap mechanical; 75 percent; 2.4GHz/Bluetooth/USB; RGB; Rechargeable; CNC aluminum"),
    ("ASUS", "ROG Azoth", "Keyboard", 249, "ROG NX switches; 75 percent; Tri-mode; RGB; OLED battery display; Gasket mount"),
    ("SteelSeries", "Apex Pro TKL", "Keyboard", 189, "OmniPoint switches; TKL; USB-C; RGB; Wired; Aluminum"),
    ("Microsoft", "Designer Compact Keyboard", "Keyboard", 69, "Scissor switches; Compact; Bluetooth; No backlight; Coin cell; Low profile"),
    ("Logitech", "MX Master 3S", "Mouse", 99, "Darkfield sensor; 8000 DPI; Bluetooth/Logi Bolt; 141g; 7 buttons; 70 days"),
    ("Apple", "Magic Mouse", "Mouse", 79, "Multi-touch sensor; Adjustable; Bluetooth; 99g; Gesture surface; Rechargeable"),
    ("Razer", "DeathAdder V3 Pro", "Mouse", 149, "Focus Pro 30K; 30000 DPI; Wireless; 63g; 5 buttons; 90 hours"),
    ("Logitech", "G Pro X Superlight 2", "Mouse", 159, "HERO 2 sensor; 32000 DPI; Lightspeed wireless; 60g; 5 buttons; 95 hours"),
    ("Corsair", "Darkstar Wireless", "Mouse", 169, "Marksman sensor; 26000 DPI; Slipstream/Bluetooth; 96g; 15 buttons; 80 hours"),
    ("SteelSeries", "Aerox 5 Wireless", "Mouse", 119, "TrueMove Air; 18000 DPI; 2.4GHz/Bluetooth; 74g; 9 buttons; 180 hours"),
    ("ASUS", "ROG Harpe Ace Aim Lab", "Mouse", 129, "AimPoint sensor; 36000 DPI; Tri-mode; 54g; 5 buttons; 90 hours"),
    ("Microsoft", "Bluetooth Ergonomic Mouse", "Mouse", 49, "BlueTrack sensor; Adjustable; Bluetooth; 91g; 5 buttons; 15 months"),
    ("Apple", "iPhone 15 Pro Max", "Phone", 1199, "6.7-inch OLED; A17 Pro; 8GB RAM; 256GB; 48MP triple camera; 4441mAh"),
    ("Samsung", "Galaxy S24 Ultra", "Phone", 1299, "6.8-inch AMOLED; Snapdragon 8 Gen 3; 12GB RAM; 256GB; 200MP quad camera; 5000mAh"),
    ("Google", "Pixel 8 Pro", "Phone", 999, "6.7-inch OLED; Google Tensor G3; 12GB RAM; 128GB; 50MP triple camera; 5050mAh"),
    ("OnePlus", "12", "Phone", 799, "6.82-inch AMOLED; Snapdragon 8 Gen 3; 12GB RAM; 256GB; 50MP triple camera; 5400mAh"),
    ("Xiaomi", "14 Ultra", "Phone", 1099, "6.73-inch AMOLED; Snapdragon 8 Gen 3; 16GB RAM; 512GB; 50MP Leica quad camera; 5000mAh"),
    ("Samsung", "Galaxy Z Fold5", "Phone", 1799, "7.6-inch foldable AMOLED; Snapdragon 8 Gen 2; 12GB RAM; 256GB; 50MP triple camera; 4400mAh"),
    ("Apple", "iPad Pro 13 M4", "Tablet", 1299, "13-inch Ultra Retina XDR; Apple M4; 256GB; 12MP camera; All-day battery; Apple Pencil Pro"),
    ("Samsung", "Galaxy Tab S9 Ultra", "Tablet", 1199, "14.6-inch AMOLED; Snapdragon 8 Gen 2; 256GB; 13MP camera; 11200mAh; S Pen included"),
    ("Microsoft", "Surface Pro 10", "Tablet", 1199, "13-inch PixelSense; Intel Core Ultra 5; 256GB; Quad HD camera; Up to 19 hours; Surface Slim Pen"),
    ("Lenovo", "Tab Extreme", "Tablet", 949, "14.5-inch OLED; MediaTek Dimensity 9000; 256GB; 13MP camera; 12300mAh; Precision Pen"),
    ("NVIDIA", "GeForce RTX 4090 Founders Edition", "GPU", 1599, "24GB GDDR6X; 2.52GHz; 16384 CUDA cores; 3rd gen RT cores; 450W; HDMI, DisplayPort"),
    ("NVIDIA", "GeForce RTX 4080 Super", "GPU", 999, "16GB GDDR6X; 2.55GHz; 10240 CUDA cores; 3rd gen RT cores; 320W; HDMI, DisplayPort"),
    ("NVIDIA", "GeForce RTX 4070 Ti Super", "GPU", 799, "16GB GDDR6X; 2.61GHz; 8448 CUDA cores; 3rd gen RT cores; 285W; HDMI, DisplayPort"),
    ("AMD", "Radeon RX 7900 XTX", "GPU", 949, "24GB GDDR6; 2.5GHz; 6144 stream processors; Ray accelerators; 355W; HDMI, DisplayPort"),
    ("AMD", "Radeon RX 7800 XT", "GPU", 499, "16GB GDDR6; 2.43GHz; 3840 stream processors; Ray accelerators; 263W; HDMI, DisplayPort"),
    ("ASUS", "ROG Strix RTX 4070 OC", "GPU", 679, "12GB GDDR6X; OC mode; 5888 CUDA cores; 3rd gen RT cores; 200W; HDMI, DisplayPort"),
    ("MSI", "Gaming X Trio RTX 4060 Ti", "GPU", 399, "8GB GDDR6; Boost OC; 4352 CUDA cores; RT cores; 160W; HDMI, DisplayPort"),
    ("Intel", "Arc A770 Limited Edition", "GPU", 329, "16GB GDDR6; 2.1GHz; Xe cores; Ray tracing units; 225W; HDMI, DisplayPort"),
    ("Intel", "Core i9-14900K", "CPU", 589, "24 cores; 32 threads; 3.2GHz; 6.0GHz; LGA1700; 36MB cache"),
    ("Intel", "Core i7-14700K", "CPU", 409, "20 cores; 28 threads; 3.4GHz; 5.6GHz; LGA1700; 33MB cache"),
    ("Intel", "Core i5-14600K", "CPU", 319, "14 cores; 20 threads; 3.5GHz; 5.3GHz; LGA1700; 24MB cache"),
    ("AMD", "Ryzen 9 7950X3D", "CPU", 599, "16 cores; 32 threads; 4.2GHz; 5.7GHz; AM5; 144MB cache"),
    ("AMD", "Ryzen 7 7800X3D", "CPU", 379, "8 cores; 16 threads; 4.2GHz; 5.0GHz; AM5; 104MB cache"),
    ("AMD", "Ryzen 5 7600X", "CPU", 229, "6 cores; 12 threads; 4.7GHz; 5.3GHz; AM5; 38MB cache"),
    ("Apple", "M3 Max Developer Kit", "CPU", 999, "16-core CPU; 16 threads; Performance cores; Efficiency cores; Apple silicon; Unified cache"),
    ("Qualcomm", "Snapdragon X Elite Dev Kit", "CPU", 899, "12 cores; 12 threads; 3.8GHz; 4.3GHz; ARM; 42MB cache"),
    ("Sony", "WH-1000XM5", "Audio", 399, "30mm driver; Bluetooth; Active noise canceling; 30 hours; Beamforming mics; LDAC"),
    ("Apple", "AirPods Pro 2", "Audio", 249, "Custom driver; Bluetooth; Adaptive noise canceling; 30 hours with case; Dual beamforming mics; AAC"),
    ("Samsung", "Galaxy Buds2 Pro", "Audio", 229, "Two-way driver; Bluetooth; Active noise canceling; 29 hours with case; 3 mics; 24-bit audio"),
    ("Logitech", "G Pro X 2 Lightspeed", "Audio", 249, "50mm graphene driver; Lightspeed/Bluetooth; Passive isolation; 50 hours; Detachable boom; DTS Headphone:X"),
    ("Razer", "BlackShark V2 Pro", "Audio", 199, "50mm driver; 2.4GHz/Bluetooth; Passive isolation; 70 hours; HyperClear mic; THX spatial"),
    ("Corsair", "Virtuoso Pro", "Audio", 199, "50mm graphene driver; Wired; Open back; No battery; Broadcast mic; High-res audio"),
    ("Bose", "QuietComfort Ultra", "Audio", 429, "Custom driver; Bluetooth; Active noise canceling; 24 hours; Array mics; Immersive audio"),
    ("SteelSeries", "Arctis Nova Pro Wireless", "Audio", 349, "40mm driver; 2.4GHz/Bluetooth; Active noise canceling; Swappable batteries; ClearCast mic; 360 spatial"),
    ("Samsung", "990 Pro 2TB NVMe SSD", "Storage", 169, "2TB; PCIe 4.0 NVMe; 7450 MB/s; 6900 MB/s; 1200 TBW; 5 years"),
    ("Western Digital", "Black SN850X 2TB", "Storage", 149, "2TB; PCIe 4.0 NVMe; 7300 MB/s; 6600 MB/s; 1200 TBW; 5 years"),
    ("Crucial", "T700 4TB Gen5 SSD", "Storage", 439, "4TB; PCIe 5.0 NVMe; 12400 MB/s; 11800 MB/s; 2400 TBW; 5 years"),
    ("Seagate", "FireCuda 530 2TB", "Storage", 179, "2TB; PCIe 4.0 NVMe; 7300 MB/s; 6900 MB/s; 2550 TBW; 5 years"),
    ("Kingston", "KC3000 1TB", "Storage", 89, "1TB; PCIe 4.0 NVMe; 7000 MB/s; 6000 MB/s; 800 TBW; 5 years"),
    ("SanDisk", "Extreme Portable SSD 2TB", "Storage", 159, "2TB; USB-C; 1050 MB/s; 1000 MB/s; Rugged shell; 5 years"),
    ("Netgear", "Nighthawk RS700S WiFi 7 Router", "Networking", 699, "19Gbps; Tri-band; 10G WAN/LAN; 3500 sq ft; WPA3; App/cloud"),
    ("ASUS", "ROG Rapture GT-BE98 Pro", "Networking", 799, "25Gbps; Quad-band; 10G ports; Large homes; WPA3; Gaming dashboard"),
    ("TP-Link", "Archer BE800 WiFi 7 Router", "Networking", 599, "19Gbps; Tri-band; 10G ports; Large homes; WPA3; Tether app"),
    ("Google", "Nest WiFi Pro 3-Pack", "Networking", 399, "5.4Gbps; Tri-band; Gigabit ports; 6600 sq ft; WPA3; Google Home"),
    ("Eero", "Max 7 Mesh Router", "Networking", 599, "9.4Gbps; Tri-band; 10G ports; 2500 sq ft; WPA3; Eero app"),
    ("Ubiquiti", "UniFi Dream Machine Pro", "Networking", 379, "10Gbps routing; Dual WAN; 8 LAN ports; Business network; Firewall; UniFi controller"),
    ("TechCart", "Creator Pro Built PC", "Built PC", 1899, "AMD Ryzen 9 7900X; NVIDIA RTX 4070 Ti Super; 32GB DDR5; 2TB NVMe SSD; X670 WiFi board; 850W Gold PSU"),
    ("TechCart", "Esports Elite Built PC", "Built PC", 1299, "Intel Core i5-14600K; NVIDIA RTX 4060 Ti; 32GB DDR5; 1TB NVMe SSD; B760 WiFi board; 750W Bronze PSU"),
    ("TechCart", "4K Ultra Gaming Built PC", "Built PC", 2999, "Intel Core i9-14900K; NVIDIA RTX 4090; 64GB DDR5; 4TB NVMe SSD; Z790 WiFi board; 1200W Platinum PSU"),
    ("TechCart", "Budget Starter Built PC", "Built PC", 799, "AMD Ryzen 5 7600X; AMD Radeon RX 7600; 16GB DDR5; 1TB NVMe SSD; B650 board; 650W Bronze PSU"),
    ("TechCart", "Streaming Studio Built PC", "Built PC", 2199, "AMD Ryzen 7 7800X3D; NVIDIA RTX 4080 Super; 32GB DDR5; 2TB NVMe SSD; B650E WiFi board; 1000W Gold PSU"),
    ("TechCart", "Silent Office Built PC", "Built PC", 999, "Intel Core i7-14700; Intel Arc A770; 32GB DDR5; 1TB NVMe SSD; B760 board; 650W Gold PSU"),
    ("TechCart", "AI Workstation Built PC", "Built PC", 3499, "AMD Ryzen 9 7950X3D; NVIDIA RTX 4090; 128GB DDR5; 4TB NVMe SSD; X670E Creator board; 1200W Platinum PSU"),
    ("TechCart", "Compact Mini ITX Built PC", "Built PC", 1599, "Intel Core i7-14700K; NVIDIA RTX 4070; 32GB DDR5; 2TB NVMe SSD; Z790-I board; 750W SFX PSU"),
]


def scalar(cursor, sql, *params):
    cursor.execute(sql, params)
    row = cursor.fetchone()
    return row[0] if row else None


def main():
    conn = pyodbc.connect(CONNECTION_STRING)
    cursor = conn.cursor()
    supplier_ids = {}
    added_suppliers = 0
    added_products = 0

    for brand, _, _, _, _ in PRODUCTS:
        supplier_id = scalar(cursor, "SELECT Id FROM Supplier WHERE CompanyName = ?", brand)
        if supplier_id is None:
            cursor.execute(
                """
                INSERT INTO Supplier (CompanyName, ContactName, ContactTitle, City, Country, Phone, Fax)
                OUTPUT INSERTED.Id
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                brand,
                f"{brand} Sales",
                "Electronics Brand",
                "",
                "USA",
                "",
                "",
            )
            supplier_id = cursor.fetchone()[0]
            added_suppliers += 1
        supplier_ids[brand] = supplier_id

    for brand, model, category, price, specs in PRODUCTS:
        product_name = f"{brand} {model}"
        exists = scalar(cursor, "SELECT COUNT(*) FROM Product WHERE ProductName = ?", product_name)
        if exists:
            continue
        package = f"Brand: {brand}; Category: {category}; Specs: {specs}"
        cursor.execute(
            """
            INSERT INTO Product (ProductName, SupplierId, UnitPrice, Package, IsDiscontinued)
            VALUES (?, ?, ?, ?, 0)
            """,
            product_name,
            supplier_ids[brand],
            price,
            package,
        )
        added_products += 1

    conn.commit()
    total = scalar(cursor, "SELECT COUNT(*) FROM Product")
    conn.close()
    print(json.dumps({"added_suppliers": added_suppliers, "added_products": added_products, "total_products": total}))


if __name__ == "__main__":
    main()
