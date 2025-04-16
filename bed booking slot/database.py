import mysql.connector
from mysql.connector import Error

def init_database():
    try:
        # First connect without database to create it if not exists
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="qwert"
        )
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS covid_bed_booking")
        cursor.execute("USE covid_bed_booking")
        
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            hospital_id INT PRIMARY KEY AUTO_INCREMENT,
            hospital_name VARCHAR(100) NOT NULL,
            location VARCHAR(200) NOT NULL,
            contact_number VARCHAR(20),
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS beds (
            bed_id INT PRIMARY KEY AUTO_INCREMENT,
            hospital_id INT,
            bed_number VARCHAR(20) NOT NULL,
            bed_type ENUM('General', 'ICU', 'Ventilator') NOT NULL,
            status ENUM('Available', 'Occupied', 'Under Maintenance') DEFAULT 'Available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            age INT,
            gender ENUM('Male', 'Female', 'Other'),
            contact_number VARCHAR(20),
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INT PRIMARY KEY AUTO_INCREMENT,
            bed_id INT,
            patient_id INT,
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('Active', 'Completed', 'Cancelled') DEFAULT 'Active',
            FOREIGN KEY (bed_id) REFERENCES beds(bed_id),
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            hospital_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
        )""")
        
        connection.commit()
        print("Database and tables created successfully!")
        return True
    except Error as e:
        print(f"Error creating database: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_database_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="qwert",
            database="covid_bed_booking"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

# Hospital Operations
def add_hospital(name, location, contact, email):
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            sql = """INSERT INTO hospitals (hospital_name, location, contact_number, email)
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (name, location, contact, email))
            connection.commit()
            return True
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            connection.close()

def get_all_hospitals():
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM hospitals")
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            connection.close()

# Bed Operations
def add_bed(hospital_id, bed_number, bed_type):
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            sql = """INSERT INTO beds (hospital_id, bed_number, bed_type)
                     VALUES (%s, %s, %s)"""
            cursor.execute(sql, (hospital_id, bed_number, bed_type))
            connection.commit()
            return True
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            connection.close()

def get_available_beds(hospital_id=None):
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            if hospital_id:
                sql = """SELECT b.*, h.hospital_name 
                        FROM beds b 
                        JOIN hospitals h ON b.hospital_id = h.hospital_id 
                        WHERE b.status = 'Available' AND b.hospital_id = %s"""
                cursor.execute(sql, (hospital_id,))
            else:
                sql = """SELECT b.*, h.hospital_name 
                        FROM beds b 
                        JOIN hospitals h ON b.hospital_id = h.hospital_id 
                        WHERE b.status = 'Available'"""
                cursor.execute(sql)
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            connection.close()

# Patient Operations
def add_patient(name, age, gender, contact, email):
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            sql = """INSERT INTO patients (name, age, gender, contact_number, email)
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (name, age, gender, contact, email))
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            connection.close()

# Booking Operations
def create_booking(bed_id, patient_id):
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # Update bed status
            cursor.execute("UPDATE beds SET status = 'Occupied' WHERE bed_id = %s", (bed_id,))
            # Create booking
            sql = """INSERT INTO bookings (bed_id, patient_id)
                     VALUES (%s, %s)"""
            cursor.execute(sql, (bed_id, patient_id))
            connection.commit()
            return True
        except Error as e:
            print(f"Error: {e}")
            connection.rollback()
            return False
        finally:
            connection.close()

def cancel_booking(booking_id):
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # First get the bed_id from the booking
            cursor.execute("SELECT bed_id FROM bookings WHERE booking_id = %s", (booking_id,))
            result = cursor.fetchone()
            if result:
                bed_id = result[0]
                # Update booking status to Cancelled
                cursor.execute("""
                    UPDATE bookings 
                    SET status = 'Cancelled' 
                    WHERE booking_id = %s
                """, (booking_id,))
                # Update bed status back to Available
                cursor.execute("""
                    UPDATE beds 
                    SET status = 'Available' 
                    WHERE bed_id = %s
                """, (bed_id,))
                connection.commit()
                return True
            return False
        except Error as e:
            print(f"Error: {e}")
            connection.rollback()
            return False
        finally:
            connection.close()

def get_patient_bookings(patient_id):
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """SELECT b.*, h.hospital_name, bd.bed_number, bd.bed_type
                     FROM bookings b
                     JOIN beds bd ON b.bed_id = bd.bed_id
                     JOIN hospitals h ON bd.hospital_id = h.hospital_id
                     WHERE b.patient_id = %s AND b.status = 'Active'"""
            cursor.execute(sql, (patient_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            connection.close()

def get_hospital_beds(hospital_id):
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """SELECT * FROM beds WHERE hospital_id = %s ORDER BY bed_type, bed_number"""
            cursor.execute(sql, (hospital_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            connection.close() 