# import library
import streamlit  as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# import library dari function.py
from functions import SuportFunction, GetDataApi, TransformData

# get data plan utilisasi dari DIV. Kendaraan
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
    data.columns = ['tanggal','kontrak','move_type','equipment_category','equipment_name','name_odoo','employee','unit_condition']

    # return data
    return data

# get data validasi unit dari DIV. WORKSHOP
def get_data_validasi_ws():
    # read data plan
    data = GetDataApi.ConnectionGSheet(
        url="https://docs.google.com/spreadsheets/d/1E3OmS-aUfVq55VEk9AE3TpKEURBVcr4TCMS75Y77egU/edit?gid=94889657#gid=94889657/edit?usp=sharing",
        index_cols=[11,19]
    )

    # cleaning data
    data.dropna(axis=0, how='all', inplace=True)
    data.columns = ['name_odoo','validasi_ws']

    # return
    return data

# get data perlakuan unit dari GPS InteliTrac
def get_data_gps(date, startTime, endTime):
    # configurasi inputan dari user
    date_input = str(date).split()[0]
    start_time_input = str(startTime)
    end_time_input = str(endTime)

    # tarik data units
    tbl_unit = GetDataApi.ApiGps_units()
    tbl_unit = tbl_unit[tbl_unit.name_odoo.apply(lambda x: 'DT' in x)]

    # filter data
    # tbl_unit = tbl_unit[tbl_unit.name_odoo.isin([f"DT-{i}" for i in [385,386,387,367,358,365,363]])]
    unit_sep_semicolon = ';'.join(tbl_unit.device_id.unique().tolist())

    # get data and save to excel 
    data_summary = TransformData.summaryUtilisasi(date=date_input, start_hour=start_time_input, end_hour=end_time_input, device_id=unit_sep_semicolon, tbl_unit=tbl_unit).sort_values('name_odoo', ascending=True)
    data_summary = data_summary[['name_odoo','local_datetime','start_date','end_date','ignition_status_update','gps_working_status','retase','geofance_update']]

    # return data
    return data_summary

# integrasikan data
def integrate_data(date, startTime, endTime):
    # send get data
    plan_utilisasi = get_data_plan_utilisasi(date)
    validasi_ws = get_data_validasi_ws()
    utilisasi_gps = get_data_gps(date, startTime, endTime)

    # integrate data
    msg = plan_utilisasi.drop(columns=['tanggal','employee']).merge(validasi_ws, on='name_odoo', how='left')
    msg = msg.merge(utilisasi_gps, on='name_odoo', how='left')

    # cleaning data
    msg['unit_condition'].fillna('Unknown', inplace=True)
    msg['validasi_ws'].fillna('Unknown', inplace=True)
    msg['ignition_status_update'].fillna('Unknown', inplace=True)
    msg['ignition_status_update'].replace('Tidak Diketahui','Unknown', inplace=True)
    msg['gps_working_status'].fillna('Unknown', inplace=True)

    # transform to get status utilisasi
    msg['utilisasi_status'] = msg.apply(lambda x: SuportFunction.unit_status_clasified(x.unit_condition, x.validasi_ws, x.ignition_status_update, x.gps_working_status), axis=1)

    # recolumns data
    msg = msg[['kontrak','move_type','equipment_category','equipment_name','name_odoo','local_datetime','start_date','end_date','retase','geofance_update','utilisasi_status']]

    # merge data
    return msg
