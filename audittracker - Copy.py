# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 15:52:05 2020

@author: otosanvs
"""
import os
import warnings
import logging
import logging.config
import time
import threading
import queue
import tkinter as tk
from tkinter import ttk
from tkinter import *
from PIL import Image, ImageTk
import wtguifuncs as gf
from pandas import DataFrame
from pathlib import Path
import audittracker_basics as basics
import audittracker_settings as settings

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

import pandas
import matplotlib.pyplot as plt
import json 
import numpy as np
import struct
import wave
import numpy as np
import scipy.signal
import scipy.fftpack
import time
import binascii
import csv

import os
import glob
import pandas as pd
import threading
from scipy import signal
from scipy.fft import fft

from tkinter import filedialog
from tkinter import font as tkFont

PARAM_DB = 'audittracker_parameters.lsp'
LARGE_FONT = ('Helvatica', 12)


#   Dictionary to store variables within session
remember = {}
remember = basics.read_db(PARAM_DB, 'default_files')

#   Initializing selected part information
selected_part = {}

selected_part['LSID'] = ''
selected_part['DataSetName'] = ''
selected_part['CreationDate'] = ''
selected_part['Description'] = ''

remember['initial_selected_part'] = selected_part

choices={}
choices['calculation_method']=[]
choices['calculation_method'] =('Energy Method','Method2','Method3')

test_data_store=[]

time_data_store=[]
acc_data_store=[]
acc_fft_data_store=[]

mic_data_store = []
mic_fft_data_store = []

filt_acc_data_store=[]
filt_acc_fft_data_store=[]

filt_mic_data_store = []
filt_mic_fft_data_store = []

powersum_acc_data_store=[]
filt_powersum_acc_data_store=[]

powersum_mic_data_store = []
filt_powersum_mic_data_store = []


sampling_rate = 50000.0
low = 2500.0

class AuditTracker(tk.Tk):
    
    def __init__(self, *args, **kwargs):
            tk.Tk.__init__(self, *args, **kwargs)
            tk.Tk.iconbitmap(self)
            tk.Tk.wm_title(self, "AuditTracker v0.1")
    
            container = tk.Frame(self)
            container.pack(side="top", fill="both", expand=True)
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)
    
            #   Defining pages
            self.frames = {}
            for F in (
                       MainMenu,
                       PlotPage,
                       ImportPage,
                      # EditPart,
                      # ReviewPage,
                      # CheckPage
                      ):
                frame = F(container, self)
                self.frames[F] = frame
                frame.grid(row=0, column=0, sticky="nsew")
    
            self.show_frame(MainMenu)
    
    def show_frame(self, page_name):
        """ Shows the page page_name and generates ShowFrame event. """
        frame = self.frames[page_name]
        frame.tkraise()
        frame.event_generate('<<ShowFrame>>')

class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground   

class MainMenu(tk.Frame):
    """ Page for displaying and analyzing previously collected data. """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.page_name = 'Main Menu'
        
        frame3 = ttk.LabelFrame(self, text='Main Menu')
        frame3.grid(row=1,column=1,
                    padx=350, pady=150, sticky='nsew')
        
        # self.imgdefinepart = PhotoImage(file="define_part2.png")
        self.button21 = HoverButton(frame3, text="Import CSV Data",  width=25, font=LARGE_FONT, 
                                    activebackground='Silver', 
                                    command = lambda: controller.show_frame(ImportPage))
        self.button21.grid(row=1, column=1, sticky='nsew')
        
        # self.imgmeasure = PhotoImage(file="measure.png")        
        self.button22 = HoverButton(frame3, text="Plot Data",compound=TOP,height = 10, width=25, font=LARGE_FONT, 
                                    activebackground='Silver', 
                                    command = lambda: controller.show_frame(PlotPage))          
        self.button22.grid(row=1, column=2, sticky='nsew')

        # self.imgdatareview = PhotoImage(file="data_review.png") 
        self.button23 = HoverButton(frame3, text="...",compound=TOP, height = 10,width=25, font=LARGE_FONT, 
                                   activebackground='Silver', 
                                   command = lambda: controller.show_frame(DataReviewPage))        
        self.button23.grid(row=1, column=3, sticky='nsew')
        
        self.button24 = HoverButton(frame3, text="...",height = 10, width=20,  font=LARGE_FONT, 
                                    activebackground='Silver', 
                                    command = lambda: login_user(self))
        self.button24.grid(row=2, column=1, sticky='nsew')
        
        self.button25 = HoverButton(frame3, text="...",height = 10, width=20,  font=LARGE_FONT, 
                                    activebackground='Silver', 
                                    command = lambda: login_user(self))
        self.button25.grid(row=2, column=2, sticky='nsew')

        # self.imgadministration = PhotoImage(file="administration.png") 
        self.button26 = HoverButton(frame3, text="...",compound=TOP, width=25,  font=LARGE_FONT, 
                                    activebackground='Silver', 
                                    command = lambda: login_user(self)) 
        self.button26.grid(row=2, column=3, sticky='nsew')
        
        for item in frame3.winfo_children():
            item.grid(in_=frame3, padx=5, pady=5)
            
        # self.img = PhotoImage(file="beta.png")
        # self.imglabel27 =tk.Label(frame3, image=self.img)
        # self.imglabel27.grid(row=3, column=2, sticky='nsew')


class ImportPage(tk.Frame):
    """ Page for displaying and analyzing previously collected data. """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.page_name = 'Import Page'
        helv15 = tkFont.Font(family='Helvetica', size=15, weight='bold') 
        
        
        #   Loaded database file name
        self.index_db_path = tk.StringVar()
        self.index_db_path.set(remember['index_db'])

        self.index_db_directory = tk.StringVar()
        self.index_db_directory.set(remember['db_folder'])
        
        
        
        
        
        self.frame0 = ttk.LabelFrame(self, text='CSV Data Import')
        self.frame0.grid(
            row=0, column=0,
            sticky='nsew',
            padx=140, pady=40)
        
        self.button_select_folder = HoverButton(self.frame0, 
                                                text='Select Data Folder',
                                                font=helv15,bg='#2c3968',fg='white', 
                                                activebackground='Silver', 
                                                command=lambda: selectdatafolder(self))
        self.button_select_folder.grid(row=10,rowspan=2,
                                       column=10,columnspan=2, 
                                       sticky='nsew', padx=5, pady=5)  
        
        self.folder_path = tk.StringVar()
        self.entry_folder_path = ttk.Entry(self.frame0, 
                                           textvariable=self.folder_path,
                                           state='normal',font=helv15,width=50).grid(row = 10,rowspan=2,
                                                                                     column=12, columnspan=10,
                                                                                     sticky='nsew', 
                                                                                     padx=5, pady=5)
    
        self.label_Datasetname = tk.Label(self.frame0, 
                                          text='DataSet Name',font=helv15 ).grid(row = 12,rowspan=2, 
                                                                                 column=10, columnspan=2,
                                                                                 sticky='w', padx=5, pady=5)
        self.Datasetname = tk.StringVar()
        self.entry_Datasetname = ttk.Entry(self.frame0, 
                                           textvariable=self.Datasetname,state='normal',
                                           font=helv15,width=50).grid(row = 12,rowspan=2, 
                                                                      column=12, columnspan=10,
                                                                      sticky='nsew', padx=5, pady=5)
        
        
        self.label_Description = tk.Label(self.frame0, 
                                          text='Description',font=helv15 ).grid(row = 14,rowspan=2, 
                                                                                 column=10, columnspan=2,
                                                                                 sticky='w', 
                                                                                 padx=5, pady=5)
                                                                      
        self.text_Description = tk.Text(self.frame0, wrap='word',
                              height=4)
        self.text_Description.grid(row=14,rowspan=2,  
                         column=12, columnspan=10,
                         sticky='nsew',
                         padx=5, pady=5)
                                                                                      
                                                                      
                                                                      
        self.label_Status = tk.Label(self.frame0, 
                                     text='Status',font=helv15 ).grid(row = 16,rowspan=2,
                                                                      column=10, columnspan=2,
                                                                      sticky='w', padx=5, pady=5)
        self.Status = tk.StringVar()
        self.label_result_Status = tk.Label(self.frame0, 
                                            textvariable=self.Status,
                                            state='normal',font=helv15,borderwidth = 3,
                                            relief="sunken", width=50).grid(row = 16,rowspan=2, 
                                                                            column=12, columnspan=10,
                                                                            sticky='nsew', padx=5, pady=5)
        
        self.Status_cond = tk.StringVar()
        self.label_result_Status_cond = tk.Label(self.frame0, 
                                                 textvariable=self.Status_cond,
                                                 state='normal',font=helv15, ).grid(row = 16,rowspan=2,
                                                                                    column=22, columnspan=5,
                                                                                    sticky='nsew', 
                                                                                    padx=5, pady=5)
        self.Status_cond.set('No Data')
        
        self.button_import_csv = HoverButton(self.frame0, 
                                             text='Import Data',font=helv15,
                                             width=15,bg='#2c3968',fg='white',
                                                activebackground='Silver', 
                                                command=lambda: [settings.save_part(self,remember),import_csv_data(self),])
        self.button_import_csv.grid(row=10,rowspan=6,
                                    column=22,columnspan=5, 
                                    sticky='nsew', 
                                    padx=5, pady=5)  
        
        
        self.label_dummy1 = tk.Label(self.frame0, 
                                     text='__DataSet List__',font=helv15 ).grid(row = 18, rowspan=2,
                                                                        column=10, columnspan=6,
                                                                        sticky='nsew', padx=5, pady=5)
        # self.label_dummy2 = tk.Label(self.frame0, 
        #                              text='DataSet Content',font=helv15 ).grid(row = 18, rowspan=2,
        #                                                                        column=20, columnspan=4,
        #                                                                        sticky='w', padx=5, pady=5)
        
        
        self.listbox31 = tk.Listbox(self.frame0, font=helv15,
                                    selectmode='single',relief="sunken",
                                    height=13, width=30)
        self.listbox31.insert(1, 'Database not selected.')
        self.listbox31.bind('<<ListboxSelect>>', self.on_list)
        self.scrollbar31 = ttk.Scrollbar(self.frame0,
                                          orient='vertical',
                                          command=self.listbox31.yview)
        self.listbox31['yscrollcommand'] = self.scrollbar31.set
        
        self.listbox31.grid(in_=self.frame0, 
                            row=20, column=10,
                            columnspan=6, padx=(5, 0), pady=5, 
                            sticky='nsew')
        self.scrollbar31.grid(in_=self.frame0, 
                              row=20, column=15,
                              columnspan=2,  pady=5, 
                              sticky='ns')
        
        
        style = ttk.Style()
        # style.element_create("Custom.Treeheading.border", "from", "default")
        style.layout("Custom.Treeview.Heading", [
            ("Custom.Treeheading.cell", {'sticky': 'nswe'}),
            ("Custom.Treeheading.border", {'sticky':'nswe', 'children': [
                ("Custom.Treeheading.padding", {'sticky':'nswe', 'children': [
                    ("Custom.Treeheading.image", {'side':'right', 'sticky':''}),
                    ("Custom.Treeheading.text", {'sticky':'we'})
                ]})
            ]}),
        ])
        style.configure("Custom.Treeview.Heading",
            background="gray76", foreground="black", relief="raised")
        style.map("Custom.Treeview.Heading",
            relief=[('active','raised'),('pressed','raised')])
        
        style.configure("Custom.Treeview", highlightthickness=0, bd=0, font=('Helvetica', 15,'bold')) # Modify the font of the body
        style.configure("Custom.Treeview.Heading", font=('Helvetica', 15,'bold'))
        
        self.table = ttk.Treeview(self.frame0, show=['headings'], height='16', selectmode='browse', style='Custom.Treeview')
        self.table.grid(in_=self.frame0,row=20,column=17,columnspan=10, sticky='nsew')
        
        self.vsb = ttk.Scrollbar(self.frame0, orient="vertical", command=self.table.yview)
        self.vsb.grid(in_=self.frame0,row=20,rowspan=20, column=27,columnspan=2, sticky='ns')
        self.table.configure(yscrollcommand=self.vsb.set)
        
        self.table["columns"]=("DataSet_Content")
        self.table.column("DataSet_Content", stretch=tk.YES, anchor="w")
        self.table.heading("DataSet_Content", text="DataSet Content")
        
        
        
        
        
        
        # self.table["columns"]=("first","second",'third','fourth','fifth','sixth','seventh')

        # self.table.column("first", width=50, minwidth=50,  stretch=tk.NO,anchor="center")
        # self.table.column('second', width=50, minwidth=50,  stretch=tk.NO,anchor="center")
        # self.table.column("third", width=50, minwidth=50,   stretch=tk.NO,anchor="center")
        # self.table.column("fourth", width=50, minwidth=50,  stretch=tk.NO,anchor="center")
        # self.table.column("fifth",width=50, minwidth=50,  stretch=tk.NO,anchor="center")
        # self.table.column("sixth",width=50, minwidth=50,  stretch=tk.NO,anchor="center")
        # self.table.column("seventh",width=50, minwidth=50,  stretch=tk.NO,anchor="center")

        # self.table.heading("first", text="1st")
        # self.table.heading('second', text="2nd")
        # self.table.heading("third", text="3rd")
        # self.table.heading("fourth", text="4th")
        # self.table.heading("fifth", text="5th")
        # self.table.heading("sixth", text="Temp.")
        # self.table.heading("seventh", text="Weight")
        
        self.table.bind('<<TreeviewSelect>>', self.treeview_on_selection)
        
        
        self.button_close = HoverButton(self.frame0, text="Close", width=10, font=LARGE_FONT, 
                           activebackground='Silver', 
                           command = lambda: controller.show_frame(MainMenu)) 
        self.button_close.grid(row = 45, rowspan=2, column=24, columnspan=4, sticky='nsew', padx=5, pady=5)
        
        self.bind('<<ShowFrame>>', self.on_show_frame)
    
        def selectdatafolder(self):
            
            print('folder selection')
            
            
            self.folder_selected = filedialog.askdirectory(initialdir = "C:\\Users\\otosanvs\\Desktop\\Arcelik\\AuditTracker\\Data",title = "Choose Your Folder",)
            self.folder_path.set(self.folder_selected)
            
           
            
        def import_csv_data(self):
            
            part_db = selected_part['part_db']
            part_data = basics.read_db(part_db)  
            
            part_data['data']={}
            
            basics.write_db(part_db, part_data['data'],'data')
            
            files_path = self.folder_selected
            files_path = files_path.replace("/",'\\')

            read_files = glob.glob(os.path.join(files_path,"*.csv"))
        
            for files in read_files:
                test_data=pd.read_csv(files,
                                      encoding = "ISO-8859-1",
                                      header=None,
                                      index_col=[0],
                                      low_memory=False)
                
                test_data_store.append(test_data)
                
                # Writing updated data array into database
                filename = files.split('\\',8)[-1]
                part_data['data'][filename] = {}
                basics.write_db(part_db, part_data['data'][filename],'data',filename)
                
                part_data['time_index'] = []
                part_data['time_index'] = (test_data.index.to_numpy()[1:]).astype(float)
                basics.write_db(part_db, part_data['time_index'],'time_index')
                
                # Applying FFT
                # Number of sample points
                N = len((test_data.index.to_numpy()[1:]).astype(float))
                sampling_rate = 1.0 /((test_data.index.to_numpy()[2:3]).astype(float)-(test_data.index.to_numpy()[1:2]).astype(float))
                # sample spacing
                T = 1.0 / sampling_rate

                part_data['freq_index'] = []
                part_data['freq_index'] = np.linspace(0.0, 1.0/(2.0*T), N//2)
                basics.write_db(part_db, part_data['freq_index'],'freq_index')
                
                columns = test_data.iloc[0]
                i=0
                for column in columns:
                    part_data['data'][filename][column] = {}
                    basics.write_db(part_db, part_data['data'][filename][column],'data',filename,column)
                    # breakpoint()
         
                    part_data['data'][filename][column]['time_data'] =  []
                    part_data['data'][filename][column]['time_data'] = (test_data.to_numpy()[1:,i]).astype(float)
                    basics.write_db(part_db, part_data['data'][filename][column]['time_data'],'data',filename,column,'time_data')
                        
                    part_data['data'][filename][column]['freq_data'] = []
                    part_data['data'][filename][column]['freq_data'] = scipy.fftpack.fft((test_data.to_numpy()[1:,i]).astype(float))[:N//2]
                    basics.write_db(part_db, part_data['data'][filename][column]['freq_data'],'data',filename,column,'freq_data')
                    
                    i+=1
                    
            
                print(files.split('\\',8)[-1])
                self.Status.set(files.split('AuditTracker',3)[-1])
                self.Status_cond.set('Importing...')
               
                root.update()
            self.Status_cond.set('Import Completed')
            
      # Choosing default database when page is shown
    def on_show_frame(self, event):
        remember['current_page'] = 'Choose Part'
        # self.main_label_text.set(remember['current_page'])

        remember['index_db'] = 'Database/DB_Index.lsdb'

        self.listbox31.delete(0, 'end')

        if not os.path.isfile(remember['index_db']):
            # This block is executed if database index file is not found
            if not os.path.exists(remember['db_folder']):
                # Database directory is created if not found:
                os.makedirs(remember['db_folder'])
            basics.create_index_db(self)
        
        self.remember = remember
        
        basics.fill_listbox(self) 
        
    def update_listbox(self):
        remember['current_page'] = 'Choose Part'
        
    
        remember['index_db'] = 'Database/DB_Index.lsdb'
    
        self.Datasetname.set('')
        self.text_Description.set('')
    
        self.listbox31.delete(0, 'end')
    
        if not os.path.isfile(remember['index_db']):
            # This block is executed if database index file is not found
            if not os.path.exists(remember['db_folder']):
                # Database directory is created if not found:
                os.makedirs(remember['db_folder'])
            basics.create_index_db(self)
    
        self.remember = remember
    
        basics.fill_listbox(self)    
        
        
    def treeview_on_selection():
        print('treeview_on_selection')
        
    def on_list(self,event):
        print("on_list active") 
        
        if remember['current_page'] == 'Choose Part':
            _widget = event.widget
            _index = int(_widget.curselection()[0])
            print(_index)
            _selection = _widget.get(_index)
            _selection = _selection.split()[0]
            print(_selection)

            if _selection != 'Database not selected.':

                selected_part = remember['initial_selected_part']
                selected_part['LSID'] = _selection

                empty = 'not defined'
                selected_part['DatsSetName'] = empty
                selected_part['CreationDate'] = empty
                selected_part['Description'] = empty


                lsid = selected_part['LSID']            
                metadata = basics.read_db(remember['index_db'],
                          lsid,
                          'metadata')

                self.Datasetname.set(metadata['DataSetName'])
                self.text_Description.delete(1.0, 'end')
                self.text_Description.insert(END,metadata['Description'])
                
                
                # Show files imported files with this database
                part_db =  remember['db_folder'] + selected_part['LSID'] + remember['db_extension']
                part_data = basics.read_db(part_db)

                if 'data' in part_data.keys():
                    
                    for i in self.table.get_children():
                        self.table.delete(i)
                    
                    for filenames in  part_data['data'].keys():
                        self.table.insert('', 'end',  values= filenames)
                        
                else:
                    for i in self.table.get_children():
                        self.table.delete(i)

        
        
        

class PlotPage(tk.Frame):
    """ Page for displaying and analyzing previously collected data. """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.page_name = 'Plot Page'

 #   Defining LabelFrames
        self.frame1 = ttk.LabelFrame(self, text='Main Controls')
        self.frame2 = ttk.LabelFrame(self, text='Chart')

        self.frame1.grid(
            row=0, column=0,
            sticky='nsew',
            padx=5, pady=5)
        self.frame2.grid(
            row=0, column=1,columnspan=2,
            sticky='nsew', 
            padx=5, pady=5)
        
        
        """ Frame 1 - main control """
        
        self.button_data_select = tk.Button(self.frame1, text='Import_CSV_Data',
                                            command=lambda: [import_csv_data(self),plot_analysis()])
        self.button_data_select.grid(row=0,rowspan=2,column=0,columnspan=2, sticky='nsew', padx=5, pady=5)  
        self.data_file = tk.StringVar()
        self.label_data_select = tk.Label(self.frame1,textvariable=self.data_file)
        self.label_data_select.grid(row=0, rowspan=2, column=2, columnspan=2,sticky='nsew', padx=5, pady=5)
                                                                 
        self.label_calc_method = tk.Label(self.frame1,text='Calculation Method:').grid( row=2, rowspan=2,column=0, columnspan=2,sticky='w', padx=5, pady=5)
        
        self.method = tk.StringVar()
        self.calc_method = ttk.Combobox(self.frame1, textvariable=self.method, width=15)
        self.calc_method.grid(row=2, rowspan=2,column=2, columnspan=2,sticky='nsew', padx=5, pady=5)                                                                       
        
        self.label_analysis_range = tk.Label(self.frame1, text='Frequency Range:').grid(row = 4,rowspan=2, column=0, columnspan=2,sticky='w', padx=5, pady=5)
        self.min_freq = tk.StringVar()
        self.entry_min_freq = ttk.Entry(self.frame1,textvariable=self.min_freq,state='normal',width=10).grid(row = 4,rowspan=2, column=2, columnspan=1,sticky='nsew', padx=5, pady=5)
        self.max_freq = tk.StringVar()
        self.entry_max_freq = ttk.Entry(self.frame1,textvariable=self.max_freq,state='normal',width=10).grid(row = 4,rowspan=2, column=3, columnspan=1,sticky='nsew', padx=5, pady=5)
        
        self.calculate_button = tk.Button(self.frame1, text='Calculate').grid( row=6, rowspan=2,column=0,columnspan=4,sticky='nsew', padx=5, pady=5)
        
        
        self.calc_method['values'] = choices['calculation_method']
        self.calc_method.current(0)
        
            # Matplotlib Figure is defined
        self.fig = plt.Figure(figsize=(10.5,6.7), dpi=100)
        
        self.fig.subplots_adjust(left=0.06, 
                                  bottom=0.04,
                                  right=0.99,
                                  top=0.98,
                                  wspace=0.2,
                                  hspace=0.2)
        
        self.ax1 = self.fig.add_subplot(321)
        self.ax2 = self.fig.add_subplot(322)
        self.ax3 = self.fig.add_subplot(323)
        self.ax4 = self.fig.add_subplot(324)
        self.ax5 = self.fig.add_subplot(325)
        self.ax6 = self.fig.add_subplot(326)
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame2)
        toolbar = NavigationToolbar2Tk(self.canvas, self.frame2)
        self.canvas.get_tk_widget().pack()
        self.canvas._tkcanvas.pack(side = TOP, fill= BOTH, expand = True)
        
        
        
    
 
        
        
        def clear_plot_axes(self):
            for item in self.plots1:
                item.cla()        
        
        def import_csv_data(self):
            
            files_path= r"C:\measurement_data"
            read_files = glob.glob(os.path.join(files_path,"*.csv"))
            
            
            for files in read_files:
                test_data=pd.read_csv(files,
                                      encoding = "ISO-8859-1",
                                      header=None,
                                      index_col=[0],
                                      low_memory=False)
                
                test_data_store.append(test_data)
                self.data_file.set(files.split('data',1)[-1])
                root.update()
                
                # Original Data Set
                time_data = (test_data.index.to_numpy()[1:]).astype(float)
                mic_data = (test_data.to_numpy()[1:,0]).astype(float)
                acc_data = (test_data.to_numpy()[1:,1]).astype(float)
                
                time_data_store.append(time_data)
                acc_data_store.append(acc_data)
                mic_data_store.append(mic_data)
                
                # Filtered Data Set
                filtered_acc_data = lowpass(acc_data,sampling_rate,low)
                filtered_mic_data = lowpass(mic_data,sampling_rate,low)
                
                filt_acc_data_store.append(filtered_acc_data)
                filt_mic_data_store.append(filtered_mic_data)
                
                # Applying FFT
                # Number of sample points
                N = 500000
                # sample spacing
                T = 1.0 / 50000
                x = np.linspace(0, N*T, N)
                xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
                
                yf_1 = scipy.fftpack.fft(acc_data)
                yf_2 = scipy.fftpack.fft(filtered_acc_data)
                
                yf_3 = scipy.fftpack.fft(mic_data)
                yf_4 = scipy.fftpack.fft(filtered_mic_data)
                
                acc_fft_data_store.append(yf_1)
                filt_acc_fft_data_store.append(yf_2)
                
                mic_fft_data_store.append(yf_3)
                filt_mic_fft_data_store.append(yf_4)
                
                
                
                # Energy Calculation 
                power_1 = np.square(acc_data)
                power_2 = np.square(filtered_acc_data)
                
                power_3 = np.square(mic_data)
                power_4 = np.square(filtered_mic_data)
                
                power_sum_value_1 = np.sum(power_1)
                power_sum_value_2 = np.sum(power_2)  
                
                power_sum_value_3 = np.sum(power_3)
                power_sum_value_4 = np.sum(power_4) 
                
                powersum_acc_data_store.append(power_sum_value_1)
                filt_powersum_acc_data_store.append(power_sum_value_2 )
                
                powersum_mic_data_store.append(power_sum_value_3)
                filt_powersum_mic_data_store.append(power_sum_value_4 )

                
        def plot_analysis():
            
            # Number of sample points
            N = 500000
            # sample spacing
            T = 1.0 / 50000
            
            t=np.linspace(1, (len(powersum_acc_data_store)), (len(powersum_acc_data_store)))
                    
            
            self.ax1.plot(time_data_store[5],acc_data_store[5], color='red')
            self.ax1.plot(time_data_store[7],mic_data_store[7], color='blue')
            # self.ax1.plot(time_data_store[9],acc_data_store[9], color='black')
            self.ax3.plot(np.linspace(0.0, 1.0/(2.0*T), N//2),2.0/N * np.abs(acc_fft_data_store[5][0:N//2]),color='red')
            self.ax3.plot(np.linspace(0.0, 1.0/(2.0*T), N//2),2.0/N * np.abs(mic_fft_data_store[5][0:N//2]),color='blue')
            # self.ax2.plot(np.linspace(0.0, 1.0/(2.0*T), N//2),2.0/N * np.abs(acc_fft_data_store[9][0:N//2]),color='black')
            self.ax5.plot(t,powersum_acc_data_store,'o',color='blue')
            # self.ax3.set_ylim([1500,40000])
            
            NOK =[1,2,3,4,5,6,16,17,18,19,20,21,28,29,30,31,32,33,41,42,43,47,48,49,53,54,55,62,63,64,68,69,70,74,75,76 ]
            for i in t:
                if i in NOK:
                    self.ax5.annotate(int(i), (int(i), powersum_acc_data_store[int(i)-1]), xytext=(int(i), powersum_acc_data_store[int(i)-1]), 
                                arrowprops=dict(facecolor='red', shrink=0.1))
                else:
                    self.ax5.annotate(int(i), (int(i), powersum_acc_data_store[int(i)-1]))  
            
            self.canvas.draw()
            
            

        def lowpass(time_data, sampling_rate, low):
            """ Applies lowpass filter on time_data and returns filtered signal. """
        
            nyquist = sampling_rate / 2
            bess_b,bess_a = scipy.signal.iirfilter(5,
                        Wn=[low/nyquist],
                        btype="lowpass", ftype='bessel' )
            filtered_data = scipy.signal.filtfilt(bess_b, bess_a, time_data)
        
            return filtered_data
                                                                    
        
        
    
if __name__ == '__main__':
    root = AuditTracker()
    root.attributes('-topmost', True)
    # root.overrideredirect(True)
    root.resizable(True, True)
    fullScreenState = False
    root.attributes("-fullscreen", fullScreenState)
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d" % (w, h))
    root.mainloop()