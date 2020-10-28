"""
Setting default parameters into Parameter Database file
"""

import datetime
import audittracker_basics as basics
from audittracker_basics import write_db, create_db, read_db


if __name__ == '__main__':

    DATABASE_FOLDER = 'Database/'
    param_db = 'audittracker_Parameters.lsp'

    #   Setting default DAQ parameters
    default_settings = {}
    default_choices = {}
    default_files = {}

    default_files['index_db'] = DATABASE_FOLDER + 'DB_Index.lsdb'
    default_files['db_folder'] = DATABASE_FOLDER
    default_files['db_extension'] = '.lsdb'
    default_files['param_db'] = param_db
    
    
    # default_settings['sampling_rate'] = 16384
    # default_settings['samples_to_read'] = 16384
    # default_settings['resolution'] = 1.0
    # default_settings['excitation_type'] = 'Chirp'
    # default_settings['excitation_level'] = 1
    # default_settings['excitation_freq_min'] = 200
    # default_settings['excitation_freq_max'] = 8000
    # default_settings['excitation_duration'] = 100
    # default_settings['chan_ai_ref_mode'] = 'AC'
    # default_settings['chan_ai_res_mode'] = 'ICP'
    # default_settings['chan_ai_add_mode'] = 'AC'
    # default_settings['chan_ai_ref_sens'] = 1
    # default_settings['chan_ai_res_sens'] = 1
    # default_settings['di_trigger_delay'] = 0.5

    # default_settings['run_averages'] = 3
    # default_settings['calculation_method'] = 'LSQ-3'
    # default_settings['save_ref_time'] = True
    # default_settings['save_res_time'] = True
    # default_settings['save_additional_channel'] = False
    # default_settings['fft_or_psd'] = 1
    # default_settings['psd_res'] = '8'
    # default_settings['analysis_freq'] = [(200, 10000)]
    # default_settings['threshold'] = 10
    # default_settings['ref_signal_choice'] = 'Primary'
    # default_settings['res_signal_choice'] = 'Primary'

    # default_choices['analog_input_mode'] = ('ICP', 'AC', 'DC')
    # default_choices['bandwidth'] = (
    #         '3200',
    #         '4096',
    #         '6400',
    #         '8192',
    #         '12800',
    #         '16384',
    #         '25600')
    # default_choices['resolution'] = ('0.5', '1', '2', '4',
    #                                  '8', '16', '32', '64')
    # default_choices['calculation_method'] = ('LSQ-3', 'LSQ-4', 'LSQ-5',
    #                                          'LSQ-6', 'LSQ-3m', 'LSQ-6m',
    #                                          'LSQ-7', 'LSQ-8')
    # default_choices['psd_res'] = ('2', '4', '8', '16', '32', '64')
    # default_choices['excitation_type'] = ('Chirp', 'Random')
    # default_choices['ref_signal_choice'] = (
    #         'Primary', 'Secondary', 'Virtual', 'FFT')
    # default_choices['export_format'] = ('.mat', '.csv', '.xlsx')

    param_data = {}
    param_data['settings'] = {}           # Initializing session settings
    param_data['default_settings'] = default_settings
    param_data['default_choices'] = default_choices
    param_data['default_files'] = default_files

    create_db(param_db)
    write_db(param_db, param_data)


def enable_edit(settings_frame):
    " Enables editting settings by switching widget states to normal. "

    for item in settings_frame.winfo_children():
        item['state'] = 'normal'


def disable_edit(settings_frame):
    " Enables editting settings by switching widget states to disabled. "

    for item in settings_frame.winfo_children():
        item['state'] = 'disabled'


def import_settings(self,
                    selected_part,
                    param_db='LS_Beta_Parameters.lsp',
                    use_defaults=True):
    """
    Importing default settings or selected_part settings from database and
    implementing them as current settings.
    """

    #disable_edit(self.frame2)

    if use_defaults or selected_part['settings'] == 'use_defaults':
        # Gets default settings

        # self.settings_mode.set(1)

        settings = read_db(param_db, 'default_settings')

    else:
        # Gets previously defined part settings
        settings = selected_part['settings']
        # self.settings_mode.set(2)

    self.chan_ai_ref_mode.set(settings['chan_ai_ref_mode'])
    self.chan_ai_res_mode.set(settings['chan_ai_res_mode'])
    # self.chan_ai_add_mode.set(settings['chan_ai_add_mode'])
    self.chan_ai_ref_sens.set(str(settings['chan_ai_ref_sens']))
    self.chan_ai_res_sens.set(str(settings['chan_ai_res_sens']))
    # self.di_trigger_delay.set(str(settings['di_trigger_delay']))
    self.bandwidth.set(int(settings['sampling_rate'] / 2))
    self.resolution.set(settings['resolution'])
    self.acquisition_period.set(str(1/settings['resolution']))
    self.excitation_type.set(settings['excitation_type'])
    self.excitation_level.set(settings['excitation_level'])
    self.excitation_freq_min.set(settings['excitation_freq_min'])
    self.excitation_freq_max.set(settings['excitation_freq_max'])
    self.excitation_duration.set(settings['excitation_duration'])
    self.run_averages.set(str(settings['run_averages']))
    # self.save_ref_time.set(settings['save_ref_time'])
    # self.save_res_time.set(settings['save_res_time'])
    # self.save_additional_channel.set(settings['save_additional_channel'])


def get_settings(self, selected_part):
    " Gets settings on page and returns them as a dictionary. "

    settings = selected_part['settings']
    
    # Calculating necessary parameters
    resolution = float(self.resolution.get())
    sampling_rate = int(self.sampling_rate)
    acquisition_period = 1 / resolution
    samples_to_read = int(acquisition_period * sampling_rate)
    # targets = [self.entry40.get(), self.entry41.get(), self.entry42.get(), self.entry43.get(), self.entry44.get(),self.entry45.get()]


    # Basic DAQ parameters
    settings['sampling_rate'] = sampling_rate
    settings['resolution'] = resolution
    settings['acquisition_period'] = acquisition_period
    settings['samples_to_read'] = samples_to_read
    

    # Channel setup
    settings['chan_ai_ref'] = 'Dev7/ai0'
    settings['chan_ai_res'] = 'Dev7/ai1'
    settings['chan_ao'] = 'Dev7/ao0'
    settings['chan_ai_ref'] = self.chan_ai_ref.get()
    settings['chan_ai_res'] = self.chan_ai_res.get()
    settings['chan_ao'] = self.chan_ao.get()
    settings['chan_ai_ref_mode'] = self.chan_ai_ref_mode.get()
    settings['chan_ai_res_mode'] = self.chan_ai_res_mode.get()
    settings['chan_ai_ref_sens'] = float(self.chan_ai_ref_sens.get())
    settings['chan_ai_res_sens'] = float(self.chan_ai_res_sens.get())
    # settings['save_additional_channel'] = self.save_additional_channel.get()
    # settings['chan_ai_additional'] = self.chan_ai_additional.get()

    # Triggering settings
    # settings['chan_di_trigger'] = self.chan_di_trigger.get()
    # settings['di_trigger_delay'] = float(self.di_trigger_delay.get())

    # Excitation parameters
    settings['excitation_type'] = self.excitation_type.get()
    settings['excitation_level'] = float(self.excitation_level.get())
    settings['excitation_freq_min'] = \
        int(self.excitation_freq_min.get())
    settings['excitation_freq_max'] = \
        int(self.excitation_freq_max.get())
    settings['excitation_duration'] = int(self.excitation_duration.get())

    settings['run_averages'] = int(self.run_averages.get())
    # settings['save_ref_time'] = self.save_ref_time.get()
    # settings['save_res_time'] = self.save_res_time.get()

    return settings


def get_and_save_settings(self, selected_part, index_db):
    """
    Gets selected settings from page and saves them
    into part and index databases.
    """
    
    selected_part['settings'] = get_settings(self, selected_part)
    


    write_db(selected_part['part_db'],
             selected_part['settings'],
             'settings',
             )

    write_db(index_db,
             selected_part['settings'],
             selected_part['LSID'],
             'settings',
             )


def get_and_set_as_default(self, param_db, selected_part):
    """ Gets current settings and sets them as default settings. """

    settings = get_settings(self, selected_part)
    default_settings = read_db(param_db, 'default_settings')

    for key in default_settings.keys():
        default_settings[key] = settings[key]

    write_db(param_db, default_settings, 'default_settings')


def save_part(self,remember):
    "Saves a newly defined part."
    
    selected_part = remember['initial_selected_part']
    
    empty = 'not defined'
    selected_part['LSID'] = empty
    selected_part['DataSetName'] = empty
    selected_part['CreationDate'] = empty
    selected_part['Description'] = empty

    # selected_part = self.selected_part
    # remember = self.remember
    
    # Initializing NewPart metadata
    new_part = {}

    #   Getting current date and time
    now = datetime.datetime.now()

    #   Assigning new LSID to new part
    if remember['Parts'] == []:
        new_part['LSID'] = 'FO100001'
    else:
        last_LSID = max(list(remember['Parts']))
        head = last_LSID.rstrip('0123456789')
        tail = int(last_LSID[len(head):])
        tail = str(tail + 1)
        new_part['LSID'] = head + tail

    #   Getting strings from entry fields
    new_part['DataSetName'] = self.Datasetname.get()
    new_part['CreationDate'] = now.strftime('%Y-%m-%d %H:%M')
    new_part['Description'] = self.text_Description.get("1.0","end")
    
    #   Writing into index database file
    write_db(remember['index_db'],
             {},
             new_part['LSID'],
             )
    write_db(remember['index_db'],
             new_part,
             new_part['LSID'],
             'metadata',
             )

    #   Assigning NewPart metadata to selected_part
    selected_part['LSID'] = new_part['LSID']
    selected_part['DataSetName'] = new_part['DataSetName']
    selected_part['CreationDate'] = new_part['CreationDate']
    selected_part['Description'] = new_part['Description']
  
    selected_part['part_db'] = \
        remember['db_folder'] \
        + selected_part['LSID']\
        + remember['db_extension']
    
    #   Creating a part database file
    create_db(selected_part['part_db'])
    write_db(selected_part['part_db'],
             new_part,
             'metadata')
    
    basics.fill_listbox(self)
    # Changes the status label on the GUI
    # self.status_label_text.set('New DataSet is created.')
    print('New part created.')

def save_changes(self):
    """
    Saving part metadata changes into database
    ('Save Changes' button)
    """

    selected_part = self.selected_part
    remember = self.remember

    #   Getting strings from entry fields
    selected_part['PartName'] = self.PartName.get()
    selected_part['PartNumber'] = self.PartNumber.get()
    selected_part['Description'] = str(self.label426.get())
    selected_part['Targets'] = [self.entry40.get(),self.entry41.get(),self.entry42.get(),
                           self.entry43.get(),self.entry44.get(),self.entry45.get()]

    #   Writing into index database file
    write_db(remember['index_db'],
             selected_part['PartName'],
             selected_part['LSID'],
             'metadata',
             'PartName',
             )
    write_db(remember['index_db'],
             selected_part['PartNumber'],
             selected_part['LSID'],
             'metadata',
             'PartNumber',
             )
    write_db(remember['index_db'],
             selected_part['Description'],
             selected_part['LSID'],
             'metadata',
             'Description',
             )
    write_db(remember['index_db'],
             selected_part['Targets'],
             selected_part['LSID'],
             'metadata',
             'Targets',
             )

    #   Writing into part database file
    write_db(selected_part['part_db'],
             selected_part['PartName'],
             'metadata',
             'PartName',
             )
    write_db(selected_part['part_db'],
             selected_part['PartNumber'],
             'metadata',
             'PartNumber',
             )
    write_db(selected_part['part_db'],
             selected_part['Description'],
             'metadata',
             'Description',
             )
    write_db(selected_part['part_db'],
             selected_part['Targets'],
             'metadata',
             'Targets',
             )

    # Changes the status label on the GUI
    # self.status_label_text.set('Changes saved.')