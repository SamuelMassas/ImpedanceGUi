from tkinter import *
from tkinter import ttk


class TopProgressBar(Toplevel):
    """
    Designing a progress bar that shows up on a toplevel window to show the
    progress during loading data
    """
    def __init__(self, tasks):
        super().__init__()
        self.update_idletasks()
        self.tasks = tasks
        self.resizable(0, 0)
        self.overrideredirect(True)
        self.attributes('-topmost', 'true')

        # Setting up the positioning
        x_left = self.master.winfo_rootx()
        y_top = self.master.winfo_rooty()
        self.geometry("+%d+%d" % (x_left, y_top))

        # Forcing pop up and disabling root
        self.focus_set()
        self.master.attributes('-disabled', True)

        self.frame = Frame(self)
        self.frame.pack(fill=BOTH, expand=True)
        self.bar = ttk.Progressbar(self.frame, orient='horizontal', mode='determinate', maximum=tasks, length=200)
        self.bar.pack(fill=BOTH, expand=True)

    def progress(self):
        """ Increases the progress of the bar """
        self.bar['value'] = 1 + int(self.bar['value'])

    def complete(self):
        """ Completely fill the bar"""
        self.bar['value'] = self.tasks

    def close(self):
        self.master.attributes('-disabled', False)
        self.destroy()
