import tkinter as tk
from tkinter import END, ttk

class CallParams:
    def __init__(self, status_text : tk.Label,  progress_par : ttk.Progressbar, progress_percent : ttk.Label):
        self.status_text = status_text
        self.progress_bar = progress_par
        self.progress_percent = progress_percent
    
    def update_params(self, d):
        print(d,'\n','================================')
        if d['status'] == 'finished':
            self.status_text.config(text='Download Done.')
            self.progress_bar['value'] = 100
            self.progress_percent.config(text='100%')
        else:
            self.status_text.config(text='Remainging Time: '+str(d['eta']))
            if 'total_bytes' in d:
                percent = round(d['downloaded_bytes'] / d['total_bytes'] * 100,2)
            elif 'total_bytes_estimate' in d:
                percent = round(d['downloaded_bytes'] / d['total_bytes_estimate'] * 100,2)
            else:
                percent = 0
            self.progress_bar['value'] = percent
            self.progress_percent.config(text=f'{percent}%') 