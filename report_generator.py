import io

import pandas as pd
from tkinter import filedialog
import xlsxwriter


def generate_report(costumeTabs):
    file = filedialog.asksaveasfilename()

    # Making sure only one .xlsx exists in the path
    file = file.replace('.xlsx', '')
    file += '.xlsx'
    i = 0
    # output = []
    with pd.ExcelWriter(file, engine="xlsxwriter") as writer:
        for tab in costumeTabs:
            fitting = tab.activeFit
            i += 1
            tab.chart.figure.savefig('reportFig.png')
            if fitting is not None:
                cons = {"Name": fitting.const[0], 'Value': fitting.const[1], 'Error': None, 'Units': None}
                initGuess = {"Name": fitting.names[0], 'Value': fitting.init_guess, 'Error': None, 'Units': fitting.names[1]}
                calFit = {'Name': fitting.names[0], 'Value': fitting.params, 'Error': fitting.errors, 'Units': fitting.names[1]}
                stats = {'Name': ['DF', u'\u03A7\u00B2', u'Critical \u03A7\u00B2', 'Confidence'], 'Value': fitting.stats, 'Error':None, 'Units': ['', '', '', '%']}
                predict = {'Frequency (Hz)': fitting.freq_p, 'Real Z (\u03A9)': fitting.z_re_p, '-Imaginary Z (\u03A9)': fitting.z_im_p, "|Z| (\u03A9)": fitting.mod_z_p, "Phase (\u00B0)": fitting.phase_p}
                measured = {'Frequency (Hz)': fitting.freq, 'Real Z (\u03A9)': fitting.z_re, '-Imaginary Z (\u03A9)': fitting.z_im, "|Z| (\u03A9)": fitting.mod_z, "Phase (\u00B0)": fitting.phase}

                df_cons = pd.DataFrame(cons)
                df_i = pd.DataFrame(initGuess)
                df_fit = pd.DataFrame(calFit)
                df_stats = pd.DataFrame(stats)
                df_predict = pd.DataFrame(predict)
                df_meas = pd.DataFrame(measured)

                # Giving title to df
                df_cons.index.name = 'Constants'
                df_i.index.name = 'Initial guess'
                df_fit.index.name = 'Calculated fitting'
                df_stats.index.name = 'Statistics'
                df_predict.index.name = 'Predicted values'

                df_results = pd.concat(
                    {'Constants': df_cons, 'Initial Guess': df_i, 'Calculated fitting': df_fit, 'Statistics': df_stats}, axis=0)

                df_rawData = pd.concat(
                    {'Predicted': df_predict, 'Measured': df_meas}, axis=1)

                # Exporting to Excel
                df_main = [df_results, df_rawData]
                startrow = 0
                for df in df_main:
                    df.to_excel(writer, engine="xlsxwriter", startrow=startrow, sheet_name=fitting.name)
                    startrow += (df.shape[0] + 2)

                worksheet = writer.sheets[fitting.name]
                worksheet.insert_image('H1', 'reportFig.png', {'x_scale': 0.5, 'y_scale': 0.5})
