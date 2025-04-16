# Covid Bed Booking Slot System

A database-driven application for managing hospital bed bookings during the Covid-19 pandemic.

## Features

- User-friendly interface for booking hospital beds
- Hospital and bed availability management
- Patient booking system
- Admin interface for hospital management
- Basic reporting functionality

## Setup Instructions

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up MySQL Database:
   - Create a new database named 'covid_bed_booking'
   - Run the SQL commands from `database.sql` to create necessary tables

3. Configure environment variables:
   - Create a `.env` file with your MySQL credentials
   - Add the following variables:
     ```
     DB_HOST=localhost
     DB_USER=your_username
     DB_PASSWORD=your_password
     DB_NAME=covid_bed_booking
     ```

4. Run the application:
   ```
   streamlit run app.py
   ```

## Project Structure

- `app.py`: Main Streamlit application
- `database.py`: Database configuration and operations
- `database.sql`: SQL commands for database setup
- `.env`: Environment variables (not included in repository)
- `requirements.txt`: Project dependencies 
