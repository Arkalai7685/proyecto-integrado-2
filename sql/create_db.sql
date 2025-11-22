-- Script para crear la base de datos y tablas para ImpulsaMente
-- Ejecutar en MySQL (por ejemplo desde mysql CLI o Workbench)

-- 1) Crear base de datos
CREATE DATABASE IF NOT EXISTS mente_libre CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mente_libre;

-- 2) Tabla de servicios
CREATE TABLE IF NOT EXISTS services (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  slug VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3) Tabla de planes/precios
CREATE TABLE IF NOT EXISTS prices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  service_id INT NOT NULL,
  plan VARCHAR(80) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  currency VARCHAR(10) DEFAULT 'COP',
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- 4) Clientes
CREATE TABLE IF NOT EXISTS customers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  email VARCHAR(200) NOT NULL,
  phone VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5) Ordenes / solicitudes
CREATE TABLE IF NOT EXISTS orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  service_id INT NOT NULL,
  price_id INT NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (service_id) REFERENCES services(id),
  FOREIGN KEY (price_id) REFERENCES prices(id)
);

-- 6) Datos iniciales para Tutoría y Terapia
INSERT INTO services (name, slug, description) VALUES
('Tutoría', 'tutoria', 'Apoyo académico y acompañamiento en tesis y estudios'),
('Terapia', 'terapia', 'Atención psicológica individual y grupal');

-- Insertar planes asociados
INSERT INTO prices (service_id, plan, price, currency, description) VALUES
((SELECT id FROM services WHERE slug='tutoria'), 'basico', 15000.00, 'COP', 'Sesión única de 60 minutos'),
((SELECT id FROM services WHERE slug='tutoria'), 'estandar', 80000.00, 'COP', 'Paquete de 6 sesiones'),
((SELECT id FROM services WHERE slug='tutoria'), 'premium', 150000.00, 'COP', 'Paquete de 12 sesiones con recursos adicionales'),
((SELECT id FROM services WHERE slug='terapia'), 'individual', 30000.00, 'COP', 'Sesión individual de 60 minutos'),
((SELECT id FROM services WHERE slug='terapia'), '10sesiones', 280000.00, 'COP', 'Programa de 10 sesiones'),
((SELECT id FROM services WHERE slug='terapia'), 'familiar', 45000.00, 'COP', 'Sesión grupal / familiar');

-- Fin del script
