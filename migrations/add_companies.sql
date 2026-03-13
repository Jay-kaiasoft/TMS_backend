-- Migration: Add companies table and manage company functionality
-- Run this after schema.sql

-- Create companies table
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    zip VARCHAR(20),
    logo VARCHAR(500),
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Add 'manage company' functionality
INSERT IGNORE INTO functionalities (name) VALUES ('manage company');

-- Add 'Companies List' module under 'manage company' functionality
INSERT IGNORE INTO modules (functionality_id, name)
SELECT id, 'Companies List' FROM functionalities WHERE name = 'manage company';

-- Add CRUD actions to the Companies List module
INSERT IGNORE INTO modules_actions (module_id, action_id)
SELECT m.id, a.id
FROM modules m
CROSS JOIN actions a
WHERE m.name = 'Companies List'
AND a.id IN (1, 2, 3, 4);
