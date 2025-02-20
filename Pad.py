import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import pygame
import os
from waveformEditor import waveformEditor




"""class mainWindow(TkinterDnD.Tk): 
    #Let MainWindow be the child class of TkinterDnD.Tk allows us to copy functionality of TkinterDnD.Tk and define our own additonal stuff - kj
    def __init__(self, title="Pervcore", window_size="500x500"): #allows us to recall this function and but set these as parameters for now - kj
        super().__init__() #initialize parent class - kj

        # Set window title and size dynamically
        self.title(title)
        self.geometry(window_size)

        
        # Main container for widgets
        self.container = ttk.Frame(self)
        self.container.pack(expand=True, pady=50)

        # Add the pad button inside the container
        pad = Pad(self.container)
        pad.pack(pady=50)
"""
class Pad(ttk.Button):
    def __init__(self, master, controller, pad_id, **kw): #pass through arguments to tk.Button class upon initilization
        super().__init__(master, **kw)
        self.audio_path = None
        self.pad_id = pad_id
        self.controller = controller
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', lambda event: self.drop(event, controller))
        self.config(command=self.play_audio)


    def drop(self, event, controller):
        print("Drop event triggered")  # Debugging line to check if the event is fired

        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        self.audio_path = file_path
        self.initialize_graph(controller, file_path)

        if not file_path.lower().endswith('.wav'):
            print("This is not a valid .wav file")
            self.audio_path = None
            self.config(text="Invalid file type")
        
    def initialize_graph(self, controller, file_path):
        """initalizes instance of waveform editor"""
        if self.pad_id in controller.waveform_editors: 
            controller.waveform_editors[self.pad_id].update_waveform(file_path)
        else:
            editor = waveformEditor(controller.display_frame,file_path)
            editor.pack(fill=tk.X, pady=5)
            controller.waveform_editors[self.pad_id] = editor

        controller.show_editor(self.pad_id)
            

    def play_audio(self):
        if self.audio_path:
            try:            
                pygame.mixer.init()
                pygame.mixer.music.load(self.audio_path)
                pygame.mixer.music.play()            
            except pygame.error as e:
                print(f"Error Playing Audio: {e}")
        else:
            print ("No Audio File Selected")

"""
if __name__ == "__main__":
    pervcore = mainWindow()
    pervcore.mainloop()
    """

