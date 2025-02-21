import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import pygame
import os
from waveformEditor import waveformEditor


class Pad(ttk.Button):
    """a pad that initalizes a waveform editor when a file is dropped on it"""
    def __init__(self, master, controller, pad_id, **kw): #master is the frame for the pads, controller is mainwindow
        super().__init__(master, **kw)
        self.audio_path = None
        self.pad_id = pad_id
        self.controller = controller
        self.drop_target_register(DND_FILES) #enable filedrop
        self.dnd_bind('<<Drop>>', lambda event: self.drop(event, controller)) #trigger file drop
        self.config(text=str(pad_id), command=self.on_trigger)

    def on_trigger(self):
        """wrapper function"""
        if self.audio_path:
            self.play_audio()

        #raises the waveform editor in the main window
        self.controller.show_editor(self.pad_id)

    def drop(self, event, controller):
        """salves file path and initalizes waveform editor"""
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        self.audio_path = file_path
        self.initialize_graph(controller, file_path)

        #check for invalid file type. just .wav for now
        if not file_path.lower().endswith('.wav'):
            print("This is not a valid .wav file")
            self.audio_path = None
            self.config(text="Invalid file type")
        
    def initialize_graph(self, controller, file_path):
        """initalizes instance of waveform editor"""

        #check if waveform editor is already initalized for this pad and update it
        #if so. waveform editors are saved in dict: waveform_editors in mainwindow.
        if self.pad_id in controller.waveform_editors: 
            controller.waveform_editors[self.pad_id].update_waveform(file_path)
        #initalize waveform editor in display frame and add it to dict: waveform_editors
        else:
            editor = waveformEditor(controller.display_frame,file_path)
            controller.waveform_editors[self.pad_id] = editor

        #raise editor to front
        controller.show_editor(self.pad_id)
            

    def play_audio(self):
        """plays audio when pad is pressed"""
        if self.audio_path:
            try:            
                pygame.mixer.init()
                pygame.mixer.music.load(self.audio_path)
                pygame.mixer.music.play()            
            except pygame.error as e:
                print(f"Error Playing Audio: {e}")
        else:
            print ("No Audio File Selected")


