-- Example queries used in Text2SQLAI

-- Demo: List all customers from USA
SELECT * FROM customers WHERE country = 'USA';

-- Demo: Get top product sales
SELECT product_name, SUM(quantity) FROM order_items GROUP BY product_id ORDER BY SUM(quantity) DESC LIMIT 10;

-- Demo: Create sample table
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  amount DECIMAL,
  created_at DATETIME
);
