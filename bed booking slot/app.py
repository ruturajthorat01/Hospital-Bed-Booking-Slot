import streamlit as st
import database as db
import pandas as pd
from datetime import datetime

# Initialize database
if 'db_initialized' not in st.session_state:
    if db.init_database():
        st.session_state.db_initialized = True
    else:
        st.error("Failed to initialize database. Please check your MySQL connection.")
        st.stop()

# Page configuration
st.set_page_config(
    page_title="Covid Bed Booking System",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# Main title
st.title("🏥 Covid Bed Booking System")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Book a Bed", "View Bookings", "Admin Login"])

# Home Page
if page == "Home":
    st.header("Welcome to Covid Bed Booking System")
    st.write("""
    This system helps you find and book hospital beds during the Covid-19 pandemic.
    
    Features:
    - Search for available beds
    - Book beds online
    - View your bookings
    - Hospital management interface
    """)
    
    # Display available beds
    st.subheader("Available Beds")
    available_beds = db.get_available_beds()
    if available_beds:
        df = pd.DataFrame(available_beds)
        st.dataframe(df[['hospital_name', 'bed_number', 'bed_type']])
    else:
        st.info("No beds available at the moment.")

# Book a Bed Page
elif page == "Book a Bed":
    st.header("Book a Hospital Bed")
    
    # Get available beds
    available_beds = db.get_available_beds()
    if not available_beds:
        st.warning("No beds available at the moment.")
    else:
        # Patient Information Form
        with st.form("booking_form"):
            st.subheader("Patient Information")
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=0, max_value=120)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            contact = st.text_input("Contact Number")
            email = st.text_input("Email")
            
            # Bed Selection
            st.subheader("Select Bed")
            bed_options = {f"{bed['hospital_name']} - {bed['bed_number']} ({bed['bed_type']})": bed['bed_id'] 
                         for bed in available_beds}
            selected_bed = st.selectbox("Available Beds", list(bed_options.keys()))
            
            submit_button = st.form_submit_button("Book Bed")
            if submit_button:
                if name and age and gender and contact and email:
                    # Add patient
                    patient_id = db.add_patient(name, age, gender, contact, email)
                    if patient_id:
                        # Create booking
                        bed_id = bed_options[selected_bed]
                        if db.create_booking(bed_id, patient_id):
                            st.success("Bed booked successfully!")
                        else:
                            st.error("Failed to book bed. Please try again.")
                    else:
                        st.error("Failed to register patient. Please try again.")
                else:
                    st.warning("Please fill in all fields.")

# View Bookings Page
elif page == "View Bookings":
    st.header("View Your Bookings")
    
    # Search by patient information
    email = st.text_input("Enter your email to view bookings")
    
    if email:
        # In a real application, you would first get the patient_id from email
        # For this example, we'll assume we have the patient_id
        bookings = db.get_patient_bookings(1)  # Replace 1 with actual patient_id
        if bookings:
            df = pd.DataFrame(bookings)
            st.write("Your Active Bookings:")
            st.dataframe(df[['hospital_name', 'bed_number', 'bed_type', 'booking_date']])
            
            # Add cancel booking functionality
            st.write("### Cancel Booking")
            booking_options = {f"{b['hospital_name']} - {b['bed_number']} ({b['bed_type']})": b['booking_id'] 
                             for b in bookings}
            selected_booking = st.selectbox("Select booking to cancel", list(booking_options.keys()))
            
            if st.button("Cancel Selected Booking"):
                booking_id = booking_options[selected_booking]
                if db.cancel_booking(booking_id):
                    st.success("Booking cancelled successfully!")
                    st.rerun()  # Refresh the page to show updated bookings
                else:
                    st.error("Failed to cancel booking. Please try again.")
        else:
            st.info("No active bookings found for this email.")
    else:
        st.warning("Please enter your email.")

# Admin Login Page
elif page == "Admin Login":
    st.header("Admin Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        submit_button = st.form_submit_button("Login")
        if submit_button:
            # In a real application, you would verify credentials against the database
            if username == "admin" and password == "admin":  # Replace with actual authentication
                st.session_state.logged_in = True
                st.session_state.user_type = "admin"
                st.success("Logged in successfully!")
            else:
                st.error("Invalid credentials!")
    
    if st.session_state.logged_in:
        st.subheader("Admin Dashboard")
        
        # Add Hospital Form
        with st.form("add_hospital_form"):
            st.write("Add New Hospital")
            hospital_name = st.text_input("Hospital Name")
            location = st.text_input("Location")
            contact = st.text_input("Contact Number")
            email = st.text_input("Email")
            
            submit_button = st.form_submit_button("Add Hospital")
            if submit_button:
                if hospital_name and location:
                    if db.add_hospital(hospital_name, location, contact, email):
                        st.success("Hospital added successfully!")
                    else:
                        st.error("Failed to add hospital.")
                else:
                    st.warning("Please fill in required fields.")
        
        # Add Bed Form
        with st.form("add_bed_form"):
            st.write("Add New Beds")
            hospitals = db.get_all_hospitals()
            if hospitals:
                hospital_options = {h['hospital_name']: h['hospital_id'] for h in hospitals}
                selected_hospital = st.selectbox("Select Hospital", list(hospital_options.keys()))
                
                # Create columns for bed type and count
                col1, col2 = st.columns(2)
                
                with col1:
                    bed_type = st.selectbox("Bed Type", ["General", "ICU", "Ventilator"])
                with col2:
                    bed_count = st.number_input("Number of Beds", min_value=1, max_value=100, value=1)
                
                submit_button = st.form_submit_button("Add Beds")
                if submit_button:
                    if bed_count > 0:
                        hospital_id = hospital_options[selected_hospital]
                        success_count = 0
                        for i in range(bed_count):
                            bed_number = f"{bed_type}-{i+1}"  # Generate bed numbers like "General-1", "ICU-1", etc.
                            if db.add_bed(hospital_id, bed_number, bed_type):
                                success_count += 1
                        
                        if success_count == bed_count:
                            st.success(f"Successfully added {success_count} {bed_type} bed(s)!")
                        else:
                            st.warning(f"Added {success_count} out of {bed_count} beds. Some beds may not have been added.")
                    else:
                        st.warning("Please enter a valid number of beds.")
            else:
                st.info("Please add a hospital first before adding beds.")
        
        # View All Hospitals and Their Beds
        st.subheader("Hospital Bed Status")
        hospitals = db.get_all_hospitals()
        if hospitals:
            for hospital in hospitals:
                st.write(f"### {hospital['hospital_name']}")
                beds = db.get_hospital_beds(hospital['hospital_id'])
                if beds:
                    df = pd.DataFrame(beds)
                    # Group beds by type and count
                    bed_counts = df.groupby('bed_type').size().reset_index(name='count')
                    st.write("Bed Distribution:")
                    st.dataframe(bed_counts)
                    st.write("Detailed Bed List:")
                    st.dataframe(df[['bed_number', 'bed_type', 'status']])
                else:
                    st.info("No beds added yet.")
        else:
            st.info("No hospitals registered yet.") 