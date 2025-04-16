-- Create database
CREATE DATABASE IF NOT EXISTS covid_bed_booking;
USE covid_bed_booking;

-- Create hospitals table
CREATE TABLE IF NOT EXISTS hospitals (
    hospital_id INT PRIMARY KEY AUTO_INCREMENT,
    hospital_name VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    contact_number VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create beds table
CREATE TABLE IF NOT EXISTS beds (
    bed_id INT PRIMARY KEY AUTO_INCREMENT,
    hospital_id INT,
    bed_number VARCHAR(20) NOT NULL,
    bed_type ENUM('General', 'ICU', 'Ventilator') NOT NULL,
    status ENUM('Available', 'Occupied', 'Under Maintenance') DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
);

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender ENUM('Male', 'Female', 'Other'),
    contact_number VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create bookings table
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    bed_id INT,
    patient_id INT,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Active', 'Completed', 'Cancelled') DEFAULT 'Active',
    FOREIGN KEY (bed_id) REFERENCES beds(bed_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- Create admin table
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    hospital_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
); 