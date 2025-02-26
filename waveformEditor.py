import tkinter as tk
import numpy as np 
import matplotlib.pyplot as plt
from mpl_draggable_line import DraggableVLine
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os


class waveformEditor(tk.Frame):
    def __init__(self, master, audio_path, audio_data, sample_rate, **kw):
        super().__init__(master, **kw)
        self.audio_path = audio_path
        self.sample_rate = sample_rate
        self.audio_data = audio_data
        self.playback_start = 0 #define default behavior
        self.playback_end =  None

        self.create_graph()

    #function to callback x value from draggable line. will need two of these for defining start and stop time but just do start for now
    def start_callback(self, x: float):
        frame_index = int(x * self.sample_rate)
        plt.suptitle(f"start pos: {x:0.2f}", x=-.01, y=-0.5, ha='center', va='bottom')
        self.playback_start = frame_index

    def end_callback(self, x: float):
        frame_index = int(x * self.sample_rate)
        plt.suptitle(f"end pos: {x:0.2f}", x=0.01, y=-0.5, ha='center', va='bottom')
        self.playback_end = frame_index

    def update_waveform(self, new_file_path, audio_data, sample_rate,):
        self.audio_path = new_file_path
        self.sample_rate = sample_rate
        self.audio_data = audio_data
        self.playback_start = 0
        self.playback_end = None

        for widget in self.winfo_children():
            widget.destroy()

        print("error 5")
        self.create_graph()

    def create_graph(self): 

        signal = self.audio_data
        # gets the frame rate
        self.playback_end = len(signal)
         
        # to Plot the x-axis in seconds  
        # you need get the frame rate  
        # and divide by size of your signal 
        # to create a Time Vector  
        # spaced linearly with the size  
        # of the audio file 
        time = np.linspace( 
            0, # start 
            len(signal) / self.sample_rate, 
            num = len(signal) 
        ) 
        
        

        fig, ax = plt.subplots()

        ax.clear()
        
        # title of the plot 
        file_name = os.path.basename(self.audio_path)
        ax.set_title(f"{file_name}") 
        
        # label of x-axis 
        ax.set_xlabel("Time") 
        
        # actual plotting 
        ax.plot(time, signal) 

        #initialize starting draggable line
        d_start = DraggableVLine(ax,0) #initialize draggable line
        d_start.on_line_changed(self.start_callback)

        #initalize ending draggable line
        d_end = DraggableVLine(ax,time[-1])
        d_end.on_line_changed(self.end_callback)

        #embed into tkinter
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw() 
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        #ensure matplotlib receives events
        canvas.mpl_connect("motion_notify_event", d_start._on_move)
        canvas.mpl_connect("button_press_event", d_start._on_press)
        canvas.mpl_connect("button_release_event", d_start._on_release)


        self.canvas = canvas
        self.d_start = d_start
        self.d_end = d_end
        
