import serial.tools.list_ports
import serial


def see_ports():
    """ Returns the available ports at the moment """
    return serial.tools.list_ports.comports()


def connect_to(portID, bauds):
    # makes the connection to the selected port
    try:
        ser = serial.Serial(portID, baudrate=bauds)
    except serial.serialutil.SerialException:
        ser = "None"
    return ser


def read_port(serialCOM):
    # reads on entire line from the communication port
    data = serialCOM.readline()
    data = data.decode('utf8')
    # serial.serialutil.SerialException
    return data


def write_port(serialCOM, Command):
    # writes the user command in the connected port
    serialCOM.write(Command)


# def write_read_port(serialCOM, Command):
#     # sends the command for serial communication
#     write_port(serialCOM, Command)
#
#     file = open('short_life_data.txt', 'w')
#
#     condition = 1
#     counter = 1
#     while condition:
#
#         data = str(read_port(serialCOM))
#
#         index = data.find("\r")
#         try:
#             numerical_data = int(data[0:index])
#             if counter == 1:
#                 file.write(str(numerical_data) + "  ")
#             else:
#                 file.write(str(numerical_data) + "\n")
#                 counter = 0
#             counter = counter + 1
#         except ValueError:
#             pass
#
#         if data == "finish\r\n":
#             condition = 0
#         elif data == "Stop\r\n":
#             condition = 0
#
#     file.close()




