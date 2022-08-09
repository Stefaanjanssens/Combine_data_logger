#script to combine data logged with humidity logger and with an independent instrument.
# Use this if the timestamp doesn't correspond in the logged files.
# The script will give as output data of the independent instrument at the timestamps of the logger and average over x points


import pandas as pd
import numpy as np
from matplotlib import pyplot
from numpy import arange
import matplotlib.pyplot as plt
from datetime import timedelta
from datetime import datetime

from dateutil import parser


#copy the filenames below of the files to be used. The dir should be the same as where the code is located
#output directory will be in a new excel sheet. The file ".xls" should contain two sheets with the data in.
# DUT data in sheet 1 and logger data in sheet 2.
# Both should hav a column called datetime and should have the date and time in the following layout: example 26/11/2021 15:15
#filename_data='testdatas.xls'
filename_data='LH001298_TS2500.xls'
#number of points to average over
average_points=10
#time interval in seconds (Will be automatically calculated if left at default 0, but can be manually filled in as well.)
time_interval=0

data_DUT= pd.read_excel(filename_data, sheet_name='Sheet1') #data of the DUT with the different timestamp
data_logger= pd.read_excel(filename_data, sheet_name='Sheet2') #data of the humidity generator

data_DUT.columns = data_DUT.iloc[1]
data_DUT = data_DUT.drop([0, 1])
data_DUT =data_DUT.dropna()

data_logger.columns = data_logger.iloc[1]
data_logger = data_logger.drop([0, 1])
#data_logger = data_logger.dropna()


#convert to datetime format
data_DUT['datetime']=pd.to_datetime(data_DUT['datetime'])
data_logger['datetime']=pd.to_datetime(data_logger['datetime'])
# #Next section is only for troubleshooting
# order=True
# prevdate=data_DUT['datetime'].iloc[0]
# for date in data_DUT['datetime']:
#     diffdate=prevdate-date
#     if diffdate >= timedelta(seconds=0):
#         print(date)
#         print(diffdate)
#         order=False
#     #(data_logger['datetime'].iloc[]-data_logger['datetime'].iloc[3])>=timedelta(seconds=0)
#     prevdate=date

if time_interval==0:
    time_interval=data_DUT['datetime'].iloc[3]-data_DUT['datetime'].iloc[2]
data_DUT['datetime before shift']=data_DUT['datetime']


#tolerance for data merge takes the values around the point.
# To average over points prior to our datapoint we need to shift the time with half the interval.
#if data is out of sync it can be ajusted by the next shift
data_DUT['datetime'] = data_DUT['datetime before shift']
additional_shift=timedelta( minutes=0)
time_shift=((average_points)*time_interval)+additional_shift
data_DUT['datetime']=data_DUT['datetime']+time_shift
average_time=time_interval*average_points

#looks for the same time stamp in both datasets
#data_merge_left=pd.merge_asof(data_logger,data_DUT,tolerance=pd.Timedelta(average_time))
data_merge_right=pd.merge_asof(data_DUT,data_logger,tolerance=pd.Timedelta(average_time))
data_merge_right_nonan=data_merge_right.dropna()

#just for troubleshooting
#data_merge_right_nonan.to_excel("outputnan.xlsx")
#data_merge_right.to_excel("outputr.xlsx")
#data_merge_left.to_excel("outputl.xlsx")

#averaging over  points
i=0
for column in data_DUT.columns:
    print(column)
    if type(data_merge_right_nonan[column].iloc[0])==float or type(data_merge_right_nonan[column].iloc[0])==int:
        data_logger['mean '+column]=(data_merge_right_nonan.groupby('no.')[column].mean()).shift(+1)
        data_logger['std '+column]=data_merge_right_nonan.groupby('no.')[column].std().shift(+1)
        #print(data_merge_right_nonan.groupby('no.')[column].mean())
    elif column=='datetime':
        data_logger['DUT datetime'] = data_merge_right_nonan.groupby('no.')[column].min().shift(+1)
        #print(data_merge_right_nonan.groupby('no.')[column])
#save to excel in same directory
#data_merge_right_nonan.to_excel("outputnan.xlsx")
data_logger.to_excel(f"datacombined {filename_data}.xlsx")

# print(data_logger.columns)
# print(data_DUT.columns)

ax=data_logger.plot.scatter(x='datetime', y='mTc 2500', color="DarkBlue", label="logger");
#data_logger.plot.scatter(x="datetime", y="mean T", color="DarkGreen",marker="x" ,label="DUT",ax=ax);
plt.errorbar(x=data_logger["datetime"], y=data_logger["mean Temperature"],xerr=average_time ,yerr=data_logger["std Temperature"], color="DarkGreen", label="DUT",fmt=".");
data_DUT.plot.line(x='datetime', y='Temperature', color="DarkBlue", label="DUT" ,ax=ax);

az=data_logger.plot.scatter(x='datetime', y='mRH_at_DUT', color="DarkRed", label="logger");
plt.errorbar(x=data_logger["datetime"], y=data_logger['mean Humidity'],xerr=average_time ,yerr=data_logger["std Humidity"], color="DarkGreen", label="DUT",fmt=".");
data_DUT.plot.line(x='datetime', y='Humidity', color="DarkBlue", label="DUT",ax=az);
plt.show()



