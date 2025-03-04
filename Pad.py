from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from waveformEditor import waveformEditor
import numpy as np
import sounddevice as sd
#import librosa
import pyrubberband as rubberband
import soundfile as sf


class Pad(ttk.Button):
    """a pad that initalizes a waveform editor when a file is dropped on it. opens audio stream and handles audio playback triggers """
    def __init__(self, master, controller, pad_id, **kw): #master is the frame for the pads, controller is mainwindow
        super().__init__(master, **kw)

        #reference to main window
        self.controller = controller 

        #set pad ID name
        self.pad_id = pad_id 

        #store necesary audio data for opening stream
        self.audio_path = None #store audio file path
        self.sample_rate, self.audio_data, self.num_channels= None, None, None #more audio data
        self.current_position = None #this might be a problem later
        self.chunk_size = None    #singal chunk for resampling
        
        """Low-latency applications (real-time playback, live effects):
        256–1024 samples (small chunks, high CPU usage)
        General audio playback (music, streaming):
        1024–4096 samples (balanced)
        High-quality time-stretching/pitch-shifting (post-processing):
        4096+ samples (larger chunks, better quality)
        """
        #holder space for opening stream
        self.stream = None 

        #these will be updated dynamically 
        #all gui elements will be referenced via controller and initalized in the mainwindow
        self.stretch_factor = 1 #for time stretching
        self.pitch_shift_semitones = 1 #for repitching

        #handle file dropping behavior
        self.drop_target_register(DND_FILES) #enable filedrop
        self.dnd_bind('<<Drop>>', lambda event: self.drop(event, controller)) #trigger file drop
        self.config(text=str(pad_id), command=self.on_trigger) #configure button behavior

    def on_trigger(self):
        """wrapper function to raise editor and play audio"""
        if self.audio_path: 
            self.controller.show_editor(self.pad_id) #raises the waveform editor in the main window ie "controller" frame
            self.play_audio()

    def drop(self, event, controller):
        """saves file path and initalizes waveform editor"""
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'): #remove brackets
            file_path = file_path[1:-1]
        self.audio_path = file_path #save filepath
        
        #self.audio_data = (self.audio_data * 32767).astype(np.int16)

        # reading with wave for .wav or librosa for anything else
        if file_path.lower().endswith(".wav"):
            
            #context manager for opening audio file
            with sf.SoundFile(self.audio_path, "r") as raw: 
                
                signal = raw.read(dtype='float32')#signal arrawy
                sample_rate = raw.samplerate #framerate
                channels = raw.channels #number of channels (stereo or mono)
                self.audio_data = (signal.reshape(-1, channels)) #format is (audio,channel) in numpy array
                self.sample_rate = sample_rate #save sample rate
        
        #currently having a memory leak when opening in stereo with librosa so I have disabled it for now
        else: 
            #signal, sample_rate =  librosa.load(self.audio_path, sr=None, mono=False)
            #if signal.ndim == 1: #check 
            #    self.audio_data = signal.reshape(1,-1) #ensure consistent shape
            pass

        #check for invalid file type. just .wav for now until I fix the memory leak
        if not file_path.lower().endswith('.wav'):
            print("This is not a valid .wav file")
            self.audio_path = None
            self.config(text="Invalid file type")
        
        #save number of channels. This was more necesary when librosa was in use so I leave this here for now
        self.num_channels = self.audio_data.shape[1] #1 if mono, 2 if stero
        
        #initalize graph in controller frame
        self.initialize_graph(controller, file_path, self.audio_data, self.sample_rate)

        
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

    #currently unimplemented
    """
    def set_params(self, stretch_factor=1.0, pitch_shift_semitones=0):
        self.stretch_factor = stretch_factor
        self.pitch_shift_semitones = pitch_shift_semitones
    """
    """"
    def normalize_audio(audio_data):
        max_val = np.max(np.abs(audio_data))

        if max_val > 0:
            return audio_data / max_val
        return audio_data
    """

    def call_back(self,outdata, frames, time, status):
        if status:
            print(status)

        #access associated editor in waveform_editors dict
        editor = self.controller.waveform_editors[self.pad_id] 
        
        #if self.current_position is None:
        #    self.current_position = editor.plaback_start
        
        #retrieve start and stop times from waveformeditor
        start = self.current_position 
        
        #set chunk size and ensure we dont go beyod available data
        self.chunk_size = min(len(self.audio_data) - start, frames)
        chunksize = self.chunk_size
        end = start + chunksize
        
        #stop if end reaches or exceeds playback end
        if end >= editor.playback_end or chunksize <=0:
            raise sd.CallbackStop

        #currently need to be applied to the outdata    
        """"
        #apply affects if necessary
        if self.stretch_factor != 1:
            chunk = np.array([rubberband.time_stretch(channel, self.sample_rate, self.stretch_factor)
                              for channel in chunk])
        if self.pitch_shift_semitones != 0:
            chunk = np.array([rubberband.pitch_shift(channel, self.sample_rate, self.pitch_shift_semitones)
                              for channel in chunk])
        """
        #write data for output buffer
        outdata[:chunksize] = self.audio_data[start:start + chunksize]
       
        #update position
        self.current_position += chunksize

        if self.current_position >= editor.playback_end:
            raise sd.CallbackStop

    #trigger function to open stream triger call back/restart playback
    def play_audio(self):
        if self.audio_data is None or len(self.audio_data) == 0:
            print("No Audio Loaded")
            return
        
        #reference waveform editor for start position
        editor = self.controller.waveform_editors[self.pad_id]
        
        # Reset to playback start upon trigger
        self.current_position = editor.playback_start 

        #check if stream is already open
        if self.stream is None or not self.stream.active:
            
            #blocksize set to 0 allows it to set dynamically from what I understand
            self.stream = sd.OutputStream(samplerate=self.sample_rate, blocksize=0, latency='low', channels=self.num_channels, callback=self.call_back,dtype='float32')
            
            #start stream
            self.stream.start()

        # If the stream is already active, just reset the current_position and continue playback
        else:
            self.current_position = editor.playback_start 