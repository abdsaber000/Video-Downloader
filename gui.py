import tkinter as tk
from tkinter import END, ttk, messagebox
import pyperclip
from concurrent import futures
from call_params import CallParams
from downloader import Downloader
thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)



ROW_START = 1
class App():
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.geometry('800x600')
        self.root.title('Video Downloader')
        self.mainFrame = tk.Frame(self.root , background='white')
        self.mainFrame.pack(fill='both' , expand=True)
        self.text = tk.Label(self.mainFrame , text= 'Enter your Url: ' , background='white')
        self.text.grid(row=ROW_START , column=0)

        self.text_field = tk.Entry(self.mainFrame , width=100)
        self.text_field.grid(row=ROW_START , column=1 ,padx=20 , pady=60 ,sticky='NWES')
        self.paste_button = tk.Button(self.mainFrame , text='Paste' , command=self.handle_paste)
        self.paste_button.grid(row = ROW_START , column= 2)
        
        n = tk.StringVar()
        self.quality = ttk.Combobox(self.mainFrame , width = 50 , textvariable=n, )
        self.quality.grid(row=ROW_START + 2, column=1 , pady= 10, padx=50)
        self.quality.set('Choose download format')
        
        self.button = tk.Button(self.mainFrame , text='Start Download'
                                , command=self.start_download)
        self.button.grid(row = ROW_START +3 , column= 1 , pady=50)

        self.button_search = tk.Button(self.mainFrame , text='Search'
                                , command=self.check_video_info)
        self.button_search.grid(row = ROW_START +1 , column= 1)

        self.status_text = tk.Label(self.mainFrame , text='No Download')
        self.status_text.grid(row= ROW_START + 4 , column=1)

        self.progress_bar = ttk.Progressbar(self.mainFrame, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.grid(row = ROW_START + 5 , column = 1)

        self.progress_percent = ttk.Label(self.mainFrame, text = '0.0%')
        self.progress_percent.grid(row = ROW_START + 5, column = 1 , pady = 50)

        self.downloader = Downloader(CallParams(self.status_text, self.progress_bar, self.progress_percent))

        self.hide_before_search()
        self.root.mainloop()
        return
    
    
    
    def hide_before_search(self):
        self.button.grid_remove()
        self.quality.grid_remove()
        self.progress_bar.grid_remove()
        self.progress_percent.grid_remove()
        self.status_text.grid_remove()

    def show_after_search(self):
        self.button.grid()
        self.quality.grid()
    

    def show_on_download(self):
        self.progress_bar.grid()
        self.progress_percent.grid()
        self.status_text.grid()
        self.status_text.config(text = 'Ready')
        self.progress_bar['value'] = 0
        self.progress_percent.config(text = '0.0%')

    def check_video_done_callback(self, future):
        self.quality['values'] = future.result()
        self.show_after_search()
        self.button_search.config(text = 'Search')

    def check_video_info(self):
        self.button_search.config(text = 'Searching...')
        self.hide_before_search()
        try:
            url = self.text_field.get()
            future = thread_pool_executor.submit(self.downloader.search_for_video_formats, url)
            future.add_done_callback(self.check_video_done_callback)
        except Exception as err:
            self.button_search.config(text = 'Search')
            messagebox.showerror("Error" , str(err))
        
    

    def start_download(self):
        self.show_on_download()
        format_index = self.quality.current()
        url = self.text_field.get()
        try:
            thread_pool_executor.submit(self.downloader.download_video, url, format_index)
        except Exception as err:
            messagebox.showerror("Error", str(err))
    
    def handle_paste(self):
        self.text_field.delete(0, END)
        self.text_field.insert(0, pyperclip.paste())