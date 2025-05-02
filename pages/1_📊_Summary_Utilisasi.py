# import library
import streamlit  as st
import altair as alt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import time as time_2
import warnings
warnings.filterwarnings('ignore')

# import library dari function.py
from generate import get_data_plan_utilisasi, get_data_gps, get_data_validasi_ws, integrate_data
from functions import TransformVisualData

# Konfigurasi tampilan
st.set_page_config(layout='wide', page_title='SAM Dashboard Utilisasi')
st.markdown("<h1 style='text-align: center;'>Dashboard Utilisasi</h1>", unsafe_allow_html=True)
st.write('')
st.write('')

# Inisialisasi hanya saat pertama kali  
if "date_input" not in st.session_state:
    st.session_state["date_input"] = datetime.today().date()

if "start_time_input" not in st.session_state:
    st.session_state["start_time_input"] = time(7, 0)  # jam 07:00

if "end_time_input" not in st.session_state:
    st.session_state["end_time_input"] = time(17, 0)  # jam 17:00

if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame({})

# Input layout
col1, col2, col3, col4, col5 = st.columns([0.4, 0.4, 0.4, 0.3, 2])
with col1:
    date_input = st.date_input("Tanggal", value=st.session_state["date_input"], format='DD/MM/YYYY')
    st.session_state['date_input'] = date_input

with col2:
    start_time_input = st.time_input("Start Time", value=st.session_state["start_time_input"])
    st.session_state["start_time_input"] = start_time_input

with col3:
    end_time_input = st.time_input("End Time", value=st.session_state["end_time_input"])
    st.session_state["end_time_input"] = end_time_input

with col4:
    st.write('Realtime')
    real_time = st.checkbox('')

# Output area placeholder
output_placeholder = st.empty()

# Logika proses
if date_input:
    if not real_time:
        # Static mode
        # Get data
        data = integrate_data(date=date_input, startTime=start_time_input, endTime=end_time_input)
        st.session_state['data'] = data

        # RENTAL BDM
        rental_bdm_fo = TransformVisualData.transform_fiz_1(data, 'Rental BDM', 'FO')
        rental_bdm_to = TransformVisualData.transform_fiz_1(data, 'Rental BDM', 'TO')

        # RENTAL NMS
        rental_nms_fo = TransformVisualData.transform_fiz_1(data, 'Rental NMS', 'FO')
        rental_nms_to = TransformVisualData.transform_fiz_1(data, 'Rental NMS', 'TO')

        # RENTAL PEMBATUAN
        rental_kbm = TransformVisualData.transform_fiz_1(data, 'Rental KBM', 'Pembatuan KBM')
        rental_mkg = TransformVisualData.transform_fiz_1(data, 'Rental MKG', 'Rental MKG')

        # KONTRAK BDM
        mining_bdm_to = TransformVisualData.transform_fiz_1(data, 'Mining BDM', 'TO')

        # TIDAK ADA PROJECT
        no_project = TransformVisualData.transform_fiz_1(data, 'Tidak Ada Job', 'Tidak Ada Job')

        # RENTAL KBM
        mining_kbm_fo = TransformVisualData.transform_fiz_1(data, 'Mining KBM', 'FO')
        mining_kbm_to = TransformVisualData.transform_fiz_1(data, 'Mining KBM', 'TO')


        # Show data
        with output_placeholder.container():
            r1c0, r1c1, r1c2, r1c3, r1c4, r1c5, r1c6 = st.columns([0.05, 0.5, 0.5, 0.1, 0.5, 0.5, 0.05], gap='small')

            with r1c1:
                # Mining KBM (FO)
                st.markdown("<h4 style='text-align: left;'>Mining KBM (FO)</h4>", unsafe_allow_html=True)
                st.altair_chart(mining_kbm_fo, use_container_width=True)

                # Rental BDM (FO)
                st.markdown("<h4 style='text-align: left;'>Rental BDM (FO)</h4>", unsafe_allow_html=True)
                st.altair_chart(rental_bdm_fo, use_container_width=True)

                # Pembatuan KBM
                st.markdown("<h4 style='text-align: left;'>Pembatuan KBM</h4>", unsafe_allow_html=True)
                st.altair_chart(rental_kbm, use_container_width=True)

                # Mining BDM (TO)
                st.markdown("<h4 style='text-align: left;'>Mining BDM (TO)</h4>", unsafe_allow_html=True)
                st.altair_chart(mining_bdm_to, use_container_width=True)

                # Rental NMS (FO)
                st.markdown("<h4 style='text-align: left;'>Rental NMS (FO)</h4>", unsafe_allow_html=True)
                st.altair_chart(rental_nms_fo, use_container_width=True)
            
            with r1c4:
                # Mining KBM (TO)
                st.markdown("<h4 style='text-align: left;'>Mining KBM (TO)</h4>", unsafe_allow_html=True)
                st.altair_chart(mining_kbm_to, use_container_width=True)

                # Rental BDM (TO)
                st.markdown("<h4 style='text-align: left;'>Rental BDM (TO)</h4>", unsafe_allow_html=True)
                st.altair_chart(rental_bdm_to, use_container_width=True)

                # Pembatuan MKG
                st.markdown("<h4 style='text-align: left;'>Pembatuan MKG</h4>", unsafe_allow_html=True)
                st.altair_chart(rental_mkg, use_container_width=True)

                # Tidak Ada Job
                st.markdown("<h4 style='text-align: left;'>Tidak Ada Job</h4>", unsafe_allow_html=True)
                st.altair_chart(no_project, use_container_width=True)

                # Rental NMS (TO)
                st.markdown("<h4 style='text-align: left;'>Rental NMS (TO)</h4>", unsafe_allow_html=True)
                st.altair_chart(rental_nms_to, use_container_width=True)

    else:
        # Real-time mode
        while True:
            end_time_input_now = datetime.now().strftime('%H:%M:%S')

            # Get data
            data = integrate_data(date=date_input, startTime=start_time_input, endTime=end_time_input)
            st.session_state['data'] = data

            # RENTAL BDM
            rental_bdm_fo = TransformVisualData.transform_fiz_1(data, 'Rental BDM', 'FO')
            rental_bdm_to = TransformVisualData.transform_fiz_1(data, 'Rental BDM', 'TO')

            # RENTAL NMS
            rental_nms_fo = TransformVisualData.transform_fiz_1(data, 'Rental NMS', 'FO')
            rental_nms_to = TransformVisualData.transform_fiz_1(data, 'Rental NMS', 'TO')

            # RENTAL PEMBATUAN
            rental_kbm = TransformVisualData.transform_fiz_1(data, 'Rental KBM', 'Pembatuan KBM')
            rental_mkg = TransformVisualData.transform_fiz_1(data, 'Rental MKG', 'Rental MKG')

            # KONTRAK BDM
            mining_bdm_to = TransformVisualData.transform_fiz_1(data, 'Mining BDM', 'TO')

            # TIDAK ADA PROJECT
            no_project = TransformVisualData.transform_fiz_1(data, 'Tidak Ada Job', 'Tidak Ada Job')

            # RENTAL KBM
            mining_kbm_fo = TransformVisualData.transform_fiz_1(data, 'Mining KBM', 'FO')
            mining_kbm_to = TransformVisualData.transform_fiz_1(data, 'Mining KBM', 'TO')

            # Show data
            with output_placeholder.container():
                r1c0, r1c1, r1c2, r1c3, r1c4, r1c5, r1c6 = st.columns([0.05, 0.5, 0.5, 0.1, 0.5, 0.5, 0.05], gap='small')

                with r1c1:
                    # Mining KBM (FO)
                    st.markdown("<h4 style='text-align: left;'>Mining KBM (FO)</h4>", unsafe_allow_html=True)
                    st.altair_chart(mining_kbm_fo, use_container_width=True)

                    # Rental BDM (FO)
                    st.markdown("<h4 style='text-align: left;'>Rental BDM (FO)</h4>", unsafe_allow_html=True)
                    st.altair_chart(rental_bdm_fo, use_container_width=True)

                    # Pembatuan KBM
                    st.markdown("<h4 style='text-align: left;'>Pembatuan KBM</h4>", unsafe_allow_html=True)
                    st.altair_chart(rental_kbm, use_container_width=True)

                    # Mining BDM (TO)
                    st.markdown("<h4 style='text-align: left;'>Mining BDM (TO)</h4>", unsafe_allow_html=True)
                    st.altair_chart(mining_bdm_to, use_container_width=True)

                    # Rental NMS (FO)
                    st.markdown("<h4 style='text-align: left;'>Rental NMS (FO)</h4>", unsafe_allow_html=True)
                    st.altair_chart(rental_nms_fo, use_container_width=True)
                
                with r1c4:
                    # Mining KBM (TO)
                    st.markdown("<h4 style='text-align: left;'>Mining KBM (TO)</h4>", unsafe_allow_html=True)
                    st.altair_chart(mining_kbm_to, use_container_width=True)

                    # Rental BDM (TO)
                    st.markdown("<h4 style='text-align: left;'>Rental BDM (TO)</h4>", unsafe_allow_html=True)
                    st.altair_chart(rental_bdm_to, use_container_width=True)

                    # Pembatuan MKG
                    st.markdown("<h4 style='text-align: left;'>Pembatuan MKG</h4>", unsafe_allow_html=True)
                    st.altair_chart(rental_mkg, use_container_width=True)

                    # Tidak Ada Job
                    st.markdown("<h4 style='text-align: left;'>Tidak Ada Job</h4>", unsafe_allow_html=True)
                    st.altair_chart(no_project, use_container_width=True)

                    # Rental NMS (TO)
                    st.markdown("<h4 style='text-align: left;'>Rental NMS (TO)</h4>", unsafe_allow_html=True)
                    st.altair_chart(rental_nms_to, use_container_width=True)
                

            time_2.sleep(5)