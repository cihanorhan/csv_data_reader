# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:51:13 2020

@author: otosanvs
"""
import pandas
import matplotlib.pyplot as plt
import json 
import numpy as np
import struct
import wave
import numpy as np
import scipy.signal

import time
import binascii
import csv




# Open CSV File --------------------------------------------------------------

# df_csv_1 = pandas.read_csv('C01_Run27.csv', encoding = "ISO-8859-1")
# df_csv_2 = pandas.read_csv('C01_Run28.csv', encoding = "ISO-8859-1")
# # df_csv_3 = pandas.read_csv('C01_Run29.csv', encoding = "ISO-8859-1")
# # df_csv_4 = pandas.read_csv('C01_Run30.csv', encoding = "ISO-8859-1")
# # df_csv_5 = pandas.read_csv('C01_Run31.csv', encoding = "ISO-8859-1")


# colum_list_1=df_csv_1.columns.tolist()
# time_csv_1 = df_csv_1[colum_list_1[0]]
# data_csv_1 = df_csv_1[colum_list_1[2]]

# colum_list_2=df_csv_2.columns.tolist()
# time_csv_2 = df_csv_2[colum_list_2[0]]
# data_csv_2 = df_csv_2[colum_list_2[2]]

# # colum_list_3=df_csv_3.columns.tolist()
# # time_csv_3 = df_csv_3[colum_list_3[0]]
# # data_csv_3 = df_csv_3[colum_list_3[2]]

# # colum_list_4=df_csv_4.columns.tolist()
# # time_csv_4 = df_csv_4[colum_list_4[0]]
# # data_csv_4 = df_csv_4[colum_list_4[2]]

# # colum_list_5=df_csv_5.columns.tolist()
# # time_csv_5 = df_csv_5[colum_list_5[0]]
# # data_csv_5 = df_csv_5[colum_list_5[2]]



# # plt.plot(time_csv,data_csv)
# # plt.xlabel(colum_list[0])
# # plt.ylabel("Sound Pressure [Pa]")
# # plt.title(colum_list[1])
# # plt.show()

# # plt.plot(time_csv,data_csv)
# # plt.xlabel(colum_list[0])
# # plt.ylabel("Velocity [m/s]")
# # plt.title(colum_list[3])
# # plt.show()

# def signal_psd(
#     time_data,
#     sampling_rate,
#     f_resolution=4,
#     overlap=66,
#     # analysis_freq=None,
#     ):

#     signal_shape = np.shape(time_data)
#     assert len(signal_shape) <= 2, \
#         'Cannot compute PSD for array shape: {}'.format(signal_shape)

#     block_size = int(sampling_rate / f_resolution)
#     n_overlap = int(block_size * overlap / 100)

#     if len(signal_shape) == 1:
#         time_data = [time_data]

#     psd = np.zeros((len(time_data), int(block_size/2 + 1)))

#     for i, data in enumerate(time_data):
#         freq, psd[i] = scipy.signal.welch(
#             data,
#             fs=sampling_rate,
#             window='boxcar',
#             noverlap=n_overlap,
#             nperseg=block_size, )

#     # if analysis_freq is not None:
#     #     freq, psd = crop_freq(psd, freq, analysis_freq)

#     return freq, psd

# # freq_sample_1, spec_sample_1 = signal_psd(
# #         data_csv_1,
# #         50000,
# #         f_resolution=1.0,
# #         overlap=66,
# #         )
# # freq_sample_2, spec_sample_2 = signal_psd(
# #         data_csv_2,
# #         50000,
# #         f_resolution=1.0,
# #         overlap=66,
# #         )
# # freq_sample_3, spec_sample_3 = signal_psd(
# #         data_csv_3,
# #         50000,
# #         f_resolution=1.0,
# #         overlap=66,
# #         )
# # freq_sample_4, spec_sample_4 = signal_psd(
# #         data_csv_4,
# #         50000,
# #         f_resolution=1.0,
# #         overlap=66,
# #         )
# # freq_sample_5, spec_sample_5 = signal_psd(
# #         data_csv_5,
# #         50000,
# #         f_resolution=1.0,
# #         overlap=66,
# #         )
    
# power_1 = np.square(data_csv_1)
# power_2 = np.square(data_csv_2)
# sum_value_1 = np.sum(power_1)
# sum_value_2 = np.sum(power_2)


# fig = plt.figure()
# ax1 = fig.add_subplot(111)

# ax1.plot(1,sum_value_1,'o',color='red')
# ax1.plot(2,sum_value_2,'o',color='red')

# # ax1.plot(freq_sample_2[5:],np.transpose(spec_sample_2)[5:],color='blau')
# # ax1.plot(freq_sample_3[5:],np.transpose(spec_sample_3)[5:],color='black')
# # ax1.plot(freq_sample_4[5:],np.transpose(spec_sample_4)[5:],color='green')
# # ax1.plot(freq_sample_5[5:],np.transpose(spec_sample_5)[5:],color='yellow')


# # ax1.set_yscale('log')



# # def signal_power(time_data):
# #     signal_shape = np.shape(time_data)
# #     assert len(signal_shape) <= 2, \
# #         'Cannot compute signal power for array shape: {}'.format(signal_shape)

# #     power = np.square(time_data)
# #     return np.average(power, axis=-1)


# # def signal_energy(time_data):
# #     signal_shape = np.shape(time_data)
# #     assert len(signal_shape) <= 2, \
# #         'Cannot compute signal energy for array shape: {}'.format(signal_shape)

# #     power = np.square(time_data)
# #     return np.sum(power, axis=-1)



# Open JSON File -------------------------------------------------------------

# with open('C01_Run1.json',) as f:
#     maindata_json = json.load(f) 

# time_json=[]
# data_json=[]
# for i in maindata_json['Data'][0]['Channel :Mikrofon[Pa]']:
#     time_json.append(i[0])
#     data_json.append(i[1])
# Channal_Name=list(maindata_json['Data'][0].keys())[1]
    
# plt.plot(time_json,data_json)
# plt.xlabel('Time [s]')
# plt.ylabel("Sound Pressure [Pa]")
# plt.title(Channal_Name)
# plt.show()


# Open TXT File --------------------------------------------------------------

# with open('C01_Run1.txt','r') as f:
#     maindata_txt = f.readlines()[11:]

# time_txt = []
# data_txt = []
# for i in maindata_txt:
#     b = str.split(i)
#     time_txt.append(float(b[0]))
#     data_txt.append(float(b[1]))

# plt.plot(time_txt,data_txt)
# plt.xlabel('Time [s]')
# plt.ylabel("Sound Pressure [Pa]")
# plt.title('Channel :Mikrofon[Pa]')
# plt.show()