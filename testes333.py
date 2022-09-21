from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from impedance import preprocessing
import numpy as np

import serialcom
import tkinter_tools_module as TTm
import threading
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from impedance.models.circuits import CustomCircuit
from impedance import preprocessing
import matplotlib.pyplot as plt
from impedance.visualization import plot_nyquist
from tkinter.messagebox import showinfo
from tkinter import filedialog
import serial.tools.list_ports
import serial


def bind_this(widget):
    def select(e):
        widget.config(bg='grey')

    def de_select(e):
        widget.config(bg='white')

    widget.bind('<Enter>', select)
    widget.bind('<Leave>', de_select)


def circuit_updater(fun):
    def wrapper(self):
        global my_blank
        my_blank.destroy()
        fun(my_blank.master)
        my_blank = add_blank(root)

    return wrapper


class BaseElement:
    def __init__(self, master, symbol, parameters, para_name):
        self.parameters = parameters
        self.para_name = para_name

        self.frame = Frame(master, borderwidth=4, bg='white')
        self.frame.pack()
        Label(self.frame, text=symbol, bg='white').pack(fill=BOTH, expand=1)

        self.labels = []
        self.entries = []
        self.add_parameters()

        # bind_this(self.frame)

    def add_parameters(self):
        for i, para in enumerate(self.parameters):
            inner_frame = Frame(self.frame, bg='white')
            inner_frame.pack(fill=BOTH, expand=1)
            Label(inner_frame, text=self.para_name[i], bg='white').pack(side=LEFT)
            e = Entry(inner_frame, width=5)
            e.insert(0, para)
            e.pack(side=LEFT)


@circuit_updater
class Resistor(BaseElement):
    def __init__(self, master):
        symbol = 'Resistor'
        resistance = 0.01  # Ohm
        para_name = ['R/Ohm =']
        parameters = [resistance]
        super().__init__(master, symbol, parameters, para_name)


@circuit_updater
class WarburgOpen(BaseElement):
    def __init__(self, master):
        symbol = 'Warburg Open'
        z0 = 1000  # Ohm
        tau = 1  # s
        para_name = ['Z0/Ohm =', 'Tau/s =']
        parameters = [z0, tau]
        super().__init__(master, symbol, parameters, para_name)


@circuit_updater
class Capacitor(BaseElement):
    def __init__(self, master):
        symbol = 'Capacitor'
        c = 0.01  # Farad
        para_name = ['c/F =']
        parameters = [c]
        super().__init__(master, symbol, parameters, para_name)


@circuit_updater
class CPE(BaseElement):
    def __init__(self, master):
        symbol = 'CPE'
        q = 1  # Ohm^-1/s^a
        alpha = 1
        para_name = [u'Q/1/(\u2126*s) =', u'\u03B1/s =']
        parameters = [q, alpha]
        super().__init__(master, symbol, parameters, para_name)


@circuit_updater
def parallel(master):
    add_blank(master, where=TOP)
    add_blank(master)


def add_blank(master, where=LEFT):
    frame = Frame(master, borderwidth=4, bg='white')
    frame.pack(side=where)
    my_label = Label(frame, width=15, height=5, text='Add element', bg='white')
    my_label.pack()

    bind_this(frame)

    my_menu = TTm.RightMouse(my_label)
    my_menu.add_item('Add Resistor', _command=lambda: Resistor(frame))
    my_menu.add_item('Add Warburg Open', _command=lambda: WarburgOpen(frame))
    my_menu.add_item('Add Capacitor', _command=lambda: Capacitor(frame))
    my_menu.add_item('Add CPE', _command=lambda: CPE(frame))
    my_menu.add_item('Add Parallel split', _command=lambda: parallel(frame))

    return my_label


root = Tk()
root.state('zoomed')

my_blank = add_blank(root)

root.mainloop()