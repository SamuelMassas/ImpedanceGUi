from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import serialcom
import tkinter_tools_module as TTm
import threading
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)


def function():
    pass


def connection():
    # Creates the window that opens when option connection is selected from the menu
    top = Toplevel()
    top.geometry("400x400")
    top.resizable(False, False)

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
            serialcom.read_port(channel)
        else:
            # if connection is not established successfully to the desired port
            statusbar.config(text="Connection failed")
            main_status.config(text="Connection failed")

    def scroll_function(event):
        print(event)
        if event.delta > 0:
            my_listbox.xview_scroll(-1, "unit")
        else:
            my_listbox.xview_scroll(1, "unit")

    # creates the input for the bauds number
    f_properties = LabelFrame(top, text="Connection properties")
    f_properties.pack()
    l_bauds = Label(f_properties, text="Bauds")
    bauds = Entry(f_properties, fg="grey")
    bauds.insert(0, 9600)
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
    b_close = Button(top, text="Save and Close", width=20, command=top.destroy)
    b_connect.pack()
    b_refresh.pack()
    b_close.pack()

    # automatically updates the list of available ports
    refresh_listbox()


def start_coms():
    # Tells the microcontroller to start, and updates the current action in Active_control variable
    global Active_control
    if Active_control == "Start":
        pass
    else:
        Active_control = "Start"
        try:
            serialcom.write_port(channel, b'Start!')
            condition = 1
            counter = 1
            xx = []
            yy = []
            while condition:
                data = str(serialcom.read_port(channel))
                data_vector = data.split("\t")

                if data == "finish\r\n":
                    condition = 0
                elif data == "Stop\r\n":
                    condition = 0


                # unpack data values
                try:
                    point = float(data_vector[0])
                    feq = float(data_vector[1])
                    v_re = float(data_vector[2])
                    v_im = float(data_vector[3])
                    i_re = float(data_vector[4])
                    i_im = float(data_vector[5])
                    mod_z = float(data_vector[6])
                    arg_z = float(data_vector[7])
                except ValueError:
                    v_re = 1 + 2*counter
                    v_im = 1 + counter
                    i_re = 1
                    i_im = 1

                # Calculating impedance
                z_re = v_re/i_re
                z_im = v_im/i_im
                xx.append(z_re)
                yy.append(z_im)
                plot_data(xx, yy)
                print(xx, yy)

                if data == "finish\r\n":
                    condition = 0
                elif data == "Stop\r\n":
                    condition = 0

                counter += 1


        except AttributeError:
            messagebox.showwarning("Warnning", "Unable to start communication. Active port: " + channel)

        Active_control = "None"


def stop_coms():
    # Tells the microcontroller to stop
    try:
        serialcom.write_port(channel, b'Stop!')
    except AttributeError:
        messagebox.showwarning("Warnning", "Unable to stop communication. No communication occurring. Active port: " + channel)


def plot_data(xdata, ydata):
    x_upper_limit = 1
    x_lower_limit = -1
    y_upper_limit = 1
    y_lower_limit = -1

    x = xdata[-1]
    y = ydata[-1]

    # Code for graphic update
    line.set_xdata(xdata)
    line.set_ydata(ydata)

    # This block rescales the x and y range on the axes_, so that all point are shown
    if 0 < x >= x_upper_limit:
        x_upper_limit = x * 1.5
    elif x_upper_limit <= x <= 0:
        x_upper_limit = x * 0.5
    elif 0 < x <= x_lower_limit:
        x_lower_limit = x * 0.5
    elif x_lower_limit >= x < 0:
        x_lower_limit = x * 1.5

    if 0 < y >= y_upper_limit:
        y_upper_limit = y * 1.5
    elif y_upper_limit <= y <= 0:
        y_upper_limit = y * 0.5
    elif 0 < y <= y_lower_limit:
        y_lower_limit = y * 0.5
    elif y_lower_limit >= y < 0:
        y_lower_limit = y * 1.5

    graph.set_xlim(x_lower_limit, x_upper_limit)
    graph.set_ylim(y_lower_limit, y_upper_limit)

    canvas.draw()


def create_new_tab(data, label):
    new_tab = Frame(my_notebook, bd=0)
    new_tab.pack(fill="both", expand=1)
    my_notebook.add(new_tab, text=label)

    button = Button(new_tab, text="X", command=new_tab.destroy)
    button.pack(side=RIGHT)
    button = Button(new_tab, text="Table", command=lambda: show_table(data))
    button.pack(side=RIGHT)

    # Builds figure
    figure = Figure()
    graph = figure.add_subplot(111)
    graph.grid(True)
    graph.set_xlabel('Time/s')
    graph.set_ylabel('Current/uA')

    # Builds canvas
    canvas = FigureCanvasTkAgg(figure, new_tab)
    canvas.get_tk_widget().pack()
    canvas.draw()

    # Add toolbar
    toolbar = NavigationToolbar2Tk(canvas, new_tab, pack_toolbar=False)
    toolbar.update()
    toolbar.pack(side=BOTTOM, fill=X)

    return graph

def show_table(data):
    top = Toplevel()
    label = Label(top, text=str(data))
    label.pack()
    top.mainloop()


root = Tk()
root.title('Elchem')
root.iconbitmap(r'group-30_116053.ico')
root.geometry('800x500')

channel = "None"  # tracks the current serial port connected to the program
Active_technic = "None"  # tracks the current electrochemical technic and its parameters
Active_control = "None"  # tracks which actions are currently on going on the serial communication control panel

#
#
# Creates the main Menu
my_menu = Menu()
root.config(menu=my_menu)

my_file = Menu(my_menu, tearoff=0)
my_file.add_command(label="Quit", command=root.quit)
my_settings = Menu(my_menu, tearoff=0)
my_settings.add_command(label="Connection", command=connection)
my_data = Menu(my_menu, tearoff=0)

my_menu.add_cascade(label="File", menu=my_file)
my_menu.add_cascade(label="Settings", menu=my_settings)
my_menu.add_cascade(label="Data", menu=my_data)


#
# Creates the control buttons to control the serial communication
f_control = LabelFrame(root, text="Control panel")
f_control.grid(row=0, column=0, rowspan=2)

b_start = Button(f_control, text="Start", command=lambda: threading.Thread(target=start_coms).start(), padx=50, pady=10)
b_start.pack()
b_stop = Button(f_control, text="Stop", command=stop_coms, padx=50, pady=10)
b_stop.pack()


#
# Creates a label that tells the user relevant information
main_status = Label(f_control, text="Connected to: None", bd=1, fg="grey", relief=SUNKEN)
main_status.pack(fill=X)


#
# Creates the right mouse popup menu
# rm_menu = TTm.RightMouse(root).add_items(["Properties", "Analysis"], [function, function])

#
# Creates the frame and tabs for data visualization in top
f_tabframe = Frame(root, pady=20, padx=10)
f_tabframe.grid(row=1, column=1, rowspan=3)

my_notebook = ttk.Notebook(f_tabframe, width=800, height=600)
my_notebook.pack()

main_tab = Frame(my_notebook, bd=0)
main_tab.pack(fill="both", expand=1)


my_notebook.add(main_tab, text="Data")



# builds axes_ for real time data visualization
# x and y limits
x_low = -1
x_up = 1
y_low = -1
y_up = 1

# Builds figure
figure = Figure()
graph = figure.add_subplot(111)
graph.grid(True)
graph.set_xlabel('Z(RE)')
graph.set_ylabel('Z(IM)')
graph.set_xlim(x_low, x_up)
graph.set_ylim(x_low, x_up)
line = graph.plot([], [], 'bo')[0]  # var that will be used for data plot

# Builds canvas
canvas = FigureCanvasTkAgg(figure, main_tab)
canvas.get_tk_widget().pack(fill=BOTH, expand=True)
canvas.draw()

# Add toolbar
toolbar = NavigationToolbar2Tk(canvas, main_tab, pack_toolbar=False)
toolbar.update()
toolbar.pack(side=BOTTOM, fill=X)









root.state('zoomed')
root.mainloop()