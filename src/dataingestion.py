import sqlite3
import pandas as pd
import random
import string
import os

# Create SQLite database
db_path = "c:/Users/jenichol/OneDrive - Capgemini/Documents/GitHub/ai_chatbot/ai_chatbot/src/db.sqlite3"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create tables
cur.executescript("""
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS payments;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    country TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price FLOAT,
    stock_quantity INTEGER
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    order_status TEXT,
    total_amount FLOAT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price_per_unit FLOAT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    payment_date TEXT,
    payment_method TEXT,
    amount_paid FLOAT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
""")

# Generate dummy data for Option A (small)
countries = ["UAE", "India", "UK", "USA", "Sri Lanka"]
statuses = ["Completed", "Pending", "Cancelled"]
methods = ["Card", "Cash", "Transfer"]

# --- Customers ---
customers = []
for i in range(1, 11):
    first = "Cust" + str(i)
    last = "User" + str(i)
    email = f"cust{i}@mail.com"
    phone = "050" + str(random.randint(1000000, 9999999))
    country = random.choice(countries)
    customers.append((i, first, last, email, phone, country))

cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?);", customers)

# --- Products ---
products = []
for i in range(1, 21):
    name = "Product " + str(i)
    category = random.choice(["Electronics", "Clothing", "Food"])
    price = round(random.uniform(10, 500), 2)
    stock = random.randint(5, 100)
    products.append((i, name, category, price, stock))

cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?);", products)

# --- Orders ---
orders = []
for i in range(1, 31):
    cust = random.randint(1, 10)
    date = f"2024-01-{random.randint(1, 28):02d}"
    status = random.choice(statuses)
    amount = round(random.uniform(50, 2000), 2)
    orders.append((i, cust, date, status, amount))

cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?);", orders)

# --- Order Items ---
order_items = []
item_id = 1
for order_id in range(1, 31):
    for _ in range(random.randint(1, 4)):
        product = random.randint(1, 20)
        qty = random.randint(1, 5)
        price = round(random.uniform(10, 500), 2)
        order_items.append((item_id, order_id, product, qty, price))
        item_id += 1

cur.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?);", order_items)

# --- Payments ---
payments = []
for i in range(1, 31):
    date = f"2024-02-{random.randint(1, 28):02d}"
    method = random.choice(methods)
    amt = round(random.uniform(50, 2000), 2)
    payments.append((i, i, date, method, amt))

cur.executemany("INSERT INTO payments VALUES (?, ?, ?, ?, ?);", payments)

conn.commit()
conn.close()

db_path
