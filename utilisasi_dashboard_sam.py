# import library
import streamlit  as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import time
warnings.filterwarnings('ignore')

# import library dari function.py
from generate import get_data_plan_utilisasi, get_data_summary

# Konfigurasi tampilan
st.set_page_config(layout='wide')
st.markdown("<h1 style='text-align: center;'>Dashboard Utilisasi</h1>", unsafe_allow_html=True)

# Input layout
col1, col2, col3, col4, col5 = st.columns([0.3, 0.2, 0.2, 0.3, 2])
with col1:
    date_input = st.date_input('Date', datetime.now(), format='DD/MM/YYYY')

with col2:
    start_time_input = st.time_input('Start Time', datetime.strptime("07:00", "%H:%M"))

with col3:
    end_time_input = st.time_input('End Time', datetime.now().time())

with col4:
    st.write('Realtime')
    real_time = st.checkbox('')

# Output area placeholder
output_placeholder = st.empty()

# Logika proses
if date_input:
    if not real_time:
        # Static mode
        data_plan = get_data_plan_utilisasi(date=date_input)
        summary_utilisasi = get_data_summary(date=date_input, startTime=start_time_input, endTime=end_time_input)
        output_placeholder.write(summary_utilisasi)
    else:
        # Real-time mode
        while True:
            end_time_input_now = datetime.now().strftime('%H:%M:%S')

            data_plan = get_data_plan_utilisasi(date=date_input)
            summary_utilisasi = get_data_summary(date=date_input,startTime=start_time_input,endTime=end_time_input_now)

            with output_placeholder.container():
                st.write(   '')
                st.markdown(f"**Terakhir update: {datetime.now().strftime('%H:%M:%S')}**")
                st.write(summary_utilisasi)

            time.sleep(5)