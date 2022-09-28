import json
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from typing import List, Any
import pandas
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import pandas as pd
from impedance.models.circuits import CustomCircuit
from scipy import stats
import threading
import openpyxl
from PIL import Image, ImageTk

"""
This modules contains classes to create useful complex widgets.

Syntax example:

        example 1: ToolTip(my_button, tip_text='This is a button')
        example 2: rm_menu = RightMouse(root).add_items(["Build Ramps", "Properties", "Analysis"],
                                         [RampEditorTop.call, function, function])
                   
                   
This class is useful to add additional information to help the user using the  GUI 
without taking much space from the screen.
"""


class ToolTip:
    """
    This class is useful to add additional information to help the user using the  GUI
    without taking much space from the screen.
    """
    def __init__(self, widget, tip_text=None):
        self.widget = widget
        self.tip_text = tip_text
        self.tip_window = None  # initializing the variable
        widget.bind('<Enter>', self.mouse_enter)
        widget.bind('<Leave>', self.mouse_leave)

    def mouse_enter(self, _event):
        self.show_tooltip()

    def mouse_leave(self, _event):
        self.hide_tooltip()

    def show_tooltip(self):
        """ Creates a new window"""
        # Getting the position at which the tooltip will pop-up
        x_left = self.widget.winfo_rootx()
        y_top = self.widget.winfo_rooty() - 18
        # Creating a new window and configuring it
        self.tip_window = Toplevel(self.widget)
        self.tip_window.overrideredirect(True)
        self.tip_window.geometry("+%d+%d" % (x_left, y_top))
        # Adding a label to display the information wanted
        #  background="#ffffe0"
        label = Label(self.tip_window, text=self.tip_text, justify=LEFT, background="#ffffe0", relief=SOLID,
                      borderwidth=1, font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self):
        """Destroys the created window"""
        # if self.tip_window:
        self.tip_window.destroy()


class ProgressBarWidget:
    """ Creates a progress bar """
    def __init__(self, master, tasks=60):
        """
        Displays a progress bar.

        :param master: tkinter widget
            Widget where the bar will be placed
        :param tasks: int
            Number of tasks expected to complete the progress bar

        """
        self.master = master
        self.frame = Frame(master, bg='white')
        self.frame.pack(side=BOTTOM, fill=Y)

        self.tasks = tasks
        self.bar = ttk.Progressbar(self.frame, orient='horizontal', mode='determinate', maximum=self.tasks, length=150)
        self.bar.pack(side=BOTTOM)

        self.text = '0%'
        self.label = Label(self.frame, text=self.text, bg='white')
        self.label.pack(side=TOP)

    def progress(self):
        """ Increases the progress of the bar """
        self.bar['value'] = 1 + int(self.bar['value'])
        self.update_label()

    def reset(self):
        """ Resets bar"""
        self.bar.stop()

    def complete(self):
        """ Completely fill the bar"""
        self.bar['value'] = self.tasks
        self.update_label()

    def update_label(self):
        """ Updates the progress label"""
        self.text = str(round(self.bar['value'] / self.tasks * 100)) + '%'
        self.label.config(text=self.text)


class RightMouse:
    """
    Creates a right mouse menu that pops-up every time the user clicks the right mouse.
    The menu can be bound to any widget, like: root, buttons, frames, labels.
    The widget that is bounded is called master
    """
    def __init__(self, master, event='<Button-3>'):
        self.master = master
        self.menu = Menu(master, tearoff=False)
        master.bind(event, self.mouse_menu)

    def mouse_menu(self, _event):
        # This function pops up the menu
        self.menu.tk_popup(_event.x_root, _event.y_root)
        # print("Menu open")

    """
    This methods bellow, can be used to add and remove items from the menu. 
    The command should be a function created in the working module
    """
    def add_item(self, item_name, _command):
        self.menu.add_command(label=item_name, command=_command)

    def add_items(self, item_list, command_list):
        for i in range(len(item_list)):
            self.menu.add_command(label=item_list[i], command=command_list[i])

    def remove_item(self, item_name):
        self.menu.deletecommand(item_name)


class TkinterChart:
    """
    TkinterGraph creates a Chart in the window. This Chart can be used to plot real time values together
    with NewSeries.

    """
    def __init__(self, master, title='', size=None, xlabel='x', ylabel='y', logscale=False, add_toolbar=False):
        """
        Initializes and displays a new empty axes in a tkinter window.

        :param master: tkinter widget
            Widget where the axes will display, generally a frame
        :param title: str
            Title of the axes
        :param size:
            Figure size, default is [7, 5]
        :param xlabel: str
            Label of the x-axis
        :param ylabel: str
            Label of the y-axis
        :param logscale: boolean
            To change the axis scale to logarithm
        :param add_toolbar: boolean
            To add a toolbar for control the axes
        """
        if size is None:
            size = [7, 5]
        self.master = master
        self.title = title
        self.size = size
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.axes_secondary = None
        # Counts the number of series in this chart up to 14, than resets
        self.series_counter = 0
        self.series_list = []
        self.legend = None

        # Building figure and main Axes
        self.figure = Figure(figsize=self.size)
        self.axes_ = self.figure.add_subplot(111)
        self.axes_.grid(True)
        self.axes_.set_title(self.title)
        self.axes_.set_xlabel(self.xlabel)
        self.axes_.set_ylabel(self.ylabel)
        # self.axes_.set_aspect(aspect='equal')

        if logscale:
            self.axes_.set_xscale('log')
            self.axes_.set_yscale('log')

        # Limits of the axes
        self.x_upper_limit = 1
        self.x_lower_limit = -1
        self.y_upper_limit = 1
        self.y_lower_limit = -1

        self.sec_x_upper_limit = 1
        self.sec_x_lower_limit = -1
        self.sec_y_upper_limit = 1
        self.sec_y_lower_limit = -1

        # Builds canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)
        self.canvas.draw()

        # Add toolbar
        if add_toolbar:
            toolbar = NavigationToolbar2Tk(self.canvas, self.master, pack_toolbar=False)
            toolbar.update()
            toolbar.pack(side=BOTTOM)

    def add_twin_(self, label=''):
        """ Creates a secondary Y axis """
        self.axes_secondary = self.axes_.twinx()
        self.axes_secondary.set_ylabel(ylabel=label)

    def add_legend_(self, labels):
        self.legend = self.axes_.legend(self.series_list, labels, loc=0)


class ImpedanceChart:
    """
    TkinterGraph creates a Chart in the window. This Chart can be used to plot real time values together
    with NewSeries.

    """
    def __init__(self, master):
        """
        Initializes and displays a new empty axes in a tkinter window.

        :param master: tkinter widget
            Widget where the axes will display, generally a frame
        """
        size = [7, 5]
        self.master = master
        self.title = ''
        self.size = size
        self.axes_secondary = None
        # Counts the number of series in this chart up to 14, than resets
        self.series_counter = 0
        self.series_list = []
        self.legend = None

        # Building figure and main Axes
        self.figure = Figure(figsize=self.size)
        # Nyquist
        self.axes_ny = self.figure.add_subplot(121)
        self.axes_ny.grid(True)
        self.axes_ny.set_title(self.title)
        self.axes_ny.set_xlabel(u"Z'/\u2126")
        self.axes_ny.set_ylabel(u"-Z''/\u2126")

        # self.axes_ny.axis('equal')
        self.axes_ny.set_xlim([0, 1000])
        self.axes_ny.set_ylim([0, 1000])
        # Bode
        # mod z
        self.axes_bd = self.figure.add_subplot(122)
        self.axes_bd.grid(True)
        self.axes_bd.set_title(self.title)
        self.axes_bd.set_xlabel('Frequency/ Hz')
        self.axes_bd.set_ylabel(u'Z/\u2126')
        self.axes_bd.set_xscale('log')
        self.axes_bd.set_yscale('log')
        self.axes_bd.set_xlim([1, 10*10**5])
        self.axes_bd.set_ylim([1, 1000])
        # phase
        self.axes_secondary = self.axes_bd.twinx()
        self.axes_secondary.set_ylabel(ylabel='Phase/º')
        self.axes_secondary.set_ylim([-1, 1])
        self.figure.tight_layout()

        # Limits of the axes
        self.x_upper_limit = 1
        self.x_lower_limit = -1
        self.y_upper_limit = 1
        self.y_lower_limit = -1

        self.sec_x_upper_limit = 1
        self.sec_x_lower_limit = -1
        self.sec_y_upper_limit = 1
        self.sec_y_lower_limit = -1

        # Builds canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        self.canvas.draw()

        toolbar = NavigationToolbar2Tk(self.canvas, self.master, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=BOTTOM, fill=BOTH)


class NewSeries:
    """ NewSeries creates and plots series of data en the desired Chart.

    Possible styles for plotting:

    lineStyles = {'': '_draw_nothing', ' ': '_draw_nothing', '-': '_draw_solid', '--': '_draw_dashed',
                  '-.': '_draw_dash_dot', ':': '_draw_dotted', 'None': '_draw_nothing'}

    markers = {'.': 'point', ',': 'pixel', 'o': 'circle', 'v': 'triangle_down', '^': 'triangle_up',
               '<': 'triangle_left', '>': 'triangle_right', '1': 'tri_down', '2': 'tri_up', '3': 'tri_left',
               '4': 'tri_right', '8': 'octagon', 's': 'square', 'p': 'pentagon', '*': 'star', 'h': 'hexagon1',
               'H': 'hexagon2', '+': 'plus', 'x': 'x', 'D': 'diamond', 'd': 'thin_diamond', '|': 'vline', '_': 'hline',
               'P': 'plus_filled', 'X': 'x_filled', 0: 'tickleft', 1: 'tickright', 2: 'tickup', 3: 'tickdown',
               4: 'caretleft', 5: 'caretright', 6: 'caretup', 7: 'caretdown', 8: 'caretleftbase', 9: 'caretrightbase',
               10: 'caretupbase', 11: 'caretdownbase', 'None': 'nothing', None: 'nothing', ' ': 'nothing',
               '': 'nothing'}
    """
    def __init__(self, chart, style=None):
        self.chart = chart
        self.im_z = []
        self.re_z = []
        self.freq = []
        self.mod_z = []
        self.arg_z = []

    # Attributes the style of the new series
        if style is None:
            if self.chart.series_counter == 0:
                self.style = 'b.'
            elif self.chart.series_counter == 1:
                self.style = 'r.'
            elif self.chart.series_counter == 2:
                self.style = 'g.'
            elif self.chart.series_counter == 3:
                self.style = 'y.'
            elif self.chart.series_counter == 4:
                self.style = 'k.'
            elif self.chart.series_counter == 5:
                self.style = 'b*'
            elif self.chart.series_counter == 6:
                self.style = 'r*'
            elif self.chart.series_counter == 7:
                self.style = 'g*'
            if self.chart.series_counter == 8:
                self.style = 'y*'
            elif self.chart.series_counter == 9:
                self.style = 'k*'
            elif self.chart.series_counter == 10:
                self.style = 'bD'
            elif self.chart.series_counter == 11:
                self.style = 'rD'
            elif self.chart.series_counter == 12:
                self.style = 'gD'
            elif self.chart.series_counter == 13:
                self.style = 'yD'
            elif self.chart.series_counter == 14:
                self.style = 'kD'
                self.chart.series_counter = -1
        else:
            self.style = style

        # Updates the number of series on the current chart
        self.chart.series_counter += 1

        # Selects which yaxis to plot. To plot a secondary axis, this must be created first in TkinterChart.add_twin_()
        self.line_ny = self.chart.axes_ny.plot([], [], self.style, markersize=3)[0]
        self.line_bd = self.chart.axes_bd.plot([], [], self.style, markersize=3)[0]
        self.line_bd2 = self.chart.axes_secondary.plot([], [], 'r.', markersize=3)[0]

        self.chart.series_list.append([self.line_ny, self.line_bd, self.line_bd2])

    def add_coordinates(self, im_z, re_z, freq, mod_z, arg_z):
        """ Stores the x and y data in the same vector and plots the points by calling draw_()"""
        self.im_z.append(im_z)
        self.re_z.append(re_z)
        self.freq.append(freq)
        self.mod_z.append(mod_z)
        self.arg_z.append(arg_z)
        self.draw_(im_z, re_z, freq, mod_z, arg_z)

    def add_coordinates_nd(self, im_z=None, re_z=None, freq=None, mod_z=None, arg_z=None):
        if im_z is not None:
            self.im_z = np.ndarray.tolist(im_z)
        if re_z is not None:
            self.re_z = np.ndarray.tolist(re_z)
        if freq is not None:
            self.freq = np.ndarray.tolist(freq)
        if mod_z is not None:
            self.mod_z = np.ndarray.tolist(mod_z)
        if arg_z is not None:
            self.arg_z = np.ndarray.tolist(arg_z)

        self.draw_(im_z, re_z, freq, mod_z, arg_z)

    def draw_(self, im_z, re_z, freq, mod_z, arg_z):
        """ Displays the point in the axes_ and rescales"""
        if im_z is not None and re_z is not None:
            self.line_ny.set_data(self.re_z, self.im_z)
        if freq is not None and mod_z is not None:
            self.line_bd.set_data(self.freq, self.mod_z)
        if freq is not None and arg_z is not None:
            self.line_bd2.set_data(self.freq, self.arg_z)
        self.rescale()
        # self.chart.canvas.draw()

    def rescale(self):
        """ Rescales the x and y axis to show all plots in the chart """
        min_imz = min(self.im_z)
        max_imz = max(self.im_z)
        min_rez = min(self.re_z)
        max_rez = max(self.re_z)

        lw_ny_x, up_ny_x = self.chart.axes_ny.get_xlim()
        lw_ny_y, up_ny_y = self.chart.axes_ny.get_ylim()

        # Nyquist plot
        if lw_ny_x >= min_rez or max_rez >= up_ny_x or lw_ny_y >= min_imz or max_imz >= up_ny_y:
            self.chart.axes_ny.set_xlim([min_rez*0.1, max_rez*1.1])
            self.chart.axes_ny.set_ylim([min_imz * 0.1, max_imz * 1.1])

        min_freq = min(self.freq)
        max_freq = max(self.freq)
        min_z = min(self.mod_z)
        max_z = max(self.mod_z)
        # min_arg = min(self.arg_z)
        # max_arg = max(self.arg_z)

        lw_bd_x, up_bd_x = self.chart.axes_bd.get_xlim()
        lw_bd_y, up_bd_y = self.chart.axes_bd.get_ylim()
        lw_arg, up_arg = self.chart.axes_secondary.get_ylim()

        # Bode Plot
        if lw_bd_x >= min_freq or max_freq >= up_bd_x or lw_bd_y >= min_z or max_z >= up_bd_y:
            self.chart.axes_bd.set_xlim([min_freq*0.9, max_freq*1.1])
            self.chart.axes_bd.set_ylim([min_z * 0.9, max_z * 1.1])

        # if lw_arg >= min_arg or max_arg >= up_arg:
        #     self.chart.axes_secondary.set_ylim([min_arg * 0.9, max_arg * 1.1])

        # if not self.chart.axes_ny.get_xlim()[0] <= self.re_z[-1] <= self.chart.axes_ny.get_xlim()[1]:
        #     self.chart.axes_ny.set_xlim([min(self.re_z)*1.5, max(self.re_z)*1.5])
#
        # if not self.chart.axes_ny.get_ylim()[0] <= self.im_z[-1] <= self.chart.axes_ny.get_ylim()[1]:
        #     self.chart.axes_ny.set_ylim([min(self.im_z)*1.5, max(self.im_z)*1.5])
#
        # if not self.chart.axes_bd.get_xlim()[0] <= self.freq[-1] <= self.chart.axes_bd.get_xlim()[1]:
        #     self.chart.axes_bd.set_xlim([min(self.freq)*1.5, max(self.freq)*1.5])
#
        # if not self.chart.axes_bd.get_ylim()[0] <= self.mod_z[-1] <= self.chart.axes_bd.get_ylim()[1]:
        #     self.chart.axes_bd.set_ylim([min(self.mod_z)*1.5, max(self.mod_z)*1.5])
#
        # if not self.chart.axes_secondary.get_ylim()[0] <= self.arg_z[-1] <= self.chart.axes_secondary.get_ylim()[1]:
        #     self.chart.axes_secondary.set_ylim([min(self.arg_z), max(self.arg_z)])

        self.chart.canvas.draw()


def fit_(circuit, x, z):
    """
    Fits the data with the given model. And predicts impedance from model. Uses impedance.py.

    :param
    -------------------------
    circuit: CostumCircuit for impedance.py
        equivalent circuit

    x: ndarray
        Contains the frequencies for fitting

    z: ndarray of complex128
        Is a complex array with the experimental impedance data (z_real + z_im*1j)

    :return:
    -------------------------
    y_fit: ndarray of complex128
        Contains the predicted impedance from the given model

    parameter: ndarray
        Optimized parameters

    error: ndarray
        Error of the parameters
    """

    circuit.fit(x, z)
    y_fit = circuit.predict(x)
    parameters = circuit.parameters_
    error = circuit.conf_

    #freqX = np.logspace(x[0], x[-1], 1000)
    freqX = np.logspace(np.log10(x[0]), np.log10(x[-1]), 1000)
    ZfitY = circuit.predict(freqX)

    print('----------------------------------------- Fiting -----------------------------------------')
    print(circuit)

    return y_fit, parameters, error, circuit, freqX, ZfitY


class NewTabGUI:
    """
    Creates a new tab. Allows management of the collected or loaded data.

    """

    def __init__(self, master, server=None, client=None, label='New tab'):
        """
        Adds a new tab in notebook

        :param
        -----------------------------
        master: ttk.Notebook

        label: str

        """
        self.master = master
        self.label = label
        self.fit_idx = 1
        self.tab = Frame(self.master, bd=0)
        self.master.add(self.tab, text=self.label)
        self.server = server
        self.client = client

        head_frame = Frame(self.tab, bg="white")
        head_frame.pack(side=TOP, fill=X)

        self.chart = ImpedanceChart(self.tab)

        self.data_array: np.ndarray
        self.headers = ['freq', 'z_re', 'z_im', 'z']

        Button(head_frame, text="x", command=self.close_tab, width=2, height=1, bg="tomato2", bd=1).pack(side=RIGHT,
                                                                                                         anchor='n')

        imgsync = Image.open('icon_sync_data.jpg')
        imgsync = imgsync.resize((30, 25))
        self.imgsync = ImageTk.PhotoImage(imgsync)

        b_sync = Button(head_frame, bg='white', image=self.imgsync, command=self.sync)
        b_sync.pack(side=LEFT, fill=BOTH)
        ToolTip(b_sync, tip_text='Send to Clients')

        imgtab = Image.open('icon_tabular_icon.jpg')
        imgtab = imgtab.resize((30, 25))
        # Image needs to be stored in a global variable , so python don't erase it
        self.imgtab = ImageTk.PhotoImage(imgtab)

        b_tabel = Button(head_frame, bg='white', image=self.imgtab, command=lambda: self.show_table(b_tabel))
        b_tabel.pack(side=LEFT, fill=BOTH)
        ToolTip(b_tabel, tip_text='Show table')

        imgxl = Image.open('icon_excel_logo.jpg')
        imgxl = imgxl.resize((30, 25))
        self.imgxl = ImageTk.PhotoImage(imgxl)

        imgcsv = Image.open('icon_csv_logo.jpg')
        imgcsv = imgcsv.resize((30, 25))
        self.imgcsv = ImageTk.PhotoImage(imgcsv)

        b_2xl = Button(head_frame, bg='white', image=self.imgxl, command=lambda: self.save(extension='.xlsx'), bd=1)
        b_2xl.pack(side=LEFT, fill=BOTH)
        ToolTip(b_2xl, tip_text="Expot to Excel file")
        b_2csv = Button(head_frame, bg='white', image=self.imgcsv, command=lambda: self.save(extension='.csv'), bd=1)
        b_2csv.pack(side=LEFT, fill=BOTH)
        ToolTip(b_2csv, tip_text="Expot to CSV file")

        self.e_name = Entry(head_frame, bg='white smoke', width=40)
        self.e_name.pack(side=LEFT, fill=Y, padx=2)
        # removing extension from file name
        label = self.label
        label = label.replace('.xlsx', '')
        label = label.replace('.csv', '')
        self.e_name.insert(0, label)

        # Getting the canvas that holds the FigureCanvasTkAgg
        rmm = RightMouse(self.chart.canvas.get_tk_widget(), event='<Alt-Button-3>')
        self.my_fittings = Menu(rmm.menu, tearoff=0)
        rmm.menu.add_cascade(label='Fittings', menu=self.my_fittings)
        rmm.add_item('Clear fittings', self.clear_fittings)

        # self.chart.canvas.get_tk_widget().bind('<Enter>', lambda e: self.highligth(e))
        # self.chart.canvas.get_tk_widget().bind('<Leave>', lambda e: self.lowligth(e))

    def close_tab(self):
        answer = messagebox.askquestion(f'Close tab: {self.label}?', 'Are you sure you want to close this tab?'
                                                                     '\nAny unsaved data will be lost, '
                                                                     'make sure you save your data before closing')
        if answer == 'no':
            pass
        elif answer == 'yes':
            self.master.remove_tab(self)  # removing tab register from tabs_list
            self.tab.destroy()

    def sync(self):
        self.get_data()
        arr = {'name': self.label,
               'append': False,
               'data': {'freq': np.ndarray.tolist(self.data_array[:, 0]),
                        'z_re': np.ndarray.tolist(self.data_array[:, 1]),
                        'z_im': np.ndarray.tolist(self.data_array[:, 2]),
                        'mod_z': np.ndarray.tolist(self.data_array[:, 3]),
                        'arg_z': np.ndarray.tolist(self.data_array[:, 4])},
               'condition': 'complete'}
        json_string = json.dumps(arr)
        if self.server.online and self.server.clients:
            for client in self.server.clients:

                self.server.stream2client(client, json_string)

    def fitting(self, circuit, initial_guess, cons, button=None, window=None):
        """
        fitting methods fits the model to the results and plots the fitting

        :param
        --------------------------------
        circuit: str
            string with the circuit model

        initial_guess: list or ndarray
            contains initial values for fitting algorithm

        :return:
        --------------------------------
        para: list of floats
            contains the fitted parameters

        para_error: list of floats
            contains the error associated to the parameters
        """
        def mod_(array):
            """
            Calculates the module of a complex array
            :param array: complex ndarray
                impedance array
            :return: ndarray
                module of impedance
            """
            mod_array = np.sqrt(array.real ** 2 + array.imag ** 2)
            return mod_array

        # Building circuit
        circuit = CustomCircuit(circuit, initial_guess=initial_guess, constants=cons)
        # getting stored data
        freq, Re_Z, Im_Z, mod_z = self.get_data()

        # Removing Nan and inf from ndarray
        freq[~np.isfinite(freq)] = 0
        Re_Z[~np.isfinite(Re_Z)] = 0
        Im_Z[~np.isfinite(Im_Z)] = 0
        mod_z[~np.isfinite(mod_z)] = 0

        # Selecting the points to fit
        if window is not None:
            freq = freq[window[0]: window[1]]
            Re_Z = Re_Z[window[0]: window[1]]
            Im_Z = Im_Z[window[0]: window[1]]
            mod_z = mod_z[window[0]: window[1]]

        # making complex array for fitting
        Z = Re_Z + (-1j*Im_Z)

        # fitting
        Z_fit, para, para_error, circuit, freqX, ZfitY = fit_(circuit=circuit, x=freq, z=Z)
        Re_Z_fit = np.real(ZfitY)
        Im_Z_fit = np.imag(ZfitY)

        mod_z_fit = mod_(Z_fit)  # For Chi square calculation
        modZfitY = mod_(ZfitY)  # For plotting

        df = len(mod_z) - 1
        pvalue = 1-0.01
        # TODO check chi square for non-linear fitting (Antonio's link)
        chi2 = np.sum((mod_z_fit - mod_z) ** 2 / mod_z_fit)
        critical_chi2 = stats.chi2.ppf(pvalue, df=df)

        print(u'Chi-square Goodness of Fit test:\n'
              f'\tDegrees of Freedom: {df} \n'
              f'\tConfidence level: {round(pvalue*100,1)} %\n'
              u'\t\u03C7^2 = ' + str(chi2) +
              f'\n\tCritical ' + u'\u03C7^2 = ' + str(critical_chi2))

        # getting parameters list to save in fit_buf
        params_txt = f'{window[0]}\n{window[1]}\n{circuit.circuit}\n'
        init_txt = f'{window[0]}\n{window[1]}\n{circuit.circuit}\n'
        if cons is not None:
            cons = list(cons.values())  # converting dic values to list
        j = 0
        for i, item in enumerate(initial_guess):
            if item is not None:
                i -= j
                params_txt += f'{para[i]}\n'
                init_txt += f'{item}\n'
            else:
                params_txt += f'{cons[j]}\n'
                init_txt += f'{cons[j]}\n'
                j += 1

        with open('fit_buf', 'w') as buffer:
            buffer.write(params_txt)
        with open('init_buf', 'w') as buffer:
            buffer.write(init_txt)

        # Plot fitting
        s_fitting = NewSeries(self.chart, style='-')
        s_fitting.add_coordinates_nd(-Im_Z_fit, Re_Z_fit, freqX, modZfitY)

        # Getting fitting lines properties to display in the right menu
        fitting_lines = self.chart.series_list[-1]
        color = fitting_lines[0].get_color()
        idx = self.fit_idx  # Getting the current index for proper label of the fitting parameters
        self.my_fittings.add_command(label=f'Fitting {self.fit_idx}',
                                     command=lambda: FittingParams(circuit,
                                                                   [chi2, critical_chi2, df, round(pvalue*100, 1)],
                                                                   idx,
                                                                   name=self.e_name.get(),
                                                                   lines=fitting_lines[:2],
                                                                   chart=self.chart),
                                     foreground=color)

        self.fit_idx += 1

        if button is not None:
            button['state'] = NORMAL  # Button from Fitting Editor
        return para, para_error, circuit.get_param_names(), [chi2, critical_chi2, df]

    def get_data(self):
        """
        get the data stored in the graphs and saves it in self.data_array.

        :return:
        ------------------------
        freq: ndarray
            frequencies

        z_re: ndarray
            real impedance

        z_im: ndarray
            imaginary impedance

        """
        line_ny, line_bd, line_bd2 = self.chart.series_list[0]
        z_re = np.array(line_ny.get_xdata())
        z_im = np.array(line_ny.get_ydata())
        freq = np.array(line_bd.get_xdata())
        z = np.array(line_bd.get_ydata())

        arg_z = np.array(line_bd2.get_ydata())

        data_array = np.array([freq, z_re, z_im, z, arg_z])
        self.data_array = np.transpose(data_array)
        return freq, z_re, z_im, z

    def save(self, extension=None, path=None):
        """
        Saves the data to a csv or a xlsx.
        """
        def save2csv(path):
            try:
                if path.find('.csv') == -1:
                    path += '.csv'
                with open(path, 'w') as file:
                    # file.write(tech + '-tear-\n')  # Adding flag
                    file.write(f"Freq/Hz,Z'/Ohm,-Z''/Ohm,modZ/Ohm,Phase/º\n")
                    for item in self.data_array:
                        file.write(f'{item[0]},{item[1]},{item[2]},{item[3]},{item[4]}\n')
            except PermissionError:
                messagebox.showerror('Permission Denied!', f'It was not possible to modify {file}. '
                                                           f'Make sure this file is closed and try again!')

        # making sure that data was collected
        self.get_data()

        if path is None:
            # Opening file and writing
            #self.extension.get()
            if extension == '.csv':
                filepath = filedialog.asksaveasfilename(title='Save to file', initialfile=f'{self.e_name.get()}.csv',
                                                    filetypes=(('CSV', '*.csv'), ('All files', "*.*")))
                save2csv(filepath)
            #self.extension.get()
            elif extension == '.xlsx':
                file = filedialog.asksaveasfilename(title='Save to file', initialfile=f'{self.e_name.get()}.xlsx',
                                                    filetypes=(('Excel', '*.xlsx'), ('All files', "*.*")))

                data_frame = pd.DataFrame(self.data_array, columns=[f"Freq/Hz",
                                                                    "Z'/Ohm,",
                                                                    "-Z''/Ohm",
                                                                    "modZ/Ohm",
                                                                    "Phase/º"])
                try:
                    if file.find('.xlsx') == -1:
                        file += '.xlsx'
                    data_frame.to_excel(file, index=False, engine='openpyxl')
                except PermissionError:
                    messagebox.showerror('Permission Denied!', f'It was not possible to modify {file}. '
                                                               f'Make sure this file is closed and try again!')
        else:
            save2csv(path)

    def show_table(self, btn):
        """
        Displays a window with the numerical data of the plots.

        """
        def good_bye_table():
            top.destroy()
            btn['state'] = NORMAL

        self.get_data()
        btn['state'] = DISABLED
        top = Toplevel()
        top.iconbitmap(r'group-30_116053.ico')
        top.resizable(0, 0)
        top.title(f'Table - {self.e_name.get()}')
        top.geometry('550x500')
        top.protocol("WM_DELETE_WINDOW", good_bye_table)
        my_tree = ttk.Treeview(top)
        my_tree['columns'] = ('Row', 'Frequency', 'Z_real', 'Z_imag', 'Mod_Z', 'Arg_Z')

        # Preparing tree view
        my_tree.column('#0', width=0, stretch=NO)
        my_tree.column('Row', width=35, minwidth=35, stretch=NO)
        my_tree.column('Frequency', width=100, minwidth=100)
        my_tree.column('Z_real', width=100, minwidth=100)
        my_tree.column('Z_imag', width=100, minwidth=100)
        my_tree.column('Mod_Z', width=100, minwidth=100)
        my_tree.column('Arg_Z', width=100, minwidth=100)

        my_tree.heading('#0', text="", anchor=W)
        my_tree.heading('Row', text='Row', anchor=W)
        my_tree.heading('Frequency', text='Frequency/ Hz', anchor=W)
        my_tree.heading('Z_real', text=u"Z'/\u2126", anchor=W)
        my_tree.heading('Z_imag', text=u"-Z''/\u2126", anchor=W)
        my_tree.heading('Mod_Z', text=u'Mod_Z/\u2126', anchor=W)
        my_tree.heading('Arg_Z', text='Phase/º', anchor=W)

        my_yscrollbar = ttk.Scrollbar(top)
        my_yscrollbar.configure(command=my_tree.yview)
        my_tree.configure(yscrollcommand=my_yscrollbar.set)
        my_yscrollbar.pack(side=RIGHT, fill=Y)

        my_tree.pack(fill=BOTH, expand=1)

        # Adding tabular data to treeview
        for i, item in enumerate(self.data_array):
            my_tree.insert(parent='', index=i, iid=i, text="", value=(i, item[0], item[1], item[2], item[3], item[4]))

        # Creating frame to hold check buttons
        my_frame = Frame(top)
        my_frame.pack()

        indices = ["Freq", "Z'", "-Z''", "Mod Z", "Phase"]

        var0, var1, var2, var3, var4 = IntVar(), IntVar(), IntVar(), IntVar(), IntVar()
        chk_btn1 = Checkbutton(my_frame, text=indices[0], variable=var0, onvalue=1)
        chk_btn2 = Checkbutton(my_frame, text=indices[1], variable=var1, onvalue=2)
        chk_btn3 = Checkbutton(my_frame, text=indices[2], variable=var2, onvalue=3)
        chk_btn4 = Checkbutton(my_frame, text=indices[3], variable=var3, onvalue=4)
        chk_btn5 = Checkbutton(my_frame, text=indices[4], variable=var4, onvalue=5)

        chk_btn1.pack(side=LEFT)
        chk_btn2.pack(side=LEFT)
        chk_btn3.pack(side=LEFT)
        chk_btn4.pack(side=LEFT)
        chk_btn5.pack(side=LEFT)

        chk_btn2.select()
        chk_btn3.select()

        Button(top, text="Copy to Clipboard",
               command=lambda: self.copy2clbd(top, [var0.get(), var1.get(), var2.get(), var3.get(), var4.get()], indices),
               bg='azure2').pack()
        top.mainloop()

    def copy2clbd(self, master, idxs, indices):
        """
        Copying data to clipboard in a \t delimited text
        :param master: widget to call clipboard function
        :param idxs: indexes of the columns to be copied
        :param indices: columns headings of the data array
        :return: clipboard containing data. Can be pasted in txt files, excel tables or origin workbooks
        """

        # Selecting only the interested indexes
        idxs = [i-1 for i in idxs if i != 0]

        # Filtrate headings and converting to \t delimited text
        my_headings = [indices[i] for i in idxs]
        my_str = ''
        length = len(my_headings)
        for i, item in enumerate(my_headings):
            if i == length-1:  # to remove the extra \t from the string
                my_str = my_str + item
            else:
                my_str = my_str + item + '\t'
        my_str = my_str + '\n'

        # Filtrating data nad convert to \t delimited text
        str_row = ''
        my_data = self.data_array[:, idxs]
        for row in my_data:
            length = len(row)
            for i, item in enumerate(row):
                if i == length-1:
                    str_row += f'{item}'
                else:
                    str_row += f'{item}\t'
            str_row += '\n'

        # Joining headings and data together in \t delimited text
        my_str = my_str + str_row

        # Clearing clipboard and updating new data
        master.clipboard_clear()
        master.clipboard_append(my_str)

    def clear_fittings(self):
        fitting_series = self.chart.series_list[1:]

        # Removing fitting lines from series_list
        self.chart.series_list = [self.chart.series_list[0]]

        # Removing lines from plot
        for lines in fitting_series:
            # lines = [fitting_line, bd_line, bd2_line]

            lines[0].remove()
            lines[1].remove()

        self.chart.canvas.draw()

    def display_params(self, data):
        print(data)

    def highligth(self, e):
        line = self.chart.series_list[0][0]
        line.set_markersize(10)
        line.set_markeredgecolor('powderblue')
        line.set_markeredgewidth(2)
        self.chart.canvas.draw()

    def lowligth(self, e):
        line = self.chart.series_list[0][0]
        line.set_markersize(6)
        line.set_markeredgewidth(0)
        self.chart.canvas.draw()


class FittingParams:
    """
    Makes a class of the
    """
    def __init__(self, circuit, stats, idx, name='', lines=None, chart=None):
        if lines is not None:
            self.lines = lines
        if chart is not None:
            self.chart = chart

        self.top = Tk()
        self.top.iconbitmap(r'group-30_116053.ico')
        # self.top.resizable(0, 0)
        self.top.title(f'Parameters - Fitting {name}:::{idx}')
        # self.top.geometry('550x400')
        self.top.attributes('-topmost', 'true')

        my_canvas = Canvas(self.top, height=5, bg=self.lines[0].get_color())
        my_canvas.pack()

        self.my_tree = ttk.Treeview(self.top)
        self.my_tree['columns'] = ('variable', 'value', 'units')

        self.my_tree.column('#0', width=100, stretch=NO)
        self.my_tree.column('variable', width=100, minwidth=35, stretch=NO)
        self.my_tree.column('value', width=200, minwidth=100)
        self.my_tree.column('units', width=100, minwidth=100)

        self.my_tree.heading('#0', text=f"Fitting {idx}", anchor=W)
        self.my_tree.heading('variable', text='Variable', anchor=W)
        self.my_tree.heading('value', text='Value', anchor=W)
        self.my_tree.heading('units', text="Units", anchor=W)

        my_yscrollbar = ttk.Scrollbar(self.top)
        my_yscrollbar.configure(command=self.my_tree.yview)
        self.my_tree.configure(yscrollcommand=my_yscrollbar.set)
        my_yscrollbar.pack(side=RIGHT, fill=Y)

        self.my_tree.pack(fill=BOTH, expand=1)

        self.my_tree.insert(parent='', index=0, iid=0, text="Constants")

        const = [list(circuit.constants.keys()), list(circuit.constants.values())]
        for i, name in enumerate(const[0]):
            self.my_tree.insert(parent='0',
                                index=i + 1,
                                iid=i + 1,
                                text='',
                                values=(name, const[1][i], ''))

        j = const[0].__len__() + 1
        self.my_tree.insert(parent='', index=j, iid=j, text="Initial guess")
        names = circuit.get_param_names()
        init_guess = circuit.initial_guess
        for i, name in enumerate(names[0]):
            self.my_tree.insert(parent=str(j),
                                index=i+j+1,
                                iid=i+j+1,
                                text='',
                                values=(name, init_guess[i], names[1][i]))

        j = j + names[0].__len__() + 1
        self.my_tree.insert(parent='', index=j, iid=j, text="Fitting")
        self.my_tree.item(j, open=True)  # Pre expanding the Fitting node
        params = circuit.parameters_
        errors = circuit.conf_
        for i, name in enumerate(names[0]):
            self.my_tree.insert(parent=str(j),
                                index=i+j+1,
                                iid=i+j+1,
                                text='',
                                values=(name, f'{params[i]} +- {errors[i]}', names[1][i]))

        j = j + names[0].__len__() + 1
        self.my_tree.insert(parent='', index=j, iid=j, text="Statistics")
        self.my_tree.item(j, open=True)  # Pre expanding the Fitting node
        self.my_tree.insert(parent=str(j), index=j+1, iid=j+1, text="", value=('DF', stats[2], ''))
        self.my_tree.insert(parent=str(j), index=j+2, iid=j+2, text="", value=(u'\u03A7\u00B2', stats[0], ''))
        self.my_tree.insert(parent=str(j), index=j+3, iid=j+3, text="", value=(u'Critical \u03A7\u00B2', stats[1], ''))
        self.my_tree.insert(parent=str(j), index=j+4, iid=j+4, text="", value=('Confidence', stats[3], '%'))

        Button(self.top, text='Copy', command=self.copy_this, bg='azure2').pack()

        self.plot_again()

        self.top.mainloop()

    def plot_again(self):
        """
        Plotting the fitting saved in this class
        :return:
        """
        # TODO check duplicated lines. how to prevent and if need to prevent
        self.chart.axes_ny.add_line(self.lines[0])
        self.chart.axes_bd.add_line(self.lines[1])

        # Re adding lines to series list. To enable delete fittings with clear fittings
        self.chart.series_list.append(self.lines)

        self.chart.canvas.draw()

    def copy_this(self):
        id = int(self.my_tree.selection()[0])
        value = list(self.my_tree.item(id).values())[2][1]
        self.top.clipboard_clear()
        self.top.clipboard_append(value)


class FittingEditor:
    def __init__(self, cnb):
        self.cnb = cnb  # fitting function from the specific chart
        self.b_fit = None
        self.checks = []
        self.parameters = []

        self.lw_bound = 0
        self.up_bound = 100
        self.values = [1, 1, 3000, 0.1, 0.000001, 0.9]
        self.eq_circ = 'R0-p(R1-Wo1,CPE1)'
        self.get_from_buffer(initial=False)

        # Initializing entries
        self.top = None
        self.lw_e = None
        self.up_e = None
        self.circuit_entry = None

    def open(self, root, menu):
        def good_bye_editor():
            menu.entryconfigure(4, state=NORMAL)
            self.top.destroy()

        menu.entryconfigure(4, state=DISABLED)
        self.top = Toplevel()
        self.top.resizable(0, 0)
        # self.top.attributes('-topmost', 'true')
        self.top.transient(root)
        self.top.title('Fitting Editor')
        self.top.protocol("WM_DELETE_WINDOW", good_bye_editor)

        bound_frame = LabelFrame(self.top, text='Data Window (indexes)')
        self.lw_e = Entry(bound_frame)
        self.lw_e.pack(side=LEFT)
        self.lw_e.insert(0, str(self.lw_bound))
        self.up_e = Entry(bound_frame)
        self.up_e.pack(side=LEFT)
        self.up_e.insert(0, str(self.up_bound))
        bound_frame.pack(pady=10)

        circ_frame = LabelFrame(self.top, text='Equivalent Circuit')
        circ_frame.pack(fill=BOTH, expand=1)
        inner_frame = Frame(circ_frame)
        inner_frame.pack()
        btn_last = Button(inner_frame, text='Last initial guess', bg='pale green', command=self.build_from_buffer)
        btn_last.pack(side=LEFT, fill=X)
        btn_last = Button(inner_frame, text='Last calculated fit', bg='bisque2',
                          command=lambda: self.build_from_buffer(initial=False))
        btn_last.pack(side=LEFT, fill=X)

        self.circuit_entry = Entry(circ_frame, width=30)
        self.circuit_entry.pack(side=LEFT, fill=BOTH, expand=1, padx=2)
        # circuit_entry.bind('<Any-KeyRelease>', build_entries)
        self.circuit_entry.insert(0, self.eq_circ)

        btn = Button(inner_frame, text='Use Default', command=self.build_entries, bg='azure2')
        btn.pack(side=LEFT, fill=X)

        para_frame = LabelFrame(self.top, text='Parameters')

        self.build_entries(default=True)

        self.top.mainloop()

    def build_entries(self, e=None, default=True):
        """
        Updates the parameters of the equivalent circuit
        """
        if not default:
            self.circuit_entry.delete(0, END)
            self.circuit_entry.insert(0, self.eq_circ)

        # Getting the para_frame
        self.top.winfo_children()[-1].destroy()

        para_frame = LabelFrame(self.top, text='Parameters')
        para_frame.pack()

        para_frame1 = Frame(para_frame)
        para_frame1.pack(side=LEFT)
        para_frame2 = Frame(para_frame)
        para_frame2.pack(side=LEFT)
        para_frame3 = Frame(para_frame)
        para_frame3.pack(side=LEFT)

        self.eq_circ = self.circuit_entry.get()
        string = self.eq_circ.replace(' ', '')

        # global parameters, checks
        self.parameters = []
        self.checks = []
        elmt_id = 0
        # Adding the parameters to the screen
        for i, char in enumerate(string):
            """ Checking the elements of the equivalent circuit and displaying the respective parameters"""
            if char == 'R':
                Label(para_frame1, text=f'{string[i:i + 2]}/' + u"\u2126").pack(pady=2)
                self.parameters.append(string[i:i + 2])
                e = Entry(para_frame2)
                e.pack(pady=3)

                if default:
                    e.insert(0, '1')
                else:
                    e.insert(0, self.values[elmt_id])
                elmt_id += 1

                var = IntVar()
                self.checks.append(var)
                Checkbutton(para_frame3, onvalue=1, offvalue=0, variable=var).pack()

            if char == 'W':
                if string[i:i + 2] == 'Ws' or string[i:i + 2] == 'Wo':
                    Label(para_frame1, text='Z0/' + u"\u2126").pack(pady=2)
                    self.parameters.append(f'{string[i:i + 3]}_0')
                    Label(para_frame1, text='tau/s').pack(pady=2)
                    self.parameters.append(f'{string[i:i + 3]}_1')
                    e = Entry(para_frame2)
                    e.pack(pady=3)
                    if default:
                        e.insert(0, '3000')
                    else:
                        e.insert(0, self.values[elmt_id])
                    elmt_id += 1

                    e = Entry(para_frame2)
                    e.pack(pady=3)
                    if default:
                        e.insert(0, '0.1')
                    else:
                        e.insert(0, self.values[elmt_id])
                    elmt_id += 1

                    var1 = IntVar()
                    self.checks.append(var1)
                    Checkbutton(para_frame3, onvalue=1, offvalue=0, variable=var1).pack()
                    var2 = IntVar()
                    self.checks.append(var2)
                    Checkbutton(para_frame3, onvalue=1, offvalue=0, variable=var2).pack()

            if char == 'C':
                if string[i:i + 3] == 'CPE':
                    Label(para_frame1, text='Q/' + u'u\u2126^-1 s^-\u03B1').pack(pady=2)
                    self.parameters.append(f'{string[i:i + 4]}_0')
                    e = Entry(para_frame2)
                    e.pack(pady=3)
                    if default:
                        e.insert(0, '0.000001')
                    else:
                        e.insert(0, self.values[elmt_id])
                    elmt_id += 1

                    Label(para_frame1, text=u'\u03B1').pack(pady=2)
                    self.parameters.append(f'{string[i:i + 4]}_1')
                    e = Entry(para_frame2)
                    e.pack(pady=3)
                    if default:
                        e.insert(0, '0.9')
                    else:
                        e.insert(0, self.values[elmt_id])
                    elmt_id += 1

                    var1 = IntVar()
                    self.checks.append(var1)
                    Checkbutton(para_frame3, onvalue=1, offvalue=0, variable=var1).pack()
                    var2 = IntVar()
                    self.checks.append(var2)
                    var2.set(1)
                    Checkbutton(para_frame3, onvalue=1, offvalue=0, variable=var2).pack()

                elif string[i:i + 3] != 'CPE':
                    Label(para_frame1, text=f'{string[i:i + 2]}/F').pack(pady=2)
                    self.parameters.append(string[i:i + 2])

                    e = Entry(para_frame2)
                    e.pack(pady=3)
                    if default:
                        e.insert(0, '0.000001')
                    else:
                        e.insert(0, self.values[elmt_id])
                    elmt_id += 1

                    var = IntVar()
                    self.checks.append(var)
                    Checkbutton(para_frame3, onvalue=1, offvalue=0, variable=var).pack()

        # b_fit = Button(para_frame, text='Apply Fitting', command=apply_fit, bg='azure2')
        self.b_fit = Button(para_frame, text='Apply Fitting',
                            command=lambda: threading.Thread(target=self.call_apply_fit).start(), bg='azure2')
        self.b_fit.pack(fill=BOTH, expand=1, side=BOTTOM)

    @staticmethod
    def get_buffer(file_name):
        """ Reads one of the buffer files and returns the equivalent circuit and the initial guess"""
        with open(file_name, 'r') as file:
            buffer = file.read()

        buffer = buffer.split('\n')
        return buffer[2], buffer[3:-1], buffer[0:2]

    def get_from_buffer(self, initial=True):
        try:
            if initial:
                eq_circ, values, window = self.get_buffer(file_name='init_buf')
            else:
                eq_circ, values, window = self.get_buffer(file_name='fit_buf')

            self.values = values
            self.eq_circ = eq_circ
            self.lw_bound = int(window[0])
            self.up_bound = int(window[1])
        except FileNotFoundError:
            pass

    def build_from_buffer(self, **kwargs):
        """
        Build entries based on data saved at the buffers
        """
        self.get_from_buffer(**kwargs)
        self.build_entries(default=False)

    def call_apply_fit(self):
        """
        updates the state of buttons and self.values and calls the apply fit
        """

        # Making sure self.value is updated
        # Getting the list of entries
        # path             para_frame              para_frame2          entries
        entries_list = self.top.winfo_children()[-1].winfo_children()[1].winfo_children()
        self.values = [float(entry.get()) for entry in entries_list]

        self.lw_bound = int(self.lw_e.get())
        self.up_bound = int(self.up_e.get())

        self.b_fit['state'] = DISABLED
        try:
            self.apply_fit()
        except ValueError or IndexError:
            # If user does not press OK
            self.build_entries()  # Update entries
        self.b_fit['state'] = NORMAL

    def apply_fit(self):
        """
        Gets the values for the fitting and calls the respective fitting function from the active tab
        """
        # Finding respective fitting function from all tabs
        cost_tab = self.cnb.get_costume_tab()
        func = cost_tab.fitting  # Getting standby function for fittings

        initial_guess = [float(val) for val in self.values]
        # Getting constants
        cons = {}
        for i, check in enumerate(self.checks):
            if check.get():
                cons[self.parameters[i]] = initial_guess[i]
                initial_guess[i] = None

        circuit = self.eq_circ
        # circuit = self.circuit_entry.get()
        circuit = circuit.replace(' ', '')

        window = [self.lw_bound, self.up_bound]

        # Fitting function
        if len(cons) == 0:
            params, error, elements, stats = func(circuit=circuit, initial_guess=initial_guess, cons=None, window=window)
        else:
            params, error, elements, stats = func(circuit=circuit, initial_guess=initial_guess, cons=cons, window=window)

        return params, error, elements, stats

