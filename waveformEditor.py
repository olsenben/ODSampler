#note here, you must install pyaudio, otherwise playback is defaulted to ffmpeg, which must be installed manually on windows. ffmpeg works fine on oxs but can cause issues with permission writing temp files on windows
import tkinter as tk
from tkinter import ttk

import numpy as np 
import wave, sys 
import matplotlib.pyplot as plt
from mpl_draggable_line import DraggableVLine
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os



#file_path = r"C:\Users\benol\Documents\GitHub\pervCore\Trimmed_Audio.wav"

#we'll need this for editing the pads class so im keeping it for now
#audio = AudioSegment.from_file(file_path)
#audio = audio.set_frame_rate(44100).set_channels(2).set_sample_width(2)

#start_time = 0 # 10 seconds
#end_time = len(audio) # 3 seconds after the start
#segment = audio[start_time:end_time]



class waveformEditor(tk.Frame):
    def __init__(self, master, audio_path=None,**kw):
        super().__init__(master, **kw)

        self.audio_path = audio_path
        self.playback_start = 0 #define default behavior
        self.playback_end =  0 

        self.create_graph()

    #function to callback x value from draggable line. will need two of these for defining start and stop time but just do start for now
    def v_callback(self, x: float):
        plt.suptitle(f"start pos: {x:0.2f}", x=0.5, y=0.01, ha='center', va='bottom')
        self.playback_start = x

    def update_waveform(self, new_file_path):
        self.audio_path = new_file_path
        self.playback_start = 0
        self.playback_end = 0

        for widget in self.winfo_children():
            widget.destroy()

    
        self.create_graph()

    def create_graph(self): 
        
        # reading the audio file 
        raw = wave.open(self.audio_path) 
        
        # reads all the frames  
        # -1 indicates all or max frames 
        signal = raw.readframes(-1) 
        signal = np.frombuffer(signal, dtype ="int16") 
        
        # gets the frame rate 
        f_rate = raw.getframerate() 
    
        # to Plot the x-axis in seconds  
        # you need get the frame rate  
        # and divide by size of your signal 
        # to create a Time Vector  
        # spaced linearly with the size  
        # of the audio file 
        time = np.linspace( 
            0, # start 
            len(signal) / f_rate, 
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

        #initialize draggable line
        d_start = DraggableVLine(ax,0) #initialize draggable line
        d_start.on_line_changed(self.v_callback)

        #embec into tkinter
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw() 
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        #ensure matplotlib receives events
        canvas.mpl_connect("motion_notify_event", d_start._on_move)
        canvas.mpl_connect("button_press_event", d_start._on_press)
        canvas.mpl_connect("button_release_event", d_start._on_release)


        self.canvas = canvas
        self.d_start = d_start
        



"""
if __name__ == "__main__": 
    plot(file_path,start_time,end_time)

"""