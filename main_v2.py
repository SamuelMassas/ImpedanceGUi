import time
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import serialcom
import serial.serialutil
import tkinter_tools_module as TTm
import threading
import numpy as np
import pandas as pd
import datetime
import webbrowser as wb
import os


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
    freq = array[:, 0]
    z_re = array[:, 1]
    z_im = array[:, 2]

    try:
        mod_z = array[:, 3]
    except IndexError:
        mod_z = np.sqrt(z_re**2 + z_im**2)
    try:
        arg_z = array[:, 4]
    except IndexError:
        arg_z = freq*0

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

    for i, item in enumerate(data):
        item = item.split(',')
        try:
            pro_data[i, 0] = item[0]
            pro_data[i, 1] = item[1]
            pro_data[i, 2] = item[2]
            pro_data[i, 3] = item[3]
            try:
                pro_data[i, 4] = item[4]
            except IndexError:
                pass
            # freq, Zre, Zim, mod_z, arg_z
        except ValueError:
            print('error')
            pass
    pro_data = np.delete(pro_data, 0, axis=0)  # remove headers
    pro_data = np.delete(pro_data, -1, axis=0)  # remove headers

    # unpaking data
    freq = pro_data[:, 0]
    z_re = pro_data[:, 1]
    z_im = pro_data[:, 2]
    mod_z = pro_data[:, 3]
    arg_z = pro_data[:, 4]

    return z_im, z_re, freq, mod_z, arg_z


def load_data():
    file = filedialog.askopenfilename()

    if file.lower().find('.csv') != -1:
        z_im, z_re, freq, mod_z, arg_z = load_csvdata(file)
    elif file.lower().find('.xlsx') != -1:
        z_im, z_re, freq, mod_z, arg_z = load_xldata(file)
    else:
        messagebox.showerror('File type not valid', 'It is not possible to read this file. Only .csv or .xlsx files can'
                                                    ' be used!')

    try:
        # creating new tab to plot data
        # TODO check the bode plot limits
        global Active_tab
        Active_tab = TTm.NewTabGUI(my_notebook, label=file.split('/')[-1])

        # Extracting graph (axes) from tab
        active_chart = Active_tab.chart

        # Creating series in graphs (axes)
        impedance_serie = TTm.NewSeries(active_chart)

        impedance_serie.add_coordinates_nd(z_im, z_re, freq, mod_z, arg_z)
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
    if runner_var.get():
        start_runner()
    else:
        start_coms()


def start_runner():
    def check_value(value):
        try:
            checked = int(value)
            if checked <= 0:
                messagebox.showwarning('Invalid sensor position', 'One or more positions are none positive numbers. '
                                                                  'All positions must be positive integer numbers '
                                                                  'smaller or equal to 10.')
                print(int('Olá'))
            elif checked > 9:
                messagebox.showwarning('Invalid sensor position', 'One or more positions are bigger than 9. '
                                                                  'All positions must be positive integer numbers '
                                                                  'smaller or equal to 10.')
                print(int('Olá'))

            return checked

        except ValueError:
            messagebox.showerror('Error, Not Valid',
                                 'One or more positions are not valid integer numbers. '
                                 'Check the electrode positions and if they are separed by "-".'
                                 'Remove all white spaces')
            print(int('Olá'))

    idxs = [check_value(item) for item in e_idxs.get().split('-')]
    print(idxs)
    for i in idxs:
        start_coms(i)


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
        Active_tab = TTm.NewTabGUI(my_notebook, label=f'{idx} Sensor')
        # my_notebook.select(my_notebook.tabs())  # selecting the new tab to show up

    Active_chart = Active_tab.chart
    b_start['state'] = DISABLED

    try:
        serialcom.write_port(channel, command)
        condition = 1
        pb.reset()
        impedance_serie = TTm.NewSeries(Active_chart)
        main_status.config(text='Measuring')
        while condition:

            try:
                data = str(serialcom.read_port(channel))
            except serial.serialutil.SerialException:
                messagebox.showwarning("Warning", f"Unable to communicat with {channel}")
                data = ''
                condition = 0

            print(data)

            # Format data
            data_vector = data.split('\t')

            if data == "Sweep Complete !!!\r\n":
                condition = 0
                print("Finish - condition:" + str(condition))

            if data == 'Calibration START !!!\r\n':
                main_status.config(text='Calibrating')
                calibrating = 1
                while calibrating:
                    data = str(serialcom.read_port(channel))
                    print(data)
                    pb.progress()
                    if data == "Sweep Complete !!!\r\n":
                        calibrating = 0
                        print("Calibration Finish - condition:" + str(condition))
                pb.reset()
                main_status.config(text='Measuring')

            """ data acquisition and rearranging """
            try:
                freq = float(data_vector[1])
                mod_z = float(data_vector[2])
                arg_z = float(data_vector[3])
                z_re = float(data_vector[4])
                z_im = float(data_vector[5])
                # print([freq, mod_z, arg_z, z_re, z_im])
                impedance_serie.add_coordinates(z_im, z_re, freq, mod_z, arg_z)
            except ValueError:
                print("Value Error")
            except ZeroDivisionError:
                print("0 division")
            except IndexError:
                print("Index error")

            pb.progress()

        pb.complete()
    except AttributeError:
        messagebox.showwarning("Warning", "Unable to start communication. Active port: " + channel)

    time_now = datetime.datetime.now()
    time_now = str(time_now).replace(':', '.')
    Active_tab.e_name.insert(END, f' {time_now[0:-7]}.csv')

    # Auto saving
    if os.path.isdir('AutoSave'):
        pass
    else:
        os.mkdir('AutoSave')

    file = 'AutoSave/' + Active_tab.e_name.get() + '.csv'
    Active_tab.save(path=file)

    b_start['state'] = NORMAL


def read_coms():
    # Tells the microcontroller to stop
    # b_stop['state'] = DISABLED
    try:
        print('Read Start')
        data = serialcom.read_port(channel)
        print(data)
        print('Read Stop')
        pass
    except AttributeError:
        messagebox.showwarning("Warning",
                               "Unable to stop communication. No communication occurring. Active port: " + channel)
    # b_start['state'] = NORMAL


def disable_radios():
    if runner_var.get():
        radio1['state'] = DISABLED
        radio2['state'] = DISABLED
        radio3['state'] = DISABLED
        radio4['state'] = DISABLED
        radio5['state'] = DISABLED
        radio6['state'] = DISABLED
        radio7['state'] = DISABLED
        radio8['state'] = DISABLED
        radio9['state'] = DISABLED
        e_idxs['state'] = NORMAL
    else:
        radio1['state'] = NORMAL
        radio2['state'] = NORMAL
        radio3['state'] = NORMAL
        radio4['state'] = NORMAL
        radio5['state'] = NORMAL
        radio6['state'] = NORMAL
        radio7['state'] = NORMAL
        radio8['state'] = NORMAL
        radio9['state'] = NORMAL
        e_idxs['state'] = DISABLED


def good_bye():
    if messagebox.askokcancel("Quit", "Do you want to quit this program?\nAny unsaved data will be lost!"):
        root.destroy()


def help_me():
    wb.open_new(r'C:\Users\ssilva50548\OneDrive - INL\Documents\PYTHON\Impedance GUI\docs\Impedance docs v3.pdf')


root = Tk()
root.title('Elchem')
root.iconbitmap(r'group-30_116053.ico')
root.geometry('800x500')
root.state('zoomed')
root.protocol("WM_DELETE_WINDOW", good_bye)


channel = "None"  # tracks the current serial port connected to the program
Active_technic = "None"  # tracks the current electrochemical technic and its parameters
Active_control = "None"  # tracks which actions are currently on going on the serial communication control panel
Active_read = False

#
# Creates the main Menu
my_menu = Menu(root)

root.config(menu=my_menu)

my_file = Menu(my_menu, tearoff=0)
my_file.add_command(label='Help', command=help_me)
my_file.add_separator()
my_file.add_command(label="Quit", command=good_bye)
my_settings = Menu(my_menu, tearoff=0)
my_settings.add_command(label="Connection", command=connection)
my_data = Menu(my_menu, tearoff=0)
my_data.add_command(label="load data", command=load_data)

my_menu.add_cascade(label="File", menu=my_file)
my_menu.add_cascade(label="Settings", menu=my_settings)
my_menu.add_cascade(label="Data", menu=my_data)


""" Control panel """
# Creates the control buttons to control the serial communication
main_frame = LabelFrame(root, text="Control Panel", bg="white")
main_frame.pack(side=LEFT, fill=BOTH)

f_control = Frame(main_frame, bg="white")
f_control.pack(side=TOP, fill=X)

b_start = Button(f_control, text="Run", width=15, height=2, bg="azure2",
                 command=lambda: threading.Thread(target=start_path).start())
b_start.pack(padx=5)

b_stop = Button(f_control, text="Read", width=15, height=2, bg="azure2",
                command=lambda: threading.Thread(target=read_coms).start())
b_stop.pack(padx=5)
b_stop['state'] = DISABLED

# Creates a label that tells the user relevant information
main_status = Label(main_frame, text="Connected to: None", bd=1, fg="grey", relief=SUNKEN)
main_status.pack(fill=X, side=BOTTOM)

# Add progress bar
pb = TTm.ProgressBarWidget(main_frame)


""" Control panel 2 """
f_control2 = LabelFrame(main_frame, text='Run Mode', bg="white")
f_control2.pack(side=TOP, fill=X)

make_unique = BooleanVar()
make_unique.set(True)

mkuq = Radiobutton(f_control2, text="Make Unique", variable=make_unique, value=True, bg="white")
ovly = Radiobutton(f_control2, text="Overlay", variable=make_unique, value=False, bg="white")
mkuq.pack(anchor="w")
ovly.pack(anchor="w")

mkuq['state'] = DISABLED
ovly['state'] = DISABLED

""" Sensor position """
f_control3 = LabelFrame(main_frame, text='Sensor', bg="white")
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

runner_var = IntVar()
my_check = Checkbutton(main_frame, text='Runner', variable=runner_var, command=disable_radios, bg='white')
my_check.pack()

e_idxs = Entry(main_frame)
e_idxs.insert(0, '1-2-3-4-5-6-7-8-9')
e_idxs.pack(fill=BOTH, padx=1)
e_idxs['state'] = DISABLED

#
# Creates the right mouse popup menu
# rm_menu = TTm.RightMouse(root).add_items(["Properties", "Analysis"], [function, function])

#
# Creates the frame and tabs for data visualization in top
f_tabframe = LabelFrame(root, text="Data Visualization", padx=10, bg="whitesmoke")
# f_tabframe.grid(row=0, column=1, rowspan=2, sticky="N")
f_tabframe.pack(side=LEFT, fill=BOTH, expand=True)

my_notebook = ttk.Notebook(f_tabframe)
my_notebook.pack(side=LEFT, anchor="n", fill=BOTH, expand=True)


Active_tab = TTm.NewTabGUI(my_notebook)


root.mainloop()
