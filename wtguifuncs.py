""" Functions to execute GUI commands. """

import os
import logging
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
# import wtbasics as bf
# import wtdaq as daq
# import wtsettings
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

logger = logging.getLogger(__name__)


def save_description(self, log_modification=False):
    # Updates description (called from PlotPage pages)
    self.selected_part['description'] = self.text_description.get(
        '1.0', 'end-1c')
    if log_modification:
        description = self.selected_part['description']
        sample_no = self.sample_count.get()
        modification = self.modification
        new_line = f"{sample_no}:{modification}"
        description += f"/n{new_line}"
    bf.write_db(
        self.selected_part['index_db'],
        self.selected_part['description'],
        self.selected_part['wtid'],
        'metadata',
        'description', )
    logger.info('Part description updated: \n{}'.format(
        self.selected_part['description']))


def listen_modifications(self):
    """ Listens for modifications in stamping parameters
        through digital input channels. """

    digital_modifications = ('mod1', 'mod2', 'mod3', 'mod4')
    settings = self.selected_part['daq_settings']
    for mod in digital_modifications:
        if settings[mod + '_active']:
            modified = daq.digital_listen(settings[mod + '_chan'])
            self.mod_name = settings[mod + '_name']
            relearn = settings[mod + '_init']
            if modified and getattr(self, mod) is False:
                self.status_label2_text.set(
                    f"""Sample {self.sample_count.get()}: {self.mod_name}. Re-learn: {relearn}""")
                self.status_label2.configure(
                    foreground='white', background='black')
                update_description(
                    self, self.sample_count.get(), self.mod_name, )
                logger.info(
                    f"{self.mod_name} on sample {self.sample_count.get()}")
                if relearn == 'True':
                    bf.clear_ref_data(self)
                    logger.info(
                        f"Re-learning on sample {self.sample_count.get()}")
            setattr(self, mod, modified)


def init_modifications(self):
    """ Initializes modifications after a sample is measured. """

    digital_modifications = ('mod1', 'mod2', 'mod3', 'mod4')
    for mod in digital_modifications:
        setattr(self, mod, False)


def update_description(self, sample_no, event):
    """ Updates part description with respect to detected modifications. """
    self.text_description.insert('end', f"\n{sample_no}: {event}")
    save_description(self)


def init_selected_part(param_db):
    selected_part = {}      # Initializing selected part information
    selected_part['param_db'] = param_db
    selected_part['time_stamp'] = lambda: datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S')

    # Setting default DAQ parameters
    daq_settings = bf.read_db(param_db, 'default_daq_settings')
    settings = bf.read_db(param_db, 'default_settings')
    choices = bf.read_db(param_db, 'default_choices')
    selected_part.update(bf.read_db(param_db, 'default_files'))

    for key in settings['metadata_keys']:
        selected_part[key] = ''

    selected_part['wtid'] = 'defaults'
    selected_part['settings'] = settings

    return selected_part, settings, daq_settings, choices


def create_secondary_label(selected_part):
    wtid = selected_part['wtid']
    part_number = selected_part['part_number']
    return wtid + ' - ' + part_number

# Functions from StartPage:


def filter_listbox(self, parts, listbox):

    filtered_parts = []
    display_options = [False, False, False]

    if self.display_wtid_option.get():
        display_options[0] = True
    if self.display_part_name_option.get():
        display_options[1] = True
    if self.display_part_no_option.get():
        display_options[2] = True

    for part in parts:
        listentry = ''
        display_data = [part,
                        parts[part]['metadata']['part_name'],
                        parts[part]['metadata']['part_number']]

        for n, option in enumerate(display_options):
            if option:
                if listentry != '':
                    listentry += ' - '
                listentry += display_data[n]

        filtered_parts.append(listentry)
        listbox.insert(0, listentry)

    logger.debug('Listbox filtered: {}'.format(display_options))

    return filtered_parts


def search_in_db(self, search_term):
    '''
    Filtering items in listbox with the search_term written in Search Entry.
    '''
    search_term = search_term.get()
    self.listbox_parts.delete(0, 'end')
    for part in self.parts_filtered:
        if search_term.upper() in part.upper():
            self.listbox_parts.insert('end', part)


def fill_listbox(self):
    """ Fills the parts listbox to display the parts stored in
        db directory. """

    selected_part = self.selected_part
    self.listbox_parts.delete(0, 'end')

    parts = bf.read_db(self.index_db_path)

    #   Storing part WTIDs for session
    selected_part['db_folder'] = self.db_directory.get()
    selected_part['index_db'] = self.index_db_path
    selected_part['parts'] = list(parts.keys())
    selected_part['parts'].sort(reverse=True)
    self.parts_filtered = filter_listbox(self, parts, self.listbox_parts)


def load_file(self):
    ''' Reads parts in database and fills the listbox.
        Called by 'Browse' button. '''

    dir_path = askdirectory() + '/'

    self.db_directory.set(dir_path)
    self.index_db_path = dir_path + 'index_db.idx'
    logger.info(f'Index db path set to: {self.index_db_path}')

    if os.path.isfile(self.index_db_path):
        fill_listbox(self)
    else:
        bf.create_index_db(self)
        fill_listbox(self)


def get_part_metadata(self, set_lsid=True):
    """ Gets part metadata and settings from part_db/index_db
        and insert values into selected_part object. """

    selected_part = self.selected_part
    wtid = selected_part['wtid']
    if set_lsid:
        self.wtid.set(wtid)
    selected_part['part_db'] = selected_part['db_folder'] + wtid + '/'

    stored_data = bf.read_db(selected_part['index_db'], selected_part['wtid'])

    for key, value in stored_data['metadata'].items():
        selected_part[key] = value

    if 'settings' in stored_data.keys():
        selected_part['settings'] = stored_data['settings']

    if 'sample_count' in stored_data.keys():
        selected_part['sample_count'] = stored_data['sample_count']
    else:
        selected_part['sample_count'] = 0


def store_metadata(selected_part):
    """ Stores a copy of part metadata in part_db directory. """

    metadata = {}
    for key in (
        'daq_settings',
        'wtid',
        'part_name',
        'part_number',
        'creation_date',
        'description', ):
        metadata[key] = selected_part[key]

    file_name = selected_part['part_db'] +\
        selected_part['wtid'] + '_ref_data.lsdb'
    bf.write_db(file_name, metadata)

# PartPage related functions: ######


def format_canvas(self):
    """ Creates tabs and canvases on PlotPage. """

    # Matplotlib Figure is defined
    self.fig1 = Figure(figsize=(10, 5), dpi=100)
    self.fig2 = Figure(figsize=(10, 5), dpi=100)

    # Tabs are defined
    self.tabs = ttk.Notebook(self.frame2)
    self.tab1 = ttk.Frame(self.tabs)
    self.tab2 = ttk.Frame(self.tabs)
    self.tabs.add(self.tab1, text='WTR Analysis', sticky='nsew')
    self.tabs.add(self.tab2, text='Run Details')

    self.tabs.bind('<<NotebookTabChanged>>', self.on_tab_change)

    # Canvas 1 is defined
    self.canvas1 = FigureCanvasTkAgg(self.fig1, self.tab1)
    self.canvas1.draw()
    self.canvas1.get_tk_widget().pack(
        in_=self.tab1,
        side=tk.TOP,
        fill=tk.BOTH,
        expand=True, )

    # Navigation toolbar for the plots
    self.toolbar1 = NavigationToolbar2Tk(self.canvas1, self.tab1)
    self.toolbar1.update()
    self.canvas1._tkcanvas.pack(
        in_=self.tab1,
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True, )

    # Canvas 2 is defined
    self.canvas2 = FigureCanvasTkAgg(self.fig2, self.tab2)
    self.canvas2.draw()
    self.canvas2.get_tk_widget().pack(
        in_=self.tab2,
        side=tk.TOP,
        fill=tk.BOTH,
        expand=True, )

    # Navigation toolbar for the plots
    self.toolbar2 = NavigationToolbar2Tk(self.canvas2, self.tab2)
    self.toolbar2.update()
    self.canvas2._tkcanvas.pack(
        in_=self.tab2,
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True, )

    # The defined tabs are placed & displayed using pack layout manager
    self.tabs.pack(fill='both', expand=True)


def format_chart_area(self):
    """
    Clearing chart area and adjusting subplot orientations.
    """

    # Clearing figure
    self.fig1.clf()

    if self.page_name == 'Check Part':
        # Adding subplots with the desired layout

        n_rows, n_cols = 5, 3
        gs1 = GridSpec(n_rows, n_cols, )
        gs2 = GridSpec(n_rows, n_cols, top=0.8, hspace=0)
        gs3 = GridSpec(n_rows, n_cols, )

        self.plot_spec = self.fig1.add_subplot(gs1[0:3, 0:2])
        self.plot_time = self.fig1.add_subplot(gs2[3, 0:2])
        self.plot_time2 = self.fig1.add_subplot(
            gs2[4, 0:2], sharex=self.plot_time, sharey=self.plot_time)
        self.plot_wtr = self.fig1.add_subplot(gs3[:, 2])

        self.plots = [self.plot_time, self.plot_time2]

    elif self.page_name == 'Review Part':
        # Adding subplots with the desired layout

        n_rows, n_cols = 2, 3
        gs1 = GridSpec(n_rows, n_cols, )
        gs2 = GridSpec(n_rows, n_cols, top=0.8, hspace=0)
        gs3 = GridSpec(n_rows, n_cols, )

        self.plot_spec = self.fig1.add_subplot(gs1[0, 0:2])
        self.plot_time = self.fig1.add_subplot(gs2[1, 0:2])
        self.plot_wtr = self.fig1.add_subplot(gs3[:, 2])

        self.plots = [self.plot_time]

    self.plots.extend([self.plot_spec, self.plot_wtr])


def get_last_part_metadata(self):
    """
    Gets latest part metadata and settings and assigns the
    values to selected_part object.
    """

    selected_part = self.selected_part
    parts = selected_part['parts'].copy()
    assert len(parts) >= 1, \
        'No part found in memory to get the metadata from.'

    selected_part = {}
    selected_part['parts'] = parts
    selected_part['wtid'] = parts[0]

    get_part_metadata(self, set_lsid=False)
    fill_metadata(self, selected_part, set_lsid=False)

    wtsettings.import_settings(self, selected_part, use_defaults=False)

    selected_part['wtid'] = None
    selected_part['part_db'] = None


def fill_metadata(self, selected_part, set_lsid=True):
    " Fills selected_part values into entries on PartPage instances. "

    if set_lsid:
        self.wtid.set(selected_part['wtid'])
    self.part_name.set(selected_part['part_name'])
    self.part_number.set(selected_part['part_number'])
    self.creation_date.set(selected_part['creation_date'])
    self.text_description.delete(1.0, 'end')
    self.text_description.insert('end', selected_part['description'])


def set_resolution_choices(sampling_rate, choices):
    spectral_lines = []
    resolution_choices = []
    for n in range(4, 17):
        spectral_lines.append(2 ** n)
        resolution_choices.append(sampling_rate / spectral_lines[-1])
    choices['resolution'] = resolution_choices


def delete_part_dialog(self):
    """ Deleting a part from database ('Delete Part' button) """
    selected_part = self.selected_part
    if messagebox.askokcancel(
        'Delete',
        'Are you sure you want to delete the part: {}?'.format(
            selected_part['wtid'], ),
        ):

        bf.delete_part(selected_part)
        logger.info('Part deleted: '.format(selected_part['wtid']))

        # Clearing selected_part information
        init_selected_part(selected_part['param_db'])
        fill_listbox(self)      # refreshes parts in listbox