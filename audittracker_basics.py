"""
Basic functions for Lasersonix Q
Functions are called from LS_GUI.py
"""

import numpy as np
import scipy.io
import pickle
import pandas as pd
from math import pi
from matplotlib.gridspec import GridSpec
from matplotlib import style
import matplotlib.colors as colors
import datetime
import os
from tkinter import messagebox

# import ls_beta_daq as daq
# import ls_beta_signal as sigp


# Database manipulation ##########


def create_index_db(self):
    'Creates a new index database or fixes an existing one.'

    index_db_directory = self.index_db_directory.get()

    files = os.listdir(index_db_directory)

    data = {}
    index_db_path = index_db_directory + 'DB_Index.lsdb'

    filtered_files = []
    for item in files:
        if item.endswith('.lsdb') and item != 'DB_Index.lsdb':
            filtered_files.append(item)

    for item in filtered_files:
        LSID = os.path.splitext(item)[0]
        data[LSID] = {}
        metadata = read_db(index_db_directory + item, 'metadata')
        # try:
        #     data_count = read_db(index_db_directory + item,
        #                          'data',
        #                          'data_count',
        #                          )
        #     metadata['data_count'] = data_count
        # except:
        #     metadata['data_count'] = 0

        # try:
        #     settings = read_db(index_db_directory + item,
        #                        'settings',
        #                        )
        #     data[LSID]['settings'] = settings
        # except:
        #     data[LSID]['settings'] = 'use_default'

        data[LSID]['metadata'] = metadata

        park_data = read_db(index_db_directory + item)
        create_db(index_db_directory + LSID + '.lsdb')
        write_db(index_db_directory + LSID + '.lsdb', park_data)

    with open(index_db_path, 'wb') as f:
        pickle.dump(data, f)

    self.index_db_path.set(index_db_path)
    # self.status_label_text.set('Index Database Created')
    print('Index Database Created')


def create_db(db_file):
    " Creates a new part database file. "

    with open(db_file, 'wb') as f:
        data = {}
        data['metadata'] = {}
        data['settings'] = {}
        pickle.dump(data, f)


def write_db(db, value, pname=0, pname2=0, pname3=0, pname4=0):
    " Adding or changing a parameter in the database file. "
    with open(db, 'rb') as f:
        data = pickle.load(f)
        
        if pname == 0:
            data = value
        elif pname2 == 0:
            data[pname] = value
        elif pname3 == 0:
            data[pname][pname2] = value
        elif pname4 == 0:
            data[pname][pname2][pname3] = value
        else:
            data[pname][pname2][pname3][pname4] = value
    with open(db, 'wb') as f:
        pickle.dump(data, f)
        



def read_db(db, pname=0, pname2=0, pname3=0, pname4=0):
    " Reading the value of a parameter in the database file. "
    with open(db, 'rb') as f:
        data = pickle.load(f)
        if pname == 0:
            return data
        elif pname2 == 0:
            return data[pname]
        elif pname3 == 0:
            return data[pname][pname2]
        elif pname4 == 0:
            return data[pname][pname2][pname3]
        else:
            return data[pname][pname2][pname3][pname4]


def filter_listbox(self, parts, listbox):
    """ Filters listbox to show only selected options of parts. """

    filtered_parts = []
    display_options = [True, True, False]

    # if self.display_LSID_option.get():
    #     display_options[0] = True
    # if self.display_part_name_option.get():
    #     display_options[1] = True
    # if self.display_part_no_option.get():
    #     display_options[2] = True
    
    

    for part in parts:
        listentry = ''

        display_data = [part,
                        parts[part]['metadata']['DataSetName'],
                        parts[part]['metadata']['LSID']]

        for n, option in enumerate(display_options):
            if option:
                if listentry != '':
                    listentry += ' - '
                listentry += display_data[n]

        filtered_parts.append(listentry)
        listbox.insert(0, listentry)

    return filtered_parts


def fill_listbox(self):

    fname = 'Database/DB_Index.lsdb'
    remember = self.remember

    listbox = self.listbox31
    remember['index_db'] = fname
    remember['db_folder'] = fname[:-13]
    listbox.delete(0, 'end')

    parts = read_db(remember['index_db'])

    #   Storing part LS# for session
    remember['Parts'] = list(parts.keys())
    remember['Parts'].sort(reverse=True)
    remember['Parts2'] = filter_listbox(self, parts, listbox)


def load_file(self, remember):
    '''
    Reads parts in database and fills the listbox.
    Called by 'Browse' button.
    '''

    dir_path = filedialog.askdirectory()
    dir_path += '/'

    self.index_db_directory.set(dir_path)
    index_db_path = dir_path + 'DB_Index.lsdb'
    self.index_db_path.set(index_db_path)

    if not os.path.isfile(index_db_path):
        bf.create_index_db(self)

    fill_listbox(self)


def delete_part(self,selected_part, remember):
    "Deleting a part from database ('Delete Part' button)"
    if messagebox.askokcancel(
            'Delete',
            'Are you sure you want to delete the part: '
            + selected_part['DataSetName'] + '?'):
        
        temp_db = read_db(remember['index_db'])
        del temp_db[selected_part['LSID']]
        
        selected_part['part_db'] = \
        remember['db_folder'] \
        + selected_part['LSID'] \
        + remember['db_extension']
        
        os.remove(selected_part['part_db'])
        write_db(remember['index_db'], temp_db)
        # controller.show_frame(SelectPart)

        # #   Clearing selected_part information
        # selected_part['LSID'] = ''
        # selected_part['PartName'] = ''
        # selected_part['PartNumber'] = ''
        # selected_part['CreationDate'] = ''
        # selected_part['Description'] = ''



# def delete_run(self):
#     'Deletes a particular run from data'

#     selected_part = self.selected_part
#     part_db = selected_part['part_db']
#     data = read_db(part_db, 'data')
    
#     # Extracting user input from entry
#     selected_run = str(len(data['frf']))

#     selected_run = selected_run.replace(',', ':')
#     selected_run = selected_run.replace('-', ':')
#     selected_run = selected_run.split(':')
    

#     # Deleting single run

#     run = int(selected_run[0]) - 1
#     print(run)
#     # Deleting spectrums
    
#     if 'measurement_results' in data.keys():
#         if (len(data['frf']) == len(data['measurement_results']['part_results'])):
#             del data['measurement_results']['part_results'][run]
#             del data['measurement_results']['peak_frequencies'][run]
#             del data['measurement_results']['peak_frequency_results'][run]
#         else:
#             pass
    
#     del data['frf'][run]
#     del data['coherence'][run]
#     del data['measurement_time'][run]
    


#     # Deleting time data, if there is any
#     if 'time_data_ref' in data.keys():
#         del data['time_data_ref'][run]
#     if 'time_data_res' in data.keys():
#         del data['time_data_res'][run]

#     data['data_count'] = len(data['frf'])

#     write_db(part_db, data, 'data')


# def export_data(selected_part, export_format, indicator):
#     " Exports part data as Matlab .mat file. "

#     part_data = read_db(selected_part['part_db'])
#     part_lsid = selected_part['LSID']
#     db_folder = selected_part['db_folder'] + 'exported_data/'

#     if not os.path.exists(db_folder):
#         # Database directory is created if not found:
#         os.makedirs(db_folder)

#     try:
#         if export_format == '.mat':
#             export_path = db_folder + part_lsid + '.mat'
#             scipy.io.savemat(export_path, mdict={part_lsid: part_data})
#         elif export_format == '.csv':
#             export_path = db_folder + part_lsid + '_frf_abs.csv'
#             frf_data = np.abs(part_data['data']['frf'])
#             frf_array = frf_data[0]
#             for line in frf_data[1:]:
#                 frf_array = np.vstack((frf_array, line))
#             np.savetxt(export_path, frf_array, delimiter='\t', fmt='%.5E')
#         elif export_format == '.xlsx':
#             export_path = db_folder + part_lsid + '.xlsx'
#             frf_data = np.abs(part_data['data']['frf'])
            
#             frf_phase = np.angle(part_data['data']['frf'])
            
#             coh_data = part_data['data']['coherence']
#             time_ref = np.vstack(tuple(part_data['data']['time_data_ref']))
#             time_res = np.vstack(tuple(part_data['data']['time_data_res']))
#             freq = part_data['data']['freq']
#             time = part_data['data']['time']
#             writer = pd.ExcelWriter(export_path)
#             df_frf = pd.DataFrame(frf_data)
#             df_frf.to_excel(writer,
#                             'frf_abs',
#                             index=False,
#                             header=freq)
            
#             df_frf_phase = pd.DataFrame(frf_phase)
#             df_frf_phase.to_excel(writer,
#                             'frf_phase',
#                             index=False,
#                             header=freq)
            
#             df_coh = pd.DataFrame(coh_data)
#             df_coh.to_excel(writer,
#                             'coherence',
#                             index=False,
#                             header=freq)
#             df_time_ref = pd.DataFrame(time_ref)
#             df_time_ref.to_excel(writer,
#                                  'time_ref',
#                                  index=False,
#                                  header=time)
#             df_time_res = pd.DataFrame(time_res)
#             df_time_res.to_excel(writer,
#                                  'time_res',
#                                  index=False,
#                                  header=time)
#             writer.save()

#         indicator.set('Created file: ' + export_path)
#     except:
#         indicator.set('Problem encountered while exporting data.')

# def trigger_learning(selected_part,remember):
#     """ Starts data acquisition and gathers data.
#         Runs when triggered manually or digitally.
#         Calculates FRF and coherence spectrums.
#         Saves the spectrums in the part database.
#         Also saves time data if the user chooses so. """

#     # Initializes the dictionary to store this run data
#     rundata = {}

#     part_db = selected_part['part_db']
#     settings = selected_part['settings']

#     run_averages = settings['run_averages']
#     resolution = settings['resolution']

#     # Test data is collected from DAQ device
#     testdata = daq.test_part(selected_part, run_averages)

#     # Time data is extracted from the data
#     reference_time = testdata[1]
#     response_time = testdata[2]

#     # if settings['save_additional_channel'] == 1:
#     #     rundata['additional_data'] = testdata[3]

#     # FRF & Coherence spectrums are calculated:
#     frf, coherence, a, b = sigp.time2frf(reference_time, response_time)

#     # Number of samples
#     N = np.shape(reference_time)[1]

#     # Frequency axis
#     freq = np.linspace(0, N * resolution, N + 1)

#     # Shortening the frequency range to work with dependable data
#     N_simp = round(N * 0.5)

#     # Shortening latest run data to desired frequency range
#     rundata['freq'] = freq[:N_simp]
#     rundata['frf'] = frf[:N_simp]
#     rundata['coherence'] = coherence[:N_simp]

#     selected_part['latest_frf'] = rundata['frf']
#     selected_part['latest_frf_freq'] = rundata['freq']
#     selected_part['latest_coherence'] = rundata['coherence']
    
#     # Getting all SelectedPart information
#     part_data = read_db(part_db)
    
#     # Getting current date and time
#     now = datetime.datetime.now()
#     rundata['measurement_time'] = now.strftime('%Y-%m-%d %H:%M')
    
   
                
#     # Adding collected data to Part data
#     if 'learning_data' in part_data.keys():
#         learning_data = part_data['learning_data']
        
#         learning_data['frf'].append(rundata['frf'])
#         learning_data['coherence'].append(rundata['coherence'])
#         learning_data['measurement_time'].append(rundata['measurement_time'])
    
#     else:
        
#         # Creating data dictionary and lists, saving axes
#         learning_data = {}
        
#         learning_data['frf'] = []
#         learning_data['coherence'] = []
#         learning_data['measurement_time'] = []
    
#         learning_data['freq'] = rundata['freq']
#         learning_data['time'] = testdata[0]
    
#         # Creating time data lists, if requested
#         if settings['save_ref_time']:
#             learning_data['time_data_ref'] = []
#         if settings['save_res_time']:
#             learning_data['time_data_res'] = []
#         if settings['save_additional_channel']:
#             learning_data['time_data_additional'] = []
    
#         # Writing latest run data
#         learning_data['frf'].append(rundata['frf'])
#         learning_data['coherence'].append(rundata['coherence'])
#         learning_data['measurement_time'].append(rundata['measurement_time'])
    
#     # Saving time data, if requested
#     if settings['save_ref_time']:
#         rundata['time_data_ref'] = reference_time
#         learning_data['time_data_ref'].append(rundata['time_data_ref'])
    
#     if settings['save_res_time']:
#         rundata['time_data_res'] = response_time
#         learning_data['time_data_res'].append(rundata['time_data_res'])
    
#     # if settings['save_additional_channel']:
#     #     data['time_data_additional'].append(rundata['additional_data'])
    
#     # Adjusting the data counter
#     # part_data['learning_data']['M1_Level']['data_count'] = len(part_data['learning_data']['M1_Level']['frf'])
#     # selected_part['data_count'] = data['data_count']
    
#     # Writing updated data array into database
#     write_db(part_db, learning_data,'learning_data')



# def trigger(selected_part):
#     """ Starts data acquisition and gathers data.
#         Runs when triggered manually or digitally.
#         Calculates FRF and coherence spectrums.
#         Saves the spectrums in the part database.
#         Also saves time data if the user chooses so. """

#     # Initializes the dictionary to store this run data
#     rundata = {}
    
#     part_db = selected_part['part_db']
#     settings = selected_part['settings']

#     run_averages = settings['run_averages']
#     resolution = settings['resolution']

#     # Test data is collected from DAQ device
#     testdata = daq.test_part(selected_part, run_averages)

#     # Time data is extracted from the data
#     reference_time = testdata[1]
#     response_time = testdata[2]

#     # if settings['save_additional_channel'] == 1:
#     #     rundata['additional_data'] = testdata[3]

#     # FRF & Coherence spectrums are calculated:
#     frf, coherence, a, b = sigp.time2frf(reference_time, response_time)

#     # Number of samples
#     N = np.shape(reference_time)[1]

#     # Frequency axis
#     freq = np.linspace(0, N * resolution, N + 1)

#     # Shortening the frequency range to work with dependable data
#     N_simp = round(N * 0.5)

#     # Shortening latest run data to desired frequency range
#     rundata['freq'] = freq[:N_simp]
#     rundata['frf'] = frf[:N_simp]
#     rundata['coherence'] = coherence[:N_simp]

#     selected_part['latest_frf'] = rundata['frf']
#     selected_part['latest_frf_freq'] = rundata['freq']
#     selected_part['latest_coherence'] = rundata['coherence']
    
#     # Getting all SelectedPart information
#     part_data = read_db(part_db)
    
#     # Getting current date and time
#     now = datetime.datetime.now()
#     rundata['measurement_time'] = now.strftime('%Y-%m-%d %H:%M')
    
#     # Adding collected data to Part data
#     if 'data' in part_data.keys():
#         data = part_data['data']
        
#     else:
#         # Creating data dictionary and lists, saving axes
#         data = {}
#         data['frf'] = []
#         data['coherence'] = []
#         data['measurement_time'] = []        
        
#         data['freq'] = rundata['freq']
#         data['time'] = testdata[0]
    
#         # Creating time data lists, if requested
#         if settings['save_ref_time']:
#             data['time_data_ref'] = []
#         if settings['save_res_time']:
#             data['time_data_res'] = []
#         if settings['save_additional_channel']:
#             data['time_data_additional'] = []
    
#     # Writing latest run data
#     data['frf'].append(rundata['frf'])
#     data['coherence'].append(rundata['coherence'])
#     data['measurement_time'].append(rundata['measurement_time'])

#     # Saving time data, if requested
#     if settings['save_ref_time']:
#         rundata['time_data_ref'] = reference_time
#         data['time_data_ref'].append(rundata['time_data_ref'])
    
#     if settings['save_res_time']:
#         rundata['time_data_res'] = response_time
#         data['time_data_res'].append(rundata['time_data_res'])
    
#     if settings['save_additional_channel']:
#         data['time_data_additional'].append(rundata['additional_data'])
    
#     # Adjusting the data counter
#     data['data_count'] = len(data['frf'])
#     selected_part['data_count'] = data['data_count']

#     # Writing updated data array into database
#     write_db(part_db, data, 'data')
        


# def evaldata(self):
#     """
#     Evaluates the data for to the interval in frequency entries.
#     Uses the chosen calculation method.
#     """

#     selected_part = self.selected_part
#     calculation_method = self.calculation_method.get()
#     page = self.main_label_text.get()
#     part_db = selected_part['part_db']
#     fft_or_psd = self.fft_or_psd.get()
#     ref_signal_choice = self.ref_signal_choice.get()
#     res_signal_choice = self.res_signal_choice.get()

#     if fft_or_psd == 2:
#         psd_res = int(self.psd_res.get())
#     else:
#         psd_res = 0

#     self.status_label_text.set('Analyzing Data')

#     analysis_freq = get_analysis_freq(self)

#     #   Loading data with analysis outputs
#     analyzed_data = load_and_analyze(
#             part_db,
#             calculation_method=calculation_method,
#             analysis_freq=analysis_freq,
#             fft_or_psd=fft_or_psd,
#             psd_res=psd_res,
#             ref_signal=ref_signal_choice,
#             res_signal=res_signal_choice
#             )

#     selected_part['data_count'] = analyzed_data['data_count']
#     selected_part['lsq'] = analyzed_data['cors']

#     #   Displaying passing & failing sample numbers
#     if analyzed_data['data_count'] > 1:
#         display_pass_fail(self, selected_part)

#     # Clearing figure and creating subplots
#     format_chart_area(self, 'spectrum_and_lsq')

#     # Plots frf spectrums and LSQ ratings
#     plot_frf(self, analyzed_data, page)
#     plot_lsq(self, selected_part, page)

#     # Adding axis labels and executing other formatting options
#     format_plots(self)

#     self.canvas1.draw()

#     self.data_count.set(str(analyzed_data['data_count']))

#     self.status_label_text.set('Data evaluation complete.')

#     if page == 'Review Part':
#         #   Enabling 'Calculate displayed range' button
#         self.button12['state'] = 'normal'


# def check_part(self):
#     """
#     Compares the latest run data with the stored selected_part data.
#     """

#     selected_part = self.selected_part

#     calculation_method = selected_part['settings']['calculation_method']
#     latest_frf_freq = selected_part['latest_frf_freq']
#     latest_frf = selected_part['latest_frf']
#     latest_coherence = selected_part['latest_coherence']
#     analysis_freq = selected_part['settings']['analysis_freq']

#     frf_ref = selected_part['frf_ref']
#     coh_ref = selected_part['coh_ref']
#     freq_ref = selected_part['freq_ref']

#     #   Cropping latest FRF in frequency domain to match
#     #   with reference FRF
#     latest_frf = crop_freq(
#         latest_frf,
#         latest_frf_freq,
#         analysis_freq)[1]

#     latest_coherence = crop_freq(
#         latest_coherence,
#         latest_frf_freq,
#         analysis_freq)[1]

#     lsq = compute_lsq(
#         latest_frf,
#         frf_ref,
#         calc_method=calculation_method,
#         check_part=True)

#     selected_part['lsq'].append(lsq)

#     #   Displaying passing & failing parts
#     display_pass_fail(self, selected_part)

#     #   Clearing figure and creating subplots
#     format_chart_area(self, 'spectrum_and_lsq')

#     self.a1.semilogy(freq_ref, abs(latest_frf), color='orange')
#     self.a3.plot(freq_ref, np.angle(latest_frf), color='orange')
#     self.a4.plot(freq_ref, latest_coherence, color='orange')

#     self.a1.semilogy(freq_ref, abs(frf_ref), 'k', linewidth=0.5)
#     self.a3.plot(freq_ref, np.angle(frf_ref), 'k', linewidth=0.5)
#     self.a4.plot(freq_ref, coh_ref, 'k', linewidth=0.5)

#     selected_part['data_count_session'] = len(selected_part['lsq'])

#     #   Plot of correlation values
#     plot_lsq(self, selected_part, page='Check Part')

#     format_plots(self)

#     self.canvas1.draw()

#     self.data_count.set(str(selected_part['data_count']))

#     write_db(selected_part['part_db'], lsq, 'data', 'checked_lsq')

#     if lsq > float(self.threshold.get()):
#         self.status_label_text.set(
#             f"Sample {str(selected_part['data_count'])} OK")
#         self.status_label.configure(foreground='white', background='green')
#     else:
#         self.status_label_text.set(
#             f"Sample {str(selected_part['data_count'])} NOK")
#         self.status_label.configure(foreground='white', background='red')








# def get_analysis_freq(self):
#     freqs_input = self.text11.get('1.0', 'end-1c').splitlines()
#     freqs = []
#     n = 0
#     for line in freqs_input:
#         freqs.append((int(line.split()[0]), int(line.split()[1])))
#         n += 1
#     return freqs


# def plot_lsq(self, selected_part, caller='', page='Review Part'):
#     """
#     Plotting LSQ ratings as either histogram or individual ratings.
#     """

#     #   Reading data from database
#     lsq = selected_part['lsq']

#     chart_type = self.hist_or_ind.get()

#     #   clearing figure
#     self.a2.cla()

#     #   LSQ ratings plot
#     if chart_type == 1:
#         #   Histogram of correlation values
#         self.a2.hist(lsq, bins='auto', orientation='horizontal')
#         self.a2.set_title('Histogram of LSQ ratings')
#         self.a2.set_xlabel('Number of samples')

#     elif chart_type == 2:
#         #   Individual value plot of correlation values
#         if 'data_count_session' in selected_part.keys() \
#                                         and page == 'Check Part':
#             first_sample_index = selected_part['data_count'] \
#                                  - selected_part['data_count_session'] \
#                                  + 1
#         else:
#             first_sample_index = 1
#         sample_no = list(range(first_sample_index,
#                                selected_part['data_count'] + 1))
#         self.a2.plot(sample_no, lsq, 'ko')
#         if page != 'Review Part':
#             self.a2.plot(sample_no[-1], lsq[-1], color='orange', marker='o')
#             self.a2.annotate(str(round(lsq[-1], 1)),
#                              (sample_no[-1], lsq[-1]))
#         self.a2.set_title('LSQ ratings')
#         self.a2.set_xlabel('Sample no')
#         self.a2.plot((sample_no[0], sample_no[-1]),
#                      (float(self.threshold.get()),
#                       float(self.threshold.get())),
#                       color='red')
#         if self.threshold2.get() != '':
#             self.a2.plot(
#                     (sample_no[0], sample_no[-1]),
#                     (float(self.threshold2.get()),
#                      float(self.threshold2.get())),
#                     color='yellow')
#     self.a2.grid(True)

#     if caller == 'radio_button':
#         self.canvas.draw()

#     # Stores the value indicating if the current page is run details
#     selected_part['run_details'] = False


# #   Highlights the chosen curve in the plot
# def highlight_run(self, selected_part):

#     selected_run = int(self.selected_run.get()) - 1
#     part_db = selected_part['part_db']

#     #   Reading data from database
#     data = read_db(part_db, 'data')

#     #   Frequency and frf axes from data
#     freq = data['freq']
#     frf = data['frf'][selected_run]
#     coherence = data['coherence'][selected_run]

#     analysis_freq = get_analysis_freq(self)

#     freq, frf = crop_freq(frf, freq, analysis_freq)
#     coherence = crop_freq(coherence, freq, analysis_freq)[1]

#     #   Plotting selected run
#     if self.amplitude_scale.get() == 'log':
#         self.a1.semilogy(freq, abs(frf), 'b', linewidth=1)
#     else:
#         self.a1.plot(freq, abs(frf), 'b', linewidth=1)
#     self.a3.plot(freq, np.angle(frf), 'b', linewidth=1)
#     self.a4.plot(freq, coherence, 'b', linewidth=1)

#     self.canvas1.draw()


# def plot_rundata(self):

#     selected_sample = self.selected_sample.get()
#     selected_run = self.selected_run.get()
#     if selected_sample == '':
#         selected_sample = self.selected_part['data_count']
#         self.selected_sample.set(str(selected_sample))
#     else:
#         selected_sample = int(selected_sample)

#     # Correcting selected_sample to get the index in list
#     selected_sample -= 1

#     if selected_run == '':
#         selected_run = 1
#         self.selected_run.set(str(selected_run))
#     else:
#         selected_run = int(selected_run)

#     # Correcting selected_run to get the index in list
#     selected_run -= 1

#     settings = self.selected_part['settings']
#     data = read_db(self.selected_part['part_db'], 'data')

#     averages = settings['run_averages']
#     sampling_rate = settings['sampling_rate']

#     reference_time = data['time_data_ref'][selected_sample]
#     response_time = data['time_data_res'][selected_sample]
#     time_axis = data['time']

#     if self.fft_or_psd.get() == 1:
#         # Plots FFT spectra
#         processed_data = sigp.time2frf(reference_time,
#                                        response_time)
#         freq_axis = data['freq']
#         N_half = int(len(freq_axis))
#         freq_coh = freq_axis
#         FRF = processed_data[0][:N_half]
#         coherence = processed_data[1][:N_half]
#         reference_spec = processed_data[2][:N_half]
#         response_spec = processed_data[3][:N_half]

#     else:
#         # Plots PSD spectra
#         try:
#             psd_res = int(self.psd_res.get())
#         except:
#             psd_res = 32

#         #   Calculating PSD and FRF spectra of data
#         processed_data = sigp.time2frf_psd(reference_time,
#                                            response_time,
#                                            sampling_rate,
#                                            f_res=psd_res,
#                                            rundetails=True)

#         #   Extracting axes and spectra from data
#         freq_axis = processed_data[0]
#         FRF = processed_data[1]
#         freq_coh = processed_data[2]
#         coherence = processed_data[3]
#         reference_spec = processed_data[4]
#         response_spec = processed_data[5]

#     if averages != 1:
#         reference_time = reference_time[selected_run]
#         response_time = response_time[selected_run]

#     if self.overlay_run_data.get():
#         #   Plotting time data
#         self.p1.plot(time_axis, reference_time, 'r')
#         self.p2.plot(time_axis, response_time, 'r')

#         #   Plotting PSDs
#         self.p3.semilogy(freq_axis, reference_spec, 'r')
#         self.p4.semilogy(freq_axis, response_spec, 'r')

#         #   Plotting FRF amplitude and coherence
#         self.p5.semilogy(freq_axis, abs(FRF), 'r')
#         self.p6.plot(freq_coh, coherence, 'r')

#     else:
#         #   Clearing chart area and creating subplots
#         format_chart_area(self, 'run_details')

#         #   Plotting time data
#         self.p1.plot(time_axis, reference_time)
#         self.p2.plot(time_axis, response_time)

#         #   Plotting PSDs
#         self.p3.semilogy(freq_axis, reference_spec)
#         self.p4.semilogy(freq_axis, response_spec)

#         #   Plotting FRF amplitude and coherence
#         self.p5.semilogy(freq_axis, abs(FRF))
#         self.p6.plot(freq_coh, coherence)

#         # Labels and titles for the plots
#         self.p5.set_ylabel('FRF mag')
#         self.p6.set_ylabel('Coherence')

#         self.p1.set_ylabel('Time')
#         self.p3.set_ylabel('FFT')

#         self.p1.set_title('Reference')
#         self.p2.set_title('Response')

#         for item in self.plots:
#             item.grid(True)

#         self.fig2.tight_layout()
#         self.fig3.tight_layout()

#     self.canvas2.draw()
#     self.canvas3.draw()

#     self.selected_part['run_details'] = True


# def display_pass_fail(self, selected_part):
#     """
#     Displays numbers of passing & failing parts.
#     """

#     lsq = selected_part['lsq']
#     threshold = float(self.threshold.get())

#     #   Getting indices of passing and failing parts
#     selected_part['passing_samples'] = \
#         [index + 1 for index, value in enumerate(lsq) if value >= threshold]
#     selected_part['failing_samples'] = \
#         [index + 1 for index, value in enumerate(lsq) if value < threshold]

#     #   Getting number of passing & failing parts
#     selected_part['passing_samples_count'] = \
#         len(selected_part['passing_samples'])
#     selected_part['failing_samples_count'] = \
#         len(selected_part['failing_samples'])

#     #   Displaying number of passing & failing parts
#     self.passing_samples_count.set(
#             str(selected_part['passing_samples_count'])
#             )
#     self.failing_samples_count.set(
#             str(selected_part['failing_samples_count'])
#             )

#     #   Clearing passing and failing part numbers
#     self.passing_samples_textbox.delete('1.0', 'end')
#     self.failing_samples_textbox.delete('1.0', 'end')

#     self.passing_samples_textbox.insert(
#             'end',
#             str(selected_part['passing_samples'])
#             )
#     self.failing_samples_textbox.insert(
#             'end',
#             str(selected_part['failing_samples'])
#             )


# def format_plots(self):
#     " Formats the labels and limits of plots in the chart area. "

#     #   FRF amplitude plot of all data
#     self.a1.set_ylabel('Amplitude')
#     self.a1.tick_params(labelbottom=False)
#     self.a1.tick_params(labelleft=False)
#     if self.plot_colormap.get() is False:
#         self.a1.grid(True)

#     #   Phase plot of all data
#     self.a3.set_xlabel('Frequency [Hz]')
#     self.a3.set_ylabel('Phase')
#     self.a3.tick_params(labelleft=False)
#     self.a3.grid(True)

#     #   Coherence plot of all data
#     self.a4.set_title('FRF data')
#     self.a4.tick_params(labelbottom=False)
#     self.a4.tick_params(labelleft=False)
#     self.a4.set_ylabel('Coherence')
#     self.a4.set_ylim(0, 1)
#     self.a4.grid(True)

#     #   LSQ ratings
#     self.a2.set_ylim(0)
#     self.a2.yaxis.tick_right()
#     self.a2.grid(True)

#     self.fig1.tight_layout()
#     self.fig1.subplots_adjust(hspace=0)


# def format_chart_area(self, chart_area):
#     """
#     Clearing chart area and adjusting subplot orientations.
#     """

#     style.use('classic')

#     if chart_area == 'spectrum_and_lsq':

#         #   Clearing figure
#         self.fig1.clf()

#         #   Adding subplots with the desired layout
#         gs = GridSpec(3, 2,
#                       width_ratios=[2, 1],
#                       height_ratios=[1, 3, 1])
#         self.a3 = self.fig1.add_subplot(gs[2, 0])
#         self.a1 = self.fig1.add_subplot(gs[1, 0], sharex=self.a3)
#         self.a4 = self.fig1.add_subplot(gs[0, 0], sharex=self.a3)
#         self.a2 = self.fig1.add_subplot(gs[:, 1])

#     elif chart_area == 'run_details':

#         #   Clearing figure
#         self.fig2.clf()
#         self.fig3.clf()

#         # Adding FFT tab subplots with the desired layout
#         gs2 = GridSpec(2, 2)
#         self.p1 = self.fig2.add_subplot(gs2[0, 0])
#         self.p2 = self.fig2.add_subplot(gs2[0, 1], sharex=self.p1)
#         self.p3 = self.fig2.add_subplot(gs2[1, 0])
#         self.p4 = self.fig2.add_subplot(gs2[1, 1], sharex=self.p3)

#         # Adding FRF tab subplots with the desired layout
#         gs3 = GridSpec(2, 1)
#         self.p5 = self.fig3.add_subplot(gs3[0, 0])
#         self.p6 = self.fig3.add_subplot(gs3[1, 0])

#         # Creating a list of plots to be called later on
#         self.plots = [self.p1, self.p2, self.p3,
#                       self.p4, self.p5, self.p6]


# def plot_frf(self, analyzed_data, page):
#     """
#     Plots FRF spectrums (coherence, amplitude & phase) of each part.
#     """

#     if 'coherence' in analyzed_data.keys():
#         coherence = analyzed_data['coherence']
#         if np.sum(coherence) == 0:
#             plotcoh = False
#         else:
#             coh_ref = analyzed_data['coh_ref']
#             plotcoh = True
#     else:
#         plotcoh = False

#     thres = float(self.threshold.get())

#     #   The data to be plotted
#     freq = analyzed_data['freq']
#     frf = analyzed_data['frf']
#     frf_ref = analyzed_data['frf_ref']
#     data_count = analyzed_data['data_count']
#     cors = analyzed_data['cors']

#     if page == 'Learn Part':

#         #   Plotting all the data on charts
#         for n in range(data_count):

#             if n == 0 and data_count == 1:
#                 self.a1.semilogy(freq, abs(frf), 'b', linewidth=0.5)
#                 self.a3.plot(freq, np.angle(frf), 'r', linewidth=0.5)
#                 self.a4.plot(freq, coherence)

#             elif n+1 == data_count:
#                 self.a1.semilogy(freq, abs(frf[n]), 'k', linewidth=0.5)
#                 self.a3.plot(freq, np.angle(frf[n]), 'k', linewidth=0.5)
#                 self.a4.plot(freq, coherence[n], 'k', linewidth=0.5)

#             else:
#                 self.a1.semilogy(freq, abs(frf[n]), 'y', linewidth=0.5)
#                 self.a3.plot(freq, np.angle(frf[n]), 'y', linewidth=0.5)
#                 self.a4.plot(freq, coherence[n], 'y', linewidth=0.5)

#     elif page == 'Review Part':

#         if self.plot_colormap.get() is True:
#             frf_array = np.array(np.abs(frf))
#             y = np.linspace(1, data_count, data_count)

#             if self.amplitude_scale.get() == 'lin':
#                 self.a1.pcolormesh(
#                         freq,
#                         y,
#                         frf_array,
#                         # cmap='Blues',
#                         )

#             elif self.amplitude_scale.get() == 'log':
#                 self.a1.pcolormesh(
#                         freq,
#                         y,
#                         frf_array,
#                         norm=colors.LogNorm(),
#                         )

#         # Flattening reference angle spectrum if difference spectrum
#         # option is selected:
#         if self.diff_spectrum.get():
#             angle_ref = np.zeros(np.shape(frf_ref))
#         else:
#             angle_ref = np.angle(frf_ref)

#         for n in range(data_count):

#             # Creating difference spectrum if option is selected:
#             if self.diff_spectrum.get():
#                 angle_spec = abs(np.angle(frf_ref) - np.angle(frf[n]))

#                 for i in range(len(angle_spec)):
#                     if angle_spec[i] >= pi:
#                         angle_spec[i] = 2 * pi - angle_spec[i]
#             else:
#                 angle_spec = np.angle(frf[n])

#             if cors[n] < thres:
#                 if self.plot_colormap.get() is False:
#                     if self.amplitude_scale.get() == 'lin':
#                         self.a1.plot(freq, abs(frf[n]), 'r', linewidth=0.5)
#                     else:
#                         self.a1.semilogy(freq, abs(frf[n]), 'r', linewidth=0.5)
#                 # self.a3.plot(freq, np.angle(frf[n]), 'r', linewidth=0.5)
#                 self.a3.plot(freq, angle_spec, 'r', linewidth=0.5)
#                 if plotcoh:
#                     self.a4.plot(freq, coherence[n], 'r', linewidth=0.5)

#             else:
#                 if self.plot_colormap.get() is False:
#                     if self.amplitude_scale.get() == 'lin':
#                         self.a1.plot(freq, abs(frf[n]), 'g', linewidth=0.5)
#                     else:
#                         self.a1.semilogy(freq, abs(frf[n]), 'g', linewidth=0.5)
#                 # self.a3.plot(freq, np.angle(frf[n]), 'g', linewidth=0.5)
#                 self.a3.plot(freq, angle_spec, 'g', linewidth=0.5)
#                 if plotcoh:
#                     self.a4.plot(freq, coherence[n], 'g', linewidth=0.5)

#         if self.plot_colormap.get() is False:
#             self.a1.plot(freq, np.abs(frf_ref), 'k', linewidth=0.5)
#         # self.a3.plot(freq, np.angle(frf_ref), 'k', linewidth=0.5)
#         self.a3.plot(freq, angle_ref, 'k', linewidth=0.5)
#         if plotcoh:
#             self.a4.plot(freq, coh_ref, 'k', linewidth=0.5)
