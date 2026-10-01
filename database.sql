CREATE DATABASE IF NOT EXISTS tourist_db;
USE tourist_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    role ENUM('user', 'admin') DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS packages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    package_name VARCHAR(100) NOT NULL,
    destination_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    days INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    package_id INT NOT NULL,
    travel_date DATE,
    num_people INT NOT NULL DEFAULT 1,
    total_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    payment_status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
    payment_method ENUM('UPI', 'Card', 'Cash') DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (package_id) REFERENCES packages(id)
);

INSERT INTO packages (package_name, destination_name, location, days, price, description) VALUES
('Beach Paradise', 'Goa', 'Western India', 5, 15000.00, 'Explore Goa''s stunning beaches, water sports, and local cuisine.'),
('Heritage Walk', 'Goa', 'Western India', 3, 8000.00, 'Discover Goa''s Portuguese architecture, churches, and old-world charm.'),
('Mountain Retreat', 'Manali', 'Himachal Pradesh', 7, 22000.00, 'Trek through Manali''s Himalayas, visit glaciers, and enjoy cold-weather adventures.'),
('Snow Escape', 'Manali', 'Himachal Pradesh', 4, 18000.00, 'Experience snowfall, skiing, and cozy mountain stays in Manali.'),
('Royal Tour', 'Jaipur', 'Rajasthan', 5, 16000.00, 'Visit Jaipur''s forts, palaces, and experience Rajasthani culture.'),
('Heritage Explorer', 'Jaipur', 'Rajasthan', 3, 10000.00, 'Walk through Jaipur''s historic bazaars, temples, and iconic landmarks.'),
('Backwater Bliss', 'Kerala', 'South India', 6, 20000.00, 'Cruise Kerala''s backwaters, enjoy ayurvedic massages, and nature.'),
('Wildlife and Tea', 'Kerala', 'South India', 5, 14000.00, 'Explore Kerala''s wildlife sanctuaries and tea plantations.');

-- Admin user setup:
-- To create an admin user, register a normal user first, then run this SQL:
-- UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';
-- Or insert directly with a hashed password (use generate_password_hash from werkzeug):
-- INSERT INTO users (name, email, password, phone, role) VALUES ('Admin', 'admin@example.com', 'hashed_password_here', '1234567890', 'admin');