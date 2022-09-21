import numpy as np
from impedance import preprocessing
from impedance.models.circuits import CustomCircuit
import pandas as pd
import matplotlib.pyplot as plt

circuit_library = ['R0-C1',
                   'R0-p(R1-Wo1,C1)',
                   'R0-p(R1,C1)-p(R2-Wo1,C2)']
p0 = [[.01, 100],
      [0.01, 1, 1000, 1, 0.01],
      [.01, .01, 100, .01, .05, 100, 1]]

# p0 = [[100, 200],
#       [100, 200, 1000, 1, 0.01],
#       [100, 200, 100, .01, .05, 100, 1]]


def read_excel(filename):
    """
    Loads the data from a excel file.
    :param
    filename: str
        string with the path to the desired file
    :return:
    xx: ndarray
        array with the frequencies
    yy: complex ndarray
        impedance array
    """
    data = pd.read_excel(filename)

    # take the ndarray from dataframe
    np_data = data.values

    xx = np_data[:, 0]
    yy = np_data[:, 1] - 1j * np_data[:, 2]

    plt.plot(np.real(yy), -np.imag(yy))
    return xx, yy


def read_csv_sdf(filename):
    """
     Loads the data from a CSV or space delimited file.
     :param
     filename: str
         string with the path to the desired file
     :return:
     xx: ndarray
         array with the frequencies
     yy: complex ndarray
         impedance array
     """
    with open(filename, 'r') as file:
        file = file.read()

        # Checking the delimiter
        if file.find(',') == -1:
            char = ' '
        else:
            char = ','

        # Rearrange file
        file = file.split('\n')
        pro_data = np.zeros((len(file), 3))

        for i, item in enumerate(file):
            item = item.split(char)
            try:
                pro_data[i, 0] = item[0]
                pro_data[i, 1] = item[1]
                pro_data[i, 2] = item[2]
                # freq, Zre, Zim
            except ValueError:
                print('error')
                pass

        xx = pro_data[:, 0]
        z_re = pro_data[:, 1]
        z_im = pro_data[:, 2]

        yy = z_re + 1j*z_im

        return xx, yy


def fit_(xx, yy, model, initial_guess):
    """
    Optimizes the best fitting values. using impedance.py

    :param
    xx: ndarray
        frequencies array
    yy: complex ndarray
        impedance array
    model: str
        string with the equivalent circuit
    initial_guess: list
        list with the initial values
    :return:
    Z_fit: ndarray
        array with the predicted impedance values
    parameters: ndarray
        optimized parameters
    error: ndarray
        absolute error of the parameters
    """
    circuit = CustomCircuit(model, initial_guess=initial_guess)
    circuit.fit(xx, yy)
    Z_fit = circuit.predict(xx)

    parameters = circuit.parameters_
    error = circuit.conf_

    return Z_fit, parameters, error


def corr_(y_ini, y_fit):
    """
    Calculates the correlation coefficient between the initial data and the predicted data from a fitting model.
    :param
    y_ini: ndarray
        initial data
    y_fit: ndarray
        predicted data
    :return:
    rs: float
        coefficient
    """
    res = y_ini - y_fit
    s_res = np.sum(res ** 2)

    y_mean = np.mean(y_ini)
    variance = y_ini - y_mean
    s_tol = np.sum(variance ** 2)

    r_square = 1 - s_res / s_tol

    return r_square


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


def calibration(xx, m, b):
    """
    Calibration curve
    :param
    x: float, int
        The x to calculate conc
    m: float
        slope of the line in (ug/ohm*L)
    b: float
        intersection in ug/L
    :return:
    y: float
        concentration in ug/L
    """

    y = m * xx + b
    return y


def check_best_fit(j):
    """
    Integrates through a given list of equivalent circuits and initial guesses to select the best fitting model.
    :return:
    parameters: ndarray
        optimized parameters
    error: ndarray
        calculated errors
    r_square:
        correlation coefficient
    """
    # initializing variables
    parameters = []
    error = []
    r = 0

    freq, z = read_excel(f'./ExperimentalData/ImpedanceData#{j}.xlsx')
    # freq, z = read_csv_sdf(f'./ExperimentalData/ImpedanceData#{j}.csv')
    frequencies, Z = preprocessing.ignoreBelowX(freq, z)
    mod_Z = mod_(Z)

    for i in range(0, len(circuit_library)):
        Z_fitting, parameters, error = fit_(frequencies, Z, model=circuit_library[i], initial_guess=p0[i])
        mod_fit = mod_(Z_fitting)
        r = corr_(mod_Z, mod_fit)

        plt.plot(np.real(Z_fitting), -np.imag(Z_fitting))

        if r >= 0.999:
            break

    return parameters, error, r


def validate_(value, error, r_square):
    """
    Checks the viability of the fitting according to given restrictions
    :param
    value: float
        parameter value
    error: float
        error associated
    r_square: float
        correlation coefficient
    :return:
    result: float or int
        if everything okay returns the value otherwise 0
    """

    if not isinstance(value, (float, int, np.int32, np.float64)):
        print(f'The object "{str(value)}" is not a number. Unable to compute further')
        return 0
    if not isinstance(error, (float, int, np.int32, np.float64)):
        print(f'The object "{str(error)}" is not a number. Unable to compute further')
        return 0
    if not isinstance(r_square, (float, int, np.int32, np.float64)):
        print(f'The object "{str(r_square)}" is not a number. Unable to compute further')
        return 0

    lower_limit = 0
    upper_limit = 300
    if lower_limit <= value <= upper_limit:
        result = value
    else:
        print(f'The calculated parameter {value} does not satisfy the boundary: [{lower_limit}, {upper_limit}]')
        return 0

    limit_error = 0.1
    relative_error = error/value
    if relative_error > limit_error:
        print(f'The calculated error, {value*100}, is higher than the allowed ({limit_error*100}%). '
              f'Computed concentration not viable')
        result = value

    if r_square < 0.99:
        print(f'Fitting to poor. R^2 = {r_square}. Computed concentration not viable')
        result = value

    return result


for i in range(1, 9):
    param, err, r2 = check_best_fit(i)
    var = param[1]
    var_err = err[1]
    var = validate_(var, var_err, r2)
    if var:
        concentration = calibration(var, m=0.49049, b=4.9049)
        print(f'{i}:: Parameter[R1] = {var} (+-) {var_err/var*100}%. \nR^2 = {r2} '
              f'\nConcentration = {concentration} ug/L')
