import streamlit as st
import sqlite3
import pandas as pd
from datetime import import date
import streamlit_authenticator as stauth

# 1. Setup User Credentials (You can change these passwords)
names = ['Elias Tarraf', 'Guest User']
usernames = ['elias', 'guest']
passwords = ['mma123', 'guest123'] # You should use hashed passwords for real apps

authenticator = stauth.Authenticate(names, usernames, passwords, 'training_cookie', 'auth_key', cookie_expiry_days=30)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.title(f"Welcome {name}'s Training Dashboard")

    # 2. Database connection with User Tracking
    conn = sqlite3.connect('training_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS gym_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, date TEXT, activity TEXT, duration INTEGER, intensity INTEGER)''')
    conn.commit()

    # 3. Sidebar for Logging (Now includes 'user' column)
    with st.sidebar:
        st.header("Log New Session")
        log_date = st.date_input("Date", date.today())
        activity = st.selectbox("Activity", ["MMA Sparring", "Heavy Lifting", "Cardio"])
        duration = st.number_input("Duration (mins)", min_value=1, value=60)
        intensity = st.slider("Intensity (RPE 1-10)", 1, 10, 5)
        
        if st.button("Save Session"):
            c.execute("INSERT INTO gym_logs (user, date, activity, duration, intensity) VALUES (?, ?, ?, ?, ?)",
                      (username, log_date, activity, duration, intensity))
            conn.commit()
            st.success("Saved!")

    # 4. Filtered Data Display
    df = pd.read_sql_query(f"SELECT * FROM gym_logs WHERE user = '{username}'", conn)
    if not df.empty:
        st.write("Your Training History")
        st.dataframe(df)
    else:
        st.info("No logs found. Start training!")

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
     

