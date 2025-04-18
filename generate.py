# import library
import streamlit  as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# import library dari function.py
from functions import SuportFunction, GetDataApi, TransformData

def get_data_plan_utilisasi(date):
    # transfomasi date_input agar sesuai dengan format penulisan tanggal default
    date_input = date.strftime("%d/%m/%Y")

    # read data plan
    data = GetDataApi.ConnectionGSheet(
        url="https://docs.google.com/spreadsheets/d/1E3OmS-aUfVq55VEk9AE3TpKEURBVcr4TCMS75Y77egU/edit?gid=1836032641#gid=1836032641/edit?usp=sharing", 
        index_cols=np.arange(0, 9)
    )

    # transform data plan
    data_plan_cols = data.iloc[3].tolist()
    data = data[data.index>3]
    data.columns = data_plan_cols
    data.drop(columns=['No'], inplace=True)
    data['Tanggal'] = data['Tanggal'].apply(lambda x: str(x).split()[0])

    # filter data sesuai input users
    data = data[data.Tanggal == date_input].reset_index(drop=True)

    # return data
    return data


def get_data_summary(date, startTime, endTime):
    # get data plan utilisasi
    data_plan = get_data_plan_utilisasi(date)

    # configurasi inputan dari user
    date_input = str(date).split()[0]
    start_time_input = str(startTime)
    end_time_input = str(endTime)

    # tarik data units
    tbl_unit = GetDataApi.ApiGps_units()
    tbl_unit = tbl_unit[tbl_unit.name_odoo.apply(lambda x: 'DT' in x)]

    # filter data
    tbl_unit = tbl_unit[tbl_unit.name_odoo.isin([f"DT-{i}" for i in [529,519]])]

    unit_sep_semicolon = ';'.join(tbl_unit.device_id.unique().tolist())

    # get datetime now if real-time is Activate
    # date_now = str(datetime.now()).split()[0]

    # get data and save to excel 
    data_summary = TransformData.summaryUtilisasi(date=date_input, start_hour=start_time_input, end_hour=end_time_input, device_id=unit_sep_semicolon, tbl_unit=tbl_unit).sort_values('name_odoo', ascending=True)
    data_summary = data_summary[['name_odoo','local_datetime','start_date','end_date','ignition_status_update','gps_working_status','retase','geofance_update']]

    # return data
    return data_summary