import datetime
import json
import os
import threading
import webbrowser as wb
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from SC_interface import Server, Client

import numpy as np
import pandas as pd
import serial.serialutil

import serialcom
import tkinter_tools_module_v3 as TTm3


def load_xldata(filename):
    """
    Loads the data from a excel file.
    :param
    filename: str
        string with the path to the desired file
    :return:
    freq: ndarray
        array with the frequencies
    z_real: ndarray
    z_imag: ndarray
    mod_z: ndarray
    arg_z: ndarray
    """
    df = pd.read_excel(io=filename)

    # Getting only values as numpy array
    array = df.values
    if not isinstance(array[0, 0], int) or not isinstance(array[0, 0], float):
        array = np.delete(array, 0, axis=0)

    array = array.astype(float)
    freq = array[:, 0]
    z_re = array[:, 1]
    z_im = abs(array[:, 2])

    try:
        mod_z = array[:, 3]
    except IndexError:
        mod_z = np.sqrt(z_re ** 2 + z_im ** 2)
    try:
        arg_z = array[:, 4]
    except IndexError:
        arg_z = freq * 0

    return z_im, z_re, freq, mod_z, arg_z


def load_csvdata(file):
    """
    loads data from a CSV
    filename: str
        string with the path to the desired file
    :return:
    freq: ndarray
        array with the frequencies
    z_real: ndarray
    z_imag: ndarray
    mod_z: ndarray
    arg_z: ndarray
    """
    with open(file, 'r') as data:
        data = data.read()

    # Rearrange data
    data = data.split('\n')
    pro_data = np.zeros((len(data), 5))
    idx_corr = 0
    for i, item in enumerate(data):
        item = item.split(',')
        j = i-idx_corr
        try:
            pro_data[j, 0] = item[0]
            pro_data[j, 1] = item[1]
            pro_data[j, 2] = item[2]
            try:
                pro_data[j, 3] = item[3]
            except IndexError:
                pro_data[j, 3] = np.sqrt(float(item[1])**2+float(item[2])**2)
            try:
                pro_data[j, 4] = item[4]
            except IndexError:
                pro_data[j, 4] = None
            # freq, Zre, Zim, mod_z, arg_z
        except ValueError:
            pro_data = np.delete(pro_data, j, axis=0)
            idx_corr += 1
            print(f'[SYSTEM] Deleted row {i} during data loading. Row content: {item}')
            pass
    # pro_data = np.delete(pro_data, 0, axis=0)  # remove headers
    # pro_data = np.delete(pro_data, -1, axis=0)  # remove headers

    # unpaking data
    freq = pro_data[:, 0]
    z_re = pro_data[:, 1]
    z_im = abs(pro_data[:, 2])
    mod_z = pro_data[:, 3]
    arg_z = pro_data[:, 4]

    return z_im, z_re, freq, mod_z, arg_z


def load_data(file=None):
    if file is None:
        file = filedialog.askopenfilename()

    if file.lower()[-3:] == 'csv':
        z_im, z_re, freq, mod_z, arg_z = load_csvdata(file)
    elif file.lower()[-4:] == 'xlsx':
        z_im, z_re, freq, mod_z, arg_z = load_xldata(file)
    else:
        messagebox.showerror('File type not valid', 'It is not possible to read this file. Only .csv or .xlsx files can'
                                                    ' be used!')

    try:
        # creating new tab to plot data
        global Active_tab
        # Active_tab = TTm3.NewTabGUI(my_notebook, label=file.split('/')[-1])
        Active_tab = my_notebook.add_costume_tab(server=server, label=file.split('/')[-1])

        # Extracting graph (axes) from tab
        active_chart = Active_tab.chart

        # Creating series in graphs (axes)
        impedance_serie = TTm3.NewSeries(active_chart)

        impedance_serie.add_coordinates_nd(z_im, z_re, freq, mod_z, arg_z)
        my_notebook.select(len(my_notebook.tabs()) - 1)  # selecting added tab
    except UnboundLocalError:
        pass


def connection():
    def refresh_listbox():
        # Identifies the available ports for communication
        port_list = serialcom.see_ports()
        my_listbox.delete(0, END)
        for i in range(0, len(port_list)):
            my_listbox.insert(0, port_list[i])

    def connect_port():
        # establishes the connection to the selected port
        port_name = my_listbox.get(ANCHOR)
        port_name = port_name.split(' ')
        portID = port_name[0]

        global channel  # variable that tracks current connected port
        channel = serialcom.connect_to(portID, int(bauds.get()))
        if channel != "None":
            # if connection is established successfully to the desired port
            statusbar.config(text="Connected to: " + portID)
            main_status.config(text="Connected to: " + portID)
            # serialcom.read_port(channel)
        else:
            # if connection is not established successfully to the desired port
            statusbar.config(text="Connection failed")
            main_status.config(text="Connection failed")

    def scroll_function(event):
        if event.delta > 0:
            my_listbox.xview_scroll(-1, "unit")
        else:
            my_listbox.xview_scroll(1, "unit")

    def close_top():
        my_listbox.unbind_all('<MouseWheel>')
        top.destroy()

    # Creates the window that opens when option connection is selected from the menu
    top = Toplevel()
    top.geometry("400x400")
    top.resizable(False, False)
    top.transient(root)
    top.iconbitmap(r'group-30_116053.ico')
    top.grab_set()

    # creates the input for the bauds number
    f_properties = LabelFrame(top, text="Connection properties")
    f_properties.pack()
    l_bauds = Label(f_properties, text="Bauds")
    bauds = Entry(f_properties, fg="grey")
    bauds.insert(0, 115200)
    l_bauds.grid(row=0, column=0)
    bauds.grid(row=0, column=1)

    # Create interactive display port window
    my_frame = LabelFrame(top, text="Ports")
    my_frame.pack()
    my_scrollbarX = Scrollbar(my_frame, orient=HORIZONTAL)
    my_scrollbarY = Scrollbar(my_frame, orient=VERTICAL)
    my_listbox = Listbox(my_frame, width=50, xscrollcommand=my_scrollbarX.set, yscrollcommand=my_scrollbarY.set)
    my_scrollbarY.config(command=my_listbox.yview)
    my_scrollbarX.config(command=my_listbox.xview)
    my_scrollbarY.pack(side=RIGHT, fill=Y)
    my_scrollbarX.pack(side=BOTTOM, fill=X)
    my_listbox.pack()

    my_listbox.bind_all('<MouseWheel>', scroll_function)

    # creates a bar that tells crucial information to the user
    statusbar = Label(top, text="status", width=43, bd=1, relief=SUNKEN, fg="grey")
    statusbar.pack()

    # creates the buttons for interaction
    b_connect = Button(top, text="Connect", width=20, command=connect_port)
    b_refresh = Button(top, text="Refresh", width=20, command=refresh_listbox)
    b_close = Button(top, text="Save and Close", width=20, command=close_top)
    b_connect.pack()
    b_refresh.pack()
    b_close.pack()

    # automatically updates the list of available ports
    refresh_listbox()


def start_path():
    idx = control_panel.index("current")
    if idx == 1:
        control_panel.tab(0, state='disabled')
        start_runner()
    elif idx == 0:
        control_panel.tab(1, state='disabled')
        start_coms()


def start_runner():
    def join_(item1, item2):
        """
        Joins to strings together
        """
        if isinstance(item1, str):
            return f'{item1} / {item2}'
        else:
            return f'{item1} +- {item2}'

    def check_value(value):
        try:
            checked = int(value)
            if checked <= 0 or checked > 9:
                messagebox.showwarning('Invalid sensor position', 'One or more positions are none positive numbers. '
                                                                  'All positions must be positive integer numbers '
                                                                  'smaller or equal to 10.')
            return checked

        except ValueError:
            messagebox.showerror('Error, Not Valid',
                                 'One or more positions are not valid integer numbers. '
                                 'Check the electrode positions and if they are separed by "-".'
                                 'Remove all white spaces')

    idxs = [check_value(item) for item in e_idxs.get().split('-')]

    data = []
    for idx in idxs:
        if stop.get():
            break

        # load_data(file=r'ExperimentalData\ImpedanceData#' + f'{idx}.xlsx')
        start_coms(idx)  # Making measure

        """ Starting fitting procedure"""
        fit_editor.get_from_buffer()  # Updating initial guess from buffer
        # fit_editor.up_bound = 40
        params, error, elements, stats = fit_editor.apply_fit()
        name = Active_tab.e_name.get()

        # Arranging values for data frame
        values = []
        for i, item in enumerate(params):
            values.append(item)
            values.append(error[i])
        data.append(np.concatenate(([name], values, stats), axis=0))

    elements = list(map(join_, elements[0], elements[1]))

    # creating columns list
    el_head = []
    for item in elements:
        el_head.append(item)
        el_head.append('error')
    # adding statistics columns
    headers = ['Name'] + el_head + ['Chi^2', 'Critical', 'df']

    file_name = e_file.get()
    if file_name.find('.xlsx') == -1:
        # Addding extension if not specified
        file_name += '.xlsx'

    file_path = var_dir.get().replace('\\', '/') + '/' + file_name
    df = pd.DataFrame(data, columns=headers)
    # checking if file already exists, and renaming file path
    if os.path.isfile(file_path):
        time_now = datetime.datetime.now()
        time_now = str(time_now).replace(':', '.')
        file_name = file_name.replace('.xlsx', '')
        file_name += f' {time_now[0:-7]}.xlsx'
        file_path += var_dir.get().replace('\\', '/') + '/' + file_name
    df.to_excel(file_path)

    stop.set(False)  # Resetting stop var


def start_coms(idx=None):
    # Tells the microcontroller to start, and updates the current action in Active_control variable
    if idx is None:
        idx = sensor_id.get()
        command = 'Start!' + str(idx)
    else:
        command = 'Start!' + str(idx)
    command = bytes(command, 'utf8')
    print(command)

    global Active_tab

    # Checks if need for a new tab
    if make_unique.get():
        # Active_tab = TTm3.NewTabGUI(my_notebook, label=f'{idx} Sensor')
        Active_tab = my_notebook.add_costume_tab(server=server, label=f'{idx} Sensor')
        my_notebook.select(len(my_notebook.tabs()) - 1)
        # my_notebook.select(my_notebook.tabs())  # selecting the new tab to show up

    Active_chart = Active_tab.chart
    control_panel.get_panel().b_start['state'] = DISABLED
    control_panel.get_panel().b_stop['state'] = NORMAL

    try:
        channel.reset_input_buffer()
        serialcom.write_port(channel, command)

        pb.reset()
        impedance_serie = TTm3.NewSeries(Active_chart)
        main_status.config(text='Measuring')
        while True:

            try:
                data = str(serialcom.read_port(channel))
            except serial.serialutil.SerialException:
                messagebox.showwarning("Warning", f"Unable to communicat with {channel}")
                data = ''
                break
            main_status.config(text='Measuring...')
            print(data)

            # Format data
            data_vector = data.split('\t')

            if data == "Sweep Complete !!!\r\n" or data == "Sweep Aborted !!!\r\n":
                print("Finish - condition:")
                break

            if data == 'Measurement START !!!\r\n':
                main_status.config(text='Calibrating...')

            """ data acquisition and rearranging """
            try:
                freq = float(data_vector[1])
                mod_z = float(data_vector[2])
                arg_z = float(data_vector[3])
                z_re = float(data_vector[4])
                z_im = float(data_vector[5])
                impedance_serie.add_coordinates(z_im, z_re, freq, mod_z, arg_z)

            except ValueError:
                print("Value Error")
            except IndexError:
                # print("Index error")
                pass

            if impedance_serie.freq:
                arr = {'name': Active_tab.e_name.get(),
                       'append': True,
                       'data': {'freq': freq, 'z_re': z_re, 'z_im': z_im, 'mod_z': mod_z, 'arg_z': arg_z},
                       'condition': 'running'}
                threading.Thread(target=lambda: stream_live(arr)).start()

            pb.progress()

        time_now = datetime.datetime.now()
        time_now = str(time_now).replace(':', '.')
        Active_tab.e_name.insert(END, f' {time_now[0:-7]}')

        # Auto saving
        if os.path.isdir('AutoSave'):
            pass
        else:
            os.mkdir('AutoSave')

        file = 'AutoSave/' + Active_tab.e_name.get() + '.csv'
        Active_tab.save(path=file)

        # telling client measure is complete
        arr = {'name': Active_tab.e_name.get(),
               'append': True,
               'data': None,
               'condition': 'complete'}
        threading.Thread(target=lambda: stream_live(arr)).start()

        pb.complete()
    except AttributeError:
        messagebox.showwarning("Warning", "Unable to start communication. Active port: " + channel)

    control_panel.get_panel().b_start['state'] = NORMAL
    control_panel.get_panel().b_stop['state'] = DISABLED
    control_panel.tab(0, state='normal')
    control_panel.tab(1, state='normal')


def stop_coms():
    # Tells the microcontroller to stop
    control_panel.get_panel().b_stop['state'] = DISABLED
    try:
        idx = control_panel.index("current")
        if idx == 1:
            stop.set(True)
        channel.write(b'Stop!')
    except AttributeError:
        messagebox.showwarning("Warning",
                               "Unable to stop communication. No communication occurring. Active port: " + channel)
    control_panel.get_panel().b_stop['state'] = NORMAL


def good_bye():
    if messagebox.askokcancel("Quit", "Do you want to quit this program?\nAny unsaved data will be lost!"):
        if server.online:
            server.set_offline()

        root.destroy()


def help_me():
    wb.open_new(r'C:\Users\ssilva50548\OneDrive - INL\Documents\PYTHON\Impedance GUI\docs\Impedance docs v3.pdf')


def get_dir():
    dir = filedialog.askdirectory()
    if dir != '':
        var_dir.set(dir)


def prefs():
    def save_configs():
        configs = {'ipv4': eipv4.get(),
                   'PORT': eport.get()}
        json_string = json.dumps(configs)
        with open('configs', 'w') as file:
            file.write(json_string)

        top.destroy()

    def get_configs():
        with open('configs', 'r') as file:
            json_string = file.read()
        configs = json.loads(json_string)
        return configs

    configs = get_configs()

    # Openning preferences
    top = Toplevel()
    top.transient(root)
    top.iconbitmap(r'group-30_116053.ico')
    top.grab_set()
    top.protocol("WM_DELETE_WINDOW", save_configs)

    frm_ws = LabelFrame(top, text='Socket configuration (Client):')
    frm_ws.pack()
    eipv4 = Entry(frm_ws)
    eport = Entry(frm_ws)
    eipv4.insert(0, configs['ipv4'])
    eport.insert(0, configs['PORT'])
    eipv4.pack(side=LEFT)
    eport.pack(side=LEFT)

    frm_spec = LabelFrame(top, text='Other configurations')
    frm_spec.pack()
    Checkbutton(frm_spec, text='Disable ToolTips').grid(row=0, column=0, sticky='w')
    Checkbutton(frm_spec, text='Configure default directory').grid(row=1, column=0, sticky='w')
    Checkbutton(frm_spec, text='Disable -Ask Save- upon closing program').grid(row=2, column=0, sticky='w')
    Checkbutton(frm_spec, text='Disable -Ask Save- upon closing tabs').grid(row=3, column=0, sticky='w')
    Checkbutton(frm_spec, text='Remove -New tab-').grid(row=4, column=0, sticky='w')

    top.mainloop()


def client_config():
    global client_listener
    if client.online:
        client.close_connection()
        client_listener.join()
        my_settings.entryconfigure(2, image=imgstream, label='Connect Client')
        my_settings.entryconfigure(1, state=NORMAL)
    elif not server.online:
        try:
            client.connect_client()
            client_listener = threading.Thread(target=getting_service)
            client_listener.start()  # Starting serversocket in new thread
            my_settings.entryconfigure(2, image=imgstream_on, label='Client connected')
            my_settings.entryconfigure(1, state=DISABLED)
        except ConnectionRefusedError:
            messagebox.showerror('Connection Refused!', 'Make sure to start the Server before '
                                                        'connecting the Client!')


def getting_service():
    # global Active_tab
    data_name = ''
    while client.online:
        json_string = client.start_listening()
        data = json.loads(json_string)

        if data['data'] is not None:
            freq = data['data']['freq']
            z_re = data['data']['z_re']
            z_im = data['data']['z_im']
            mod_z = data['data']['mod_z']
            arg_z = data['data']['arg_z']

            if data_name != data['name']:
                data_name = data['name']

                receiver_tab = my_notebook.add_costume_tab(server=server, label=data_name)
                active_chart = receiver_tab.chart
                impedance_serie = TTm3.NewSeries(active_chart)
                my_notebook.select(len(my_notebook.tabs()) - 1)  # selecting added tab

            if data['append']:
                impedance_serie.add_coordinates(z_im, z_re, freq, mod_z, arg_z)
            else:
                impedance_serie.add_coordinates_nd(
                    np.array(z_im),
                    np.array(z_re),
                    np.array(freq),
                    np.array(mod_z),
                    np.array(arg_z))

            if data['condition'] == 'complete':
                data_name = ''
        elif data['data'] is None and data['condition'] == 'complete':
            data_name = ''


def server_config():
    global server_listener
    # Launching or closing serversocket
    if server.online:
        server.set_offline()

        my_settings.entryconfigure(1, image=imgstream, label='Start Server')
        my_settings.entryconfigure(2, state=NORMAL)
    elif not client.online:
        server.set_online()
        server_listener = threading.Thread(target=server.start_listening)
        server_listener.start()  # Starting serversocket in new thread
        my_settings.entryconfigure(1, image=imgstream_on, label=f'Serving at {server.ipv4}:{server.PORT}')
        my_settings.entryconfigure(2, state=DISABLED)  # Disabling Client util server is offline


def stream_live(data):
    # Check if there are clients and streaming to them
    if server.clients:
        for iclient in server.clients:
            json_string = json.dumps(data)
            server.stream2client(iclient, json_string)


class CostumeNoteBook(ttk.Notebook):
    """
    Costume Notebook. Implemented methods to add and remove costume tabs and variables to track existent tabs
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tabs_list = []

    def add_costume_tab(self, **kwargs):
        cost_tab = TTm3.NewTabGUI(self, **kwargs)
        self.tabs_list.append(cost_tab)

        return cost_tab

    def remove_tab(self, costume_tab):
        self.tabs_list.remove(costume_tab)

    def get_costume_tab(self):
        """ Retrieves the active costume tab """
        return self.tabs_list[self.index(self.select())]


class ControlPanel(ttk.Notebook):
    """ Creates control panel. Allows for the additions of different panels"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tab_list = []

    def add_panel(self, mode, **kwargs):
        panel = Panel(master=self, bg='white')

        self.tab_list.append(panel)
        self.add(panel, text=kwargs['text'])
        return panel

    def get_panel(self):
        return self.tab_list[self.index('current')]


class Panel(Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.b_start = Button(self, text="Run", width=15, height=2, bg="azure2",
                              command=lambda: threading.Thread(target=start_path).start())
        self.b_start.pack(padx=5)

        self.b_stop = Button(self, text="Stop", width=15, height=2, bg="azure2",
                             command=lambda: threading.Thread(target=stop_coms).start())
        self.b_stop.pack(padx=5)
        self.b_stop['state'] = DISABLED


root = Tk()
root.title('Elchem - SERVER')
root.iconbitmap(r'group-30_116053.ico')
root.geometry('800x500')
root.state('zoomed')
root.protocol("WM_DELETE_WINDOW", good_bye)

stop = BooleanVar()
stop.set(False)  # To stop runner
channel = "None"  # tracks the current serial port connected to the program
Active_technic = "None"  # tracks the current electrochemical technic and its parameters
Active_control = "None"  # tracks which actions are currently on going on the serial communication control panel
Active_read = False

# Stetting up serversocket
server = Server()
client = Client(ipv4='192.168.33.221', port=5050)
server_listener = None  # will hold the current thread listener
client_listener = None

#
# Creates the main Menu
my_menu = Menu(root)

root.config(menu=my_menu)

imgserial = Image.open('icon_serial_connection.jpg')
imgserial = imgserial.resize((20, 20))
imgserial = ImageTk.PhotoImage(imgserial)

imgload = Image.open('icon_upload_data.jpg')
imgload = imgload.resize((20, 20))
imgload = ImageTk.PhotoImage(imgload)

imgprefs = Image.open('icon_preferences.jpg')
imgprefs = imgprefs.resize((20, 20))
imgprefs = ImageTk.PhotoImage(imgprefs)

imgstream = Image.open('icon_stream.jpg')
imgstream = imgstream.resize((20, 20))
imgstream = ImageTk.PhotoImage(imgstream)

imgstream_on = Image.open('icon_stream_online.jpg')
imgstream_on = imgstream_on.resize((20, 20))
imgstream_on = ImageTk.PhotoImage(imgstream_on)

my_file = Menu(my_menu, tearoff=0)
my_file.add_command(label='Help', command=help_me)
my_file.add_separator()
my_file.add_command(label="Quit", command=good_bye)
my_settings = Menu(my_menu, tearoff=0)
my_settings.add_command(label="Connection", command=connection, image=imgserial, compound='left')
my_settings.add_command(label="Start Server", command=server_config, image=imgstream, compound='left')
my_settings.add_command(label="Connect Client", command=client_config, image=imgstream, compound='left')
my_settings.add_command(label='Configurations', command=prefs, image=imgprefs, compound='left')
my_data = Menu(my_menu, tearoff=0)
my_data.add_command(label="load data", command=load_data, image=imgload, compound='left')
my_menu.add_cascade(label="File", menu=my_file)
my_menu.add_cascade(label="Settings", menu=my_settings)
my_menu.add_cascade(label="Data", menu=my_data)

""" Control panel """
# Creates the control buttons to control the serial communication
main_frame = Frame(root, bg="White")
main_frame.pack(side=LEFT, fill=BOTH)

control_panel = ControlPanel(master=main_frame)
control_panel.pack(fill=BOTH, expand=1)

single_panel = control_panel.add_panel(text="Single", mode='Single')
runner_panel = control_panel.add_panel(text="Runner", mode='Runner')

# Creates a label that tells the user relevant information
main_status = Label(main_frame, text="Connected to: None", bd=1, fg="grey", relief=SUNKEN)
main_status.pack(fill=X, side=BOTTOM)

# Add progress bar
pb = TTm3.ProgressBarWidget(main_frame)

""" Control panel 2 """
# f_control2 = LabelFrame(main_frame, text='Run Mode', bg="white")
# f_control2.pack(side=TOP, fill=X)
#
make_unique = BooleanVar()
make_unique.set(True)

# mkuq = Radiobutton(f_control2, text="Make Unique", variable=make_unique, value=True, bg="white")
# ovly = Radiobutton(f_control2, text="Overlay", variable=make_unique, value=False, bg="white")
# mkuq.pack(anchor="w")
# ovly.pack(anchor="w")
#
# mkuq['state'] = DISABLED
# ovly['state'] = DISABLED

""" Sensor position """
f_control3 = LabelFrame(single_panel, text='Sensor', bg="white")
f_control3.pack(side=TOP, fill=X)

sensor_id = IntVar()
sensor_id.set(1)

radio1 = Radiobutton(f_control3, text="7", variable=sensor_id, value=7, bg="white")
radio2 = Radiobutton(f_control3, text="8", variable=sensor_id, value=8, bg="white")
radio3 = Radiobutton(f_control3, text="9", variable=sensor_id, value=9, bg="white")
radio4 = Radiobutton(f_control3, text="4", variable=sensor_id, value=4, bg="white")
radio5 = Radiobutton(f_control3, text="5", variable=sensor_id, value=5, bg="white")
radio6 = Radiobutton(f_control3, text="6", variable=sensor_id, value=6, bg="white")
radio7 = Radiobutton(f_control3, text="1", variable=sensor_id, value=1, bg="white")
radio8 = Radiobutton(f_control3, text="2", variable=sensor_id, value=2, bg="white")
radio9 = Radiobutton(f_control3, text="3", variable=sensor_id, value=3, bg="white")
radio1.grid(row=0, column=0)
radio2.grid(row=0, column=1)
radio3.grid(row=0, column=2)
radio4.grid(row=1, column=0)
radio5.grid(row=1, column=1)
radio6.grid(row=1, column=2)
radio7.grid(row=2, column=0)
radio8.grid(row=2, column=1)
radio9.grid(row=2, column=2)

list_frame = LabelFrame(runner_panel, text='Electrode list:', bg='white')
list_frame.pack(fill=BOTH, pady=5)
e_idxs = Entry(list_frame)
e_idxs.insert(0, '1-2-3-4-5-6-7-8-9')
e_idxs.pack(fill=BOTH, padx=3, pady=3)

export_frame = LabelFrame(runner_panel, text='Export configuration:', bg='white')
export_frame.pack(fill=BOTH, pady=5)

imgfolder = Image.open('icon_save_folder.jpg')
imgfolder = imgfolder.resize((25, 27))
imgfolder = ImageTk.PhotoImage(imgfolder)

var_dir = StringVar()
var_dir.set(os.getcwd())
b_folder = Button(export_frame, text='Select Folder', image=imgfolder, command=get_dir)
b_folder.pack(side=LEFT, padx=2, pady=5)
TTm3.ToolTip(b_folder, tip_text='Select folder to save results')

e_file = Entry(export_frame, width=10)
e_file.insert(0, '-File name-')
e_file.pack(fill=X, expand=1, padx=5, pady=5)

# Creates the frame and tabs for data visualization in top
f_tabframe = LabelFrame(root, text="Data Visualization", padx=10, bg="whitesmoke")
# f_tabframe.grid(row=0, column=1, rowspan=2, sticky="N")
f_tabframe.pack(side=LEFT, fill=BOTH, expand=True)

my_notebook = CostumeNoteBook(master=f_tabframe)
my_notebook.pack(side=LEFT, anchor="n", fill=BOTH, expand=True)

fit_editor = TTm3.FittingEditor(my_notebook)
my_menu.add_command(label='Fitting Editor', command=lambda: fit_editor.open(root, my_menu))

Active_tab = my_notebook.add_costume_tab(server=server, client=client)

root.mainloop()
