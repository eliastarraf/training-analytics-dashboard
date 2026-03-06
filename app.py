import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

st.set_page_config(page_title="Elias's Training Dashboard", layout="wide")
st.title("🏋️‍♂️ Training Analytics Dashboard")

# 1. This creates a database file right in your folder
def get_db_connection():
    conn = sqlite3.connect('training_data.db', check_same_thread=False)
    return conn

# 2. Setup the table (Runs every time, but only creates it once)
conn = get_db_connection()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS gym_logs 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              date TEXT, 
              activity_type TEXT, 
              duration_mins INTEGER, 
              intensity_rpe INTEGER, 
              notes TEXT)''')
conn.commit()

# --- SIDEBAR: LOG DATA ---
st.sidebar.header("Log New Session")
with st.sidebar.form("workout_form", clear_on_submit=True):
    input_date = st.date_input("Date", date.today())
    input_type = st.selectbox("Activity", ["MMA Sparring", "Bodybuilding", "Powerlifting", "Cardio"])
    input_duration = st.number_input("Duration (mins)", min_value=1, value=60)
    input_rpe = st.slider("Intensity (RPE 1-10)", 1, 10, 7)
    input_notes = st.text_area("Notes")
    submit = st.form_submit_button("Save Session")

if submit:
    c.execute("INSERT INTO gym_logs (date, activity_type, duration_mins, intensity_rpe, notes) VALUES (?, ?, ?, ?, ?)",
              (str(input_date), input_type, input_duration, input_rpe, input_notes))
    conn.commit()
    st.sidebar.success("Session saved!")
    st.rerun()

# --- MAIN DISPLAY ---
df = pd.read_sql("SELECT * FROM gym_logs ORDER BY date DESC", conn)

if not df.empty:
    col1, col2 = st.columns(2)
    col1.metric("Total Sessions", len(df))
    col2.metric("Avg Intensity", round(df['intensity_rpe'].mean(), 1))

    st.subheader("Training Intensity Over Time")
    chart_df = df.sort_values('date')
    st.line_chart(chart_df.set_index('date')['intensity_rpe'])
    
    st.subheader("Raw History")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Log your first session in the sidebar to see your charts!")
