"""
Report generator.
Saves all fitting data to a xlsx file.

use function call_with_popup to add progress bar popup while generating file
"""
import pandas as pd
from tkinter import filedialog
from xlsxwriter.exceptions import DuplicateWorksheetName, InvalidWorksheetName
from tkinter import messagebox
from threader import in_thread
import datetime


def exception_permissionerror(fun):
    def wrapper(*args, **kwargs):
        try:
            fun(*args, **kwargs)
        except PermissionError:
            args[2].close()
            messagebox.showerror('Permission denied', f'File {args[0].split("/")[-1]} is open in another application.\n'
                                                      f'The report failed to be compiled. '
                                                      f'Close {args[0].split("/")[-1]} and try again!')
    return wrapper


def call_with_popup(costumeTabs):
    file = filedialog.asksaveasfilename()

    if file:
        from popups import TopProgressBar
        tpb = TopProgressBar(tasks=len(costumeTabs))
        generate_report(file, costumeTabs, tpb)


@in_thread
@exception_permissionerror
def generate_report(file, Tabs, tpb=None):

    # Making sure only one .xlsx exists in the path
    file = file.replace('.xlsx', '')
    file += '.xlsx'
    i = 0
    duplicates = []
    with pd.ExcelWriter(file, engine="xlsxwriter") as writer:
        wrkb = writer.book
        bold = wrkb.add_format({'bold': True})

        for tab in Tabs:
            try:
                fitting = tab.activeFit
                if fitting is not None:
                    tab.chart.figure.savefig(f'ReportData/reportFig{i}.png', dpi=300)

                    sht_name = tab.e_name.get()
                    if len(sht_name) > 31:
                        sht_name += ' '
                        sht_name = sht_name[-30:-1]

                    wrks = wrkb.add_worksheet(sht_name)

                    cons = {"Name": fitting.const[0], 'Value': fitting.const[1], 'Error': None, 'Units': None}
                    initGuess = {"Name": fitting.names[0], 'Value': fitting.init_guess, 'Error': None, 'Units': fitting.names[1]}
                    calFit = {'Name': fitting.names[0], 'Value': fitting.params, 'Error': fitting.errors, 'Units': fitting.names[1]}
                    stats = {'Name': [u'\u03A7\u00B2', u'Critical \u03A7\u00B2', 'DF', 'Confidence'], 'Value': fitting.stats, 'Error':None, 'Units': ['', '', '', '%']}
                    predict = {'Frequency (Hz)': fitting.freq_p, 'Real Z (\u03A9)': fitting.z_re_p, '-Imaginary Z (\u03A9)': fitting.z_im_p, "|Z| (\u03A9)": fitting.mod_z_p, "Phase (\u00B0)": fitting.phase_p}
                    measured = {'Frequency (Hz)': fitting.freq_m, 'Real Z (\u03A9)': fitting.z_re_m, '-Imaginary Z (\u03A9)': fitting.z_im_m, "|Z| (\u03A9)": fitting.mod_z_m, "Phase (\u00B0)": fitting.phase_m}

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
                    startrow = 2

                    date = str(datetime.datetime.now())
                    wrks.write_string(0, 0, fitting.name, bold)
                    wrks.write_string(1, 0, date, bold)
                    for df in df_main:
                        df.to_excel(writer, startrow=startrow, sheet_name=sht_name)
                        startrow += (df.shape[0] + 2)

                    wrks.insert_image('H1', f'ReportData/reportFig{i}.png', {'x_scale': 0.5, 'y_scale': 0.5})
                    i += 1

                    if tpb is not None:
                        tpb.progress()

            except DuplicateWorksheetName:
                if fitting.name not in duplicates:
                    duplicates.append(fitting.name)

    if tpb is not None:
        tpb.complete()
        tpb.close()

    if duplicates:
        msg = f'{duplicates.__len__()} duplicated "tab names" were found during report generation.' \
              f' The duplicated tabs were not included in the final report file. ' \
              f'Please consider confirming the data in the generated report before closing the program.' \
              f'\n' \
              f'\n' \
              f'The duplicated tab names are the folwing:\n'

        for duplicate in duplicates:
            msg += '\t' + duplicate + '\n'

        messagebox.showwarning('Duplicated Names', msg)
