CREATE TABLE IF NOT EXISTS orders (
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_name varchar(255),
    user_email varchar(255),
    total float,
    status varchar(50),
    created_at datetime
);

CREATE TABLE IF NOT EXISTS order_items (
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    order_id int NOT NULL,
    product_id int NOT NULL,
    product_name varchar(255) NOT NULL,
    quantity int NOT NULL,
    unit_price float NOT NULL,
    subtotal float NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
