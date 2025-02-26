import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
#import pygame
import os
from waveformEditor import waveformEditor
from pydub import AudioSegment 
#from pydub.playback import play
#import pyaudio
#import wave
import numpy as np
import sounddevice as sd
import wave


class Pad(ttk.Button):
    """a pad that initalizes a waveform editor when a file is dropped on it"""
    def __init__(self, master, controller, pad_id, **kw): #master is the frame for the pads, controller is mainwindow
        super().__init__(master, **kw)
        self.audio_path = None #store audio file path
        self.pad_id = pad_id #set pad ID name
        self.controller = controller #reference to main window
        self.sample_rate, self.audio_data = None, None #more audio data
        self.drop_target_register(DND_FILES) #enable filedrop
        self.dnd_bind('<<Drop>>', lambda event: self.drop(event, controller)) #trigger file drop
        self.config(text=str(pad_id), command=self.on_trigger) #configure button behavior

    #there is some latency somewhere here and it needs to be fixed
    def on_trigger(self):
        """wrapper function to raise editor and play audio"""
        if self.audio_path:
            self.controller.show_editor(self.pad_id) #raises the waveform editor in the main window
            self.play_audio(self.controller)

    def drop(self, event, controller):
        """saves file path and initalizes waveform editor"""
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'): #remove brackets
            file_path = file_path[1:-1]
        self.audio_path = file_path 
        
        # reading the audio file 
        with wave.open(self.audio_path, "rb") as raw: 
            sample_rate = raw.getframerate() # reads all the frames  
            signal = raw.readframes(-1)         # -1 indicates all or max frames 
            audio_data = np.frombuffer(signal, dtype=np.int16) #interpret from buffer
            #if raw.getnchannels() == 2: #handle stereo data
                #audio_data = audio_data.reshape((-1,2))

            self.sample_rate, self.audio_data = sample_rate, audio_data

        self.initialize_graph(controller, file_path, self.audio_data, self.sample_rate)

        #check for invalid file type. just .wav for now
        if not file_path.lower().endswith('.wav'):
            print("This is not a valid .wav file")
            self.audio_path = None
            self.config(text="Invalid file type")
        
    def initialize_graph(self, controller, file_path, audio_data, sample_rate):
        """initalizes instance of waveform editor"""

        #check if waveform editor is already initalized for this pad and update it
        #if so. waveform editors are saved in dict: waveform_editors in mainwindow.
        if self.pad_id in controller.waveform_editors: 
            controller.waveform_editors[self.pad_id].update_waveform(file_path, audio_data, sample_rate)

        #initalize waveform editor in display frame and add it to dict: waveform_editors
        else:
            editor = waveformEditor(controller.display_frame,file_path, audio_data, sample_rate)
            controller.waveform_editors[self.pad_id] = editor

        #raise editor to front
        controller.show_editor(self.pad_id)

    def play_audio(self, controller):
        #plays audio when pad is pressed
        if self.audio_path:
            try:
                editor = controller.waveform_editors[self.pad_id] #access associated editor in waveform_editors dict
                start_time = editor.playback_start #retrieve start and stop times from editor
                end_time = editor.playback_end  
                sliced_sample = self.audio_data[start_time:end_time] 
                sd.play(sliced_sample, samplerate=self.sample_rate)
            except:
                print(f"Error Playing Audio")
        else: 
            print ('No Audio File Selected')
"""            
    def play_audio(self, controller):
        #plays audio when pad is pressed
        if self.audio_path:
            try:
                audio = AudioSegment.from_file(self.audio_path)
                editor = controller.waveform_editors[self.pad_id] #access associated editor in waveform_editors dict
                start_time = editor.playback_start
                end_time = editor.playback_end
                segment = audio[start_time:end_time]
                play(segment)
            except:
                print(f"Error Playing Audio")
        else: 
            print ('No Audio File Selected')
"""

"""
    def play_audio(self):
        #plays audio when pad is pressed
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


        
    