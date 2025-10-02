FEWSHOTS = """
Q: show me all users
SQL: SELECT id, name, country FROM users LIMIT 200;

Q: top 5 skus by revenue
SQL: SELECT sku, SUM(price) as revenue FROM items GROUP BY sku ORDER BY revenue DESC LIMIT 5;

Q: orders over 100 dollars
SQL: SELECT id, user_id, total FROM orders WHERE total > 100 ORDER BY total DESC LIMIT 200;

Q: users from the US
SQL: SELECT id, name, country FROM users WHERE country = 'US' LIMIT 200;

Q: total revenue by country
SQL: SELECT u.country, SUM(o.total) as revenue FROM orders o JOIN users u ON o.user_id = u.id GROUP BY u.country ORDER BY revenue DESC LIMIT 200;
""".strip()