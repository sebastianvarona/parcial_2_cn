CREATE TABLE IF NOT EXISTS product (
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name varchar(255),
    price float,
    quantity int
);

INSERT INTO product (name, price, quantity) VALUES
    ('Laptop', 1200.00, 10),
    ('Mouse', 25.50, 50),
    ('Keyboard', 75.00, 30),
    ('Monitor', 300.00, 15),
    ('Headphones', 80.00, 20);
