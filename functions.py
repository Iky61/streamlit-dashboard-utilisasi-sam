# import library and settings
import pandas as pd
import numpy as np
import ssl
import requests
from datetime import datetime, timedelta
import xmlrpc.client
from streamlit_gsheets import GSheetsConnection
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# create class for data joiner
class SuportFunction:
    # tansform sekumpulan data kedalam tipe data string
    @staticmethod
    def join_to_text(data):
        data = np.unique(data)
        return ','.join(data)

    # transform sekumpulan data kedalam tipe data aray
    @staticmethod
    def join_to_array(data):
        data = np.unique(data)
        return list(data)
    
    # transform stardar digit for time data type
    @staticmethod
    def transform_time_digit(x):
        con = len(x)
        if con < 2:
            msg = '0' + x
        else:
            msg = x
        return msg
    
    # buat fungsi untuk transformasi data time
    @staticmethod
    def transform_actual_hours(point):
        try:
            if point == '0.0':
                msg = '00:00'
            else:
                hour = str(point).split('.')[0]
                hour = SuportFunction.transform_time_digit(hour)
                
                minute = '0.' + str(point).split('.')[-1]
                minute = float(minute)
                minute = str(int(np.ceil(minute * 60)))
                minute = SuportFunction.transform_time_digit(minute)
                
                msg = hour + ':' + minute
        except:
            msg = point
        return msg
    
    # create convertion local time
    @staticmethod
    def convert_to_local_time(utc_time_str, target_timezone='Asia/Makassar'):
        try:
            # Mengonversi string waktu UTC ke objek datetime
            utc_time = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")
            
            # Menentukan waktu sebagai UTC
            utc_zone = pytz.utc
            utc_time = utc_zone.localize(utc_time)
            
            # Mengonversi ke zona waktu lokal
            local_zone = pytz.timezone(target_timezone)
            local_time = utc_time.astimezone(local_zone)
            msg = local_time.strftime("%Y-%m-%d %H:%M:%S")
        except:
            msg = pd.NaT
        return msg
    
    # create function to transform Oprator columns
    @staticmethod
    def transform_last_data_from_list(x):
        try:
            msg = x[-1]
        except:
            msg = x
        return msg
    
    # create function to transform datetime
    @staticmethod
    def transform_datetime(x):
        try:
            msg = pd.to_datetime(x)
        except:
            msg = pd.NaT
        return msg
    
    # create function to split data per-n units in list
    @staticmethod
    def spliting_data(data):
        startIter = 0
        ids_list = data.split(';')

        msg = []
        for n in range(7, len(ids_list) + 1, 7):
            batch = ids_list[startIter:n]  # Mengambil 5 elemen dari list
            msg.append(';'.join(batch))
            startIter += 7
            
        # Menangani batch terakhir jika ada sisa elemen
        if startIter < len(ids_list):
            batch = ids_list[startIter:len(ids_list)]
            msg.append(';'.join(batch))
        return msg
    
    # create function to count Retase
    def retaseGPS(data):
        data['geofences'].fillna('Unknown', inplace=True)
        index_timbangan = data[data.geofences.apply(lambda x: 'Stockpile KM 7' in x or 'Area Pabrik' in x)].index.tolist()
        
        local_datetime_ = []
        geofences_ = []
        for i in range(len(index_timbangan)):
            if data.iloc[index_timbangan[i] - 1]['geofences'] != "":
                local_datetime_.append(data.iloc[index_timbangan[i] - 1]['local_datetime'])
                geofences_.append(data.iloc[index_timbangan[i] - 1]['geofences'])
            else:
                local_datetime_.append(data.iloc[index_timbangan[i] - 2]['local_datetime'])
                geofences_.append(data.iloc[index_timbangan[i] - 2]['geofences'])
        
        evaluated = pd.DataFrame({'local_datetime_before_bongkaran':local_datetime_, 'geofences_before_bongkaran':geofences_})
        evaluated = evaluated[evaluated['geofences_before_bongkaran'].apply(lambda x: 'Stockpile KM 7' in x or 'Area Pabrik' in x) == False]

        return len(evaluated.index.tolist())
    
# create class to GET data from APi
class GetDataApi:
    # Methods untuk menarik data dari GSheet
    @staticmethod
    def ConnectionGSheet(url, index_cols):
        connection = st.connection("gsheets", type=GSheetsConnection)
        data = connection.read(spreadsheet=url, usecols=index_cols)
        return data

    # Methods untuk menarik data dari Odoo Api
    @staticmethod
    def ApiOdoo(path, date, start_hour="00:00:00", end_hour="23:59:59", fields=None, batch_size=50000):

        # Bypass SSL certificate verification
        context_odoo = ssl._create_unverified_context()

        # Correct the URL to include the proper protocol (http/https)
        url_odoo = "https://node3.solusienergiutama.com"
        db_odoo = "cvsa"
        username_odoo = 'dicky.gps105@gmail.com'
        password_odoo = "lotongmanis0210"

        # Attempting authentication with bypassed SSL verification
        common_odoo = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url_odoo), context=context_odoo) 

        # get uid 
        uid_odoo = common_odoo.authenticate(db_odoo, username_odoo, password_odoo, {})

        models = xmlrpc.client.ServerProxy(f"{url_odoo}/xmlrpc/2/object", context=context_odoo)

        # Menghitung start_date (7 hari sebelum date)
        end_date = f"{date} {end_hour}"
        start_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d") + f" {start_hour}"

        # Gantilah 'request_date' dengan field yang sesuai di Odoo
        domain = [('request_date', '>=', start_date), ('request_date', '<=', end_date)]

        # Ambil data dengan filter tanggal & jam
        records = models.execute_kw(db_odoo, uid_odoo, password_odoo, path, 'search_read', [domain], {'fields': fields, 'limit': batch_size})

        # Return data
        return records
    
    # Methods untuk menarik data units dari GPS
    @staticmethod
    def ApiGps_units():
        url_devices_itel = "https://gps.intellitrac.co.id/apis/tracking/devices.php"

        # Data yang dikirim ke API
        payload = {
            "username": "sa_api",
            "password": "n6oCrx2f3I",
        }

        # Header opsional (tergantung pada kebutuhan API)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Mengirim permintaan POST
        response = requests.post(url_devices_itel, data=payload, headers=headers)

        # JSON to DataFrame
        db_unit_intel = pd.DataFrame(response.json()['data'])
        db_unit_intel = db_unit_intel[db_unit_intel.name.apply(lambda x: 'zTerminated' in x) == False]
        db_unit_intel = db_unit_intel[db_unit_intel.name.apply(lambda x: 'dilepas' in x) == False]

        # transform
        db_unit_intel['name_odoo'] = db_unit_intel.name.apply(lambda x: '-'.join(str(x).split()[1:]))
        db_unit_intel = db_unit_intel[db_unit_intel.device_id != '2019120162']

        # return data
        return db_unit_intel

    # Methods untuk menarik data historical move dari GPS
    def ApiGps_hist(date, start_hour='00:00:00', end_hour='23:59:59', unitIds='', tbl_unit=''):
        # condition if unitsIds not inputed
        if unitIds == '':
            unitIds = ';'.join(GetDataApi.ApiGps_units().device_id.unique().tolist())
        else:
            None
        
        # prepare data
        startDate = pd.to_datetime(str(date).split()[0] + ' ' + start_hour)
        endDate = pd.to_datetime(str(date).split()[0] + ' ' + end_hour)
        splitIds = SuportFunction.spliting_data(unitIds)
        
        _ = []
        for ids in splitIds:
            url_hist_itel = "http://gps.intellitrac.co.id/apis/tracking/history.php"
            
            # Data yang dikirim ke API
            payload = {
                "username": "sa_api",
                "password": "n6oCrx2f3I",
                "start_datetime":startDate,
                "end_datetime":endDate,
                "devices":ids
            }
            
            # Header opsional (tergantung pada kebutuhan API)
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Mengirim permintaan POST
            response = requests.post(url_hist_itel, data=payload)
            
            # # JSON to DataFrame
            db_historical_intel = response.json()
            fields = ['device_id','local_datetime','location','geofences','ignition_status','longitude','latitude','driver_name','speed','mileage','hourmeter']
            
            # transformasi data
            __ = []
            for i in ids.split(';'):
                try:
                    data = pd.DataFrame(db_historical_intel['data'][i]['history']).sort_values(['local_datetime'], ascending=False).reset_index(drop=True)
                    data['device_id'] = i
                    data = data[fields]
                except:
                    data = pd.DataFrame({'local_datetime':[pd.NaT],'location':[np.nan],'geofences':[np.nan],'ignition_status':[np.nan],
                                        'longitude':[np.nan],'latitude':[np.nan],'driver_name':[np.nan],'speed':[np.nan],'mileage':[np.nan],'hourmeter':[np.nan]})
                    data['device_id'] = i
                    data = data[fields]
                __.append(data)
            _.append(pd.concat(__))

        # cleaning data
        msg = pd.concat(_).reset_index(drop=True)
        msg = msg.merge(tbl_unit[['name_odoo','device_id']], on='device_id', how='left')
        msg = msg[['device_id','name_odoo','local_datetime','location','longitude','latitude','geofences','ignition_status','speed','mileage','hourmeter']]

        msg['geofences'].fillna('Unknown', inplace=True)
        msg['geofences'] = msg['geofences'].apply(lambda x: ', '.join(x) if type(x) == list else x)
        
        msg['local_datetime'].fillna(pd.NaT, inplace=True)
        msg['local_datetime'] = pd.to_datetime(msg['local_datetime'])
        
        msg['speed'].fillna(0, inplace=True)
        msg['speed'] = msg['speed'].astype(float)
        
        msg['mileage'].fillna(0, inplace=True)
        msg['mileage'] = msg['mileage'].astype(float)
        
        msg['hourmeter'].fillna(0, inplace=True)
        msg['hourmeter'] = msg['hourmeter'].astype(float)
        
        msg['location'].fillna('Tidak Diketahui', inplace=True)
        msg['ignition_status'].fillna('Tidak Diketahui', inplace=True)

        msg['longitude'].fillna(0, inplace=True)
        msg['latitude'].fillna(0, inplace=True)

        # return data
        return msg
        
# create class to transform data
class TransformData:
    @staticmethod
    def maintOdoo(date, start_hour="00:00:00", end_hour="23:59:59"):
        # prepare for fields custom
        field_maintenance_request = ['name','stage_id','broken_date','request_date','schedule_date','actual_date','actual_hour','date_done','employee_id',
                                    'equipment_id','hm_engine','km_engine','requirement_type','maintenance_type','maintenance_kind_id','note','description']

        mainReq = GetDataApi.ApiOdoo(path='maintenance.request',date=date ,start_hour=start_hour, end_hour=end_hour ,fields=field_maintenance_request)
        mainReq = pd.DataFrame(mainReq)

        # rename columns DataFrame
        mainReq = mainReq.drop(columns=['id'])
        mainReq.columns = ['Subjects','Stage','Broken Date','Request Date','Scheduled Date','Actual Date','Actual Hour','Completion Date',
                        'Oprator','Equipment','HM','KM','Requirement Type','Maintenance Type','Maintenance kind','Instruction','Description']
        
        # filter data
        mainReq['Broken Date'] = mainReq['Broken Date'].apply(lambda x: str(x))
        mainReq = mainReq[mainReq['Broken Date'] != 'False']

        mainReq['Broken Date'] = pd.to_datetime(mainReq['Broken Date'])
        mainReq = mainReq[mainReq['Broken Date'].dt.year >= 2023]
        mainReq['Broken Date'] = mainReq['Broken Date'].apply(lambda x: str(x))
        
        # transform data Actual Date & Actual Hour
        mainReq['Actual Date'] = mainReq['Actual Date'].apply(lambda x: str(x))
        mainReq['Actual Hour'] = mainReq['Actual Hour'].apply(lambda x: str(x))
        
        # apply function
        mainReq['Actual Hour'] = mainReq['Actual Hour'].apply(SuportFunction.transform_actual_hours)
        mainReq['Actual Date'] = mainReq['Actual Date'] + ' ' + mainReq['Actual Hour']
        mainReq = mainReq.drop(columns=['Actual Hour'])
        
        # transform Scheduled Date
        mainReq['Scheduled Date'] = mainReq['Scheduled Date'].apply(lambda x: str(x))
        
        # transform Actual Date to Datetime
        mainReq['Actual Date'] = mainReq.apply(lambda x: pd.NaT if x['Scheduled Date'] == 'False' else x['Actual Date'], axis=1)
        
        # Cleaning Data String
        for i in ['Stage','Oprator','Equipment','Maintenance kind']:
            mainReq[i] = mainReq[i].apply(SuportFunction.transform_last_data_from_list)
        
        # Cleaning Data Datetime
        for i in ['Broken Date','Request Date','Scheduled Date','Completion Date','Actual Date']:
            if i not in ['Request Date','Actual Date']:
                mainReq[i] = mainReq[i].apply(SuportFunction.convert_to_local_time)
            else:
                mainReq[i] = mainReq[i].apply(SuportFunction.transform_datetime)
                # mainReq[i] = pd.to_datetime(mainReq[i])
        
        # Cleaning Data String to Capitalize
        mainReq['Requirement Type'] = mainReq['Requirement Type'].apply(lambda x: str(x).capitalize())
        mainReq['Maintenance Type'] = mainReq['Maintenance Type'].apply(lambda x: str(x).capitalize())

        # Transforming columns
        mainReq.columns = ['_'.join(i.lower().split()) for i in mainReq.columns]
        mainReq = mainReq.rename(columns={'equipment':'name_odoo'})
        mainReq['name_odoo'] = mainReq.name_odoo.apply(lambda x: str(x).split('/')[0])
        mainReq = mainReq[mainReq.stage != 'Cancel']
        mainReq['broken_date'] = pd.to_datetime(mainReq['broken_date'])
        mainReq['scheduled_date'] = pd.to_datetime(mainReq['scheduled_date'])
        mainReq['completion_date'] = pd.to_datetime(mainReq['completion_date'])

        # return
        return mainReq
    
    # create function transformation to get summary of GPS inteliTrack
    @staticmethod
    def transformGPS(data):
        # define variabels
        data = data.reset_index(drop=True)
        device_id = data['device_id'].unique().tolist()[0]
        name_odoo = data['name_odoo'].unique().tolist()[0]
        
        # get start & end works
        try:
            startWorks = data[data.ignition_status.isin(['ON'])].sort_values('local_datetime', ascending=True)['local_datetime'].unique().tolist()[0]
        except:
            startWorks = pd.NaT

        try:
            endWokrs = data[data.ignition_status.isin(['ON'])].sort_values('local_datetime', ascending=False)['local_datetime'].unique().tolist()[0]
        except:
            endWokrs = pd.NaT

        # get summary
        avgSpeed = data[data.ignition_status.isin(['ON'])].speed.mean()
        maxSpeed = data[data.ignition_status.isin(['ON'])].speed.max()
        
        datetimeMaxSpeed = data[data.speed == maxSpeed]['local_datetime']
        locationMaxSpeed = data[data.speed == maxSpeed]['location']
        engineStatusUpdate = data.sort_values('local_datetime', ascending=False).ignition_status.unique().tolist()[0]
        locationUpdate = data.sort_values('local_datetime', ascending=False).location.unique().tolist()[0]
        geofanceUpdate = data.sort_values('local_datetime', ascending=False).geofences.unique().tolist()[0]
        longitudeUpdate = data.sort_values('local_datetime', ascending=False).longitude.unique().tolist()[0]
        latitudeUpdate = data.sort_values('local_datetime', ascending=False).latitude.unique().tolist()[0]
        localdatetimeUpdate = data.sort_values('local_datetime', ascending=False).local_datetime.unique().tolist()[0]
        hm = data.hourmeter.max() - data.hourmeter.min()
        km = data.mileage.max() - data.mileage.min()
        retase = SuportFunction.retaseGPS(data)

        # working status condition
        workingStatus = data.sort_values('local_datetime', ascending=False)[['mileage']].head(20)
        workingStatus = workingStatus.mileage.max() - workingStatus.mileage.min()
        if workingStatus > 0:
            workingStatus = 'OPR'
        else:
            workingStatus = 'IDLE'

        # concat summary
        msg = {
            'start_date':[startWorks],
            'end_date':[endWokrs],
            'avg_speed':[np.round(avgSpeed, 4)],
            'max_speed':[np.round(maxSpeed, 4)],
            'local_datetime':[localdatetimeUpdate],
            'max_speed_date':[datetimeMaxSpeed],
            'max_speed_location':[locationMaxSpeed],
            'ignition_status_update':[engineStatusUpdate],
            'gps_working_status':[workingStatus],
            'location_update':[locationUpdate],
            'longitude':[longitudeUpdate],
            'latitude':[latitudeUpdate],
            'geofance_update':[geofanceUpdate],
            'hm':[hm],
            'km':[km],
            'retase':[retase]
        }

        # transform to dataframe and cleansing
        msg = pd.DataFrame(msg)
        msg['device_id'] = device_id
        msg['name_odoo'] = name_odoo
        msg = msg[['device_id','name_odoo','ignition_status_update','gps_working_status','location_update','local_datetime','longitude','latitude','geofance_update','hm','km','retase',
                'start_date','end_date','avg_speed','max_speed','max_speed_date','max_speed_location']]
        msg['end_date'] = msg.apply(lambda x: pd.NaT if x.ignition_status_update == 'ON' else x.end_date, axis=1)

        # return data
        return msg
    
    # create function transformation to get summary of maintenance odoo
    @staticmethod
    def transformMaintenance(data):
        
        # define variabels
        data = data.sort_values('broken_date', ascending=False).reset_index(drop=True)
        name_odoo = data['name_odoo'].unique().tolist()[0]

        data = data.groupby(['name_odoo']).agg({
            'stage':SuportFunction.join_to_array,
            'subjects':SuportFunction.join_to_array,
            'broken_date':SuportFunction.join_to_array,
        }).reset_index()

        # return data
        return data
    
    # create function merge data Odoo and GPS for build utilization report
    @staticmethod
    def summaryUtilisasi(date, start_hour='00:00:00', end_hour='23:59:59', device_id='', tbl_unit=''):
        # condition if unitsIds not inputed
        if device_id == '':
            device_id = ';'.join(GetDataApi.ApiGps_units().device_id.unique().tolist())
        else:
            None

        # get data maintenance and gps
        maintennace_history = TransformData.maintOdoo(date=date, start_hour=start_hour, end_hour=end_hour)
        gps_history = GetDataApi.ApiGps_hist(date=date, start_hour=start_hour, end_hour=end_hour, unitIds=device_id, tbl_unit=tbl_unit)

        # filter data
        maintenance_history = maintennace_history[(maintennace_history.stage != 'DONE')]

        # get summary of GPS datasets
        _ = []
        for i in gps_history.device_id.unique():
            data = gps_history[gps_history.device_id == i]
            summaryGps = TransformData.transformGPS(data)
            _.append(summaryGps)
        summaryGps = pd.concat(_).reset_index(drop=True).drop(columns=['device_id'])

        # get summary of Maintenance datasets
        _ = []
        for i in maintenance_history.name_odoo.unique():
            data = maintenance_history[maintenance_history.name_odoo == i]
            summaryMaintenance = TransformData.transformMaintenance(data)
            _.append(summaryMaintenance)
        summaryMaintenance = pd.concat(_).reset_index(drop=True)

        # get summaries
        summary = tbl_unit[['device_id','name_odoo']]
        summary = summary[summary.device_id.isin(device_id.split(';'))]
        summary = summary.merge(summaryGps, on='name_odoo', how='left')
        summary = summary.merge(summaryMaintenance, on='name_odoo', how='left')

        # return
        return summary