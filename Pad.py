from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from waveformEditor import waveformEditor
import numpy as np
import sounddevice as sd
#import librosa
import pyrubberband as rubberband
import wave
import soundfile as sf




class Pad(ttk.Button):
    """a pad that initalizes a waveform editor when a file is dropped on it"""
    def __init__(self, master, controller, pad_id, **kw): #master is the frame for the pads, controller is mainwindow
        super().__init__(master, **kw)
        self.audio_path = None #store audio file path
        self.pad_id = pad_id #set pad ID name
        self.controller = controller #reference to main window
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

        self.stream = None #holder space for opening stream
        self.stretch_factor = 1 #for time stretching
        self.pitch_shift_semitones = 1 #for repitching
        self.drop_target_register(DND_FILES) #enable filedrop
        self.dnd_bind('<<Drop>>', lambda event: self.drop(event, controller)) #trigger file drop
        self.config(text=str(pad_id), command=self.on_trigger) #configure button behavior

    #there is some latency somewhere here and it needs to be fixed
    def on_trigger(self):
        """wrapper function to raise editor and play audio"""
        if self.audio_path: 
            self.controller.show_editor(self.pad_id) #raises the waveform editor in the main window
            self.play_audio()

    def drop(self, event, controller):
        """saves file path and initalizes waveform editor"""
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'): #remove brackets
            file_path = file_path[1:-1]
        self.audio_path = file_path 
        
        #self.audio_data = (self.audio_data * 32767).astype(np.int16)

        # reading with wave for .wav or librosa for anything else
        if file_path.lower().endswith(".wav"):
            with sf.SoundFile(self.audio_path, "r") as raw: 
                
                signal = raw.read(dtype='float32')
                sample_rate = raw.samplerate
                channels = raw.channels
                #sample_width = raw.getsampwidth()
                #sample_rate = raw.getframerate() # reads all the frames  
                #signal = raw.readframes(-1)         # -1 indicates all or max frames 
                #dtype = np.int16 if sample_width == 2 else np.int32
                #audio_data = np.frombuffer(signal, dtype=dtype) #interpret from buffer

                self.audio_data = (signal.reshape(-1, channels)) #format is (audio,channel)
                self.sample_rate = sample_rate
        else:
            #signal, sample_rate =  librosa.load(self.audio_path, sr=None, mono=False)
            #if signal.ndim == 1: #check 
            #    self.audio_data = signal.reshape(1,-1) #ensure consistent shape
            pass



        #check for invalid file type. just .wav for now
        if not file_path.lower().endswith('.wav'):
            print("This is not a valid .wav file")
            self.audio_path = None
            self.config(text="Invalid file type")
        
        self.num_channels = self.audio_data.shape[1] #1 if mono, 2 if stero
        print(self.num_channels)
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

    def set_params(self, stretch_factor=1.0, pitch_shift_semitones=0):
        self.stretch_factor = stretch_factor
        self.pitch_shift_semitones = pitch_shift_semitones

    def normalize_audio(audio_data):
        max_val = np.max(np.abs(audio_data))

        if max_val > 0:
            return audio_data / max_val
        return audio_data

    def call_back(self,outdata, frames, time, status):
        if status:
            print(status)

        editor = self.controller.waveform_editors[self.pad_id] #access associated editor in waveform_editors dict

        #if self.current_position is None:
        #    self.current_position = editor.plaback_start

        start = self.current_position #retrieve start and stop times from waveformeditor
        
        #set chunk size and ensure we dont go beyod available data
        self.chunk_size = min(len(self.audio_data) - start, frames)
        chunk = self.chunk_size
        end = start + chunk
        
        #stop if current position reaches or exceeds playback end
        if end >= editor.playback_end or chunk <=0:
            print(chunk.shape)
            raise sd.CallbackStop
            

        #write data for output buffer
        outdata[:chunk] = self.audio_data[start:start + chunk]
       
        #update position
        self.current_position += chunk

        if self.current_position >= editor.playback_end:
            raise sd.CallbackStop

    """
    def call_back(self,outdata,frames,time,status):
        if status:
            print(status)

        #set start and end point references from waveform editor
        editor = self.controller.waveform_editors[self.pad_id] #access associated editor in waveform_editors dict
        
        if self.current_position is None:
            self.current_position = editor.plaback_start

        start = self.current_position #retrieve start and stop times from editor
        end = min(start + self.chunk_size, editor.playback_end)
       
       #check if end of playback is reached and stop
        if end > editor.playback_end:
            self.current_position = 0
            print(self.current_position)
            raise sd.CallbackStop
            
        
        #portion of audio playing back
        chunk = self.audio_data[:,start:end].copy() #select both channels if stereo
        # If chunk is too short, pad it with zeros
        if chunk.shape[1] < frames:  
            pad_width = frames - chunk.shape[1]
            chunk = np.pad(chunk, ((0, 0), (0, pad_width)), mode='constant')


        #apply affects if necessary
        if self.stretch_factor != 1:
            chunk = np.array([rubberband.time_stretch(channel, self.sample_rate, self.stretch_factor)
                              for channel in chunk])
        if self.pitch_shift_semitones != 0:
            chunk = np.array([rubberband.pitch_shift(channel, self.sample_rate, self.pitch_shift_semitones)
                              for channel in chunk])

        # Ensure shape is correct for sounddevice (frames, channels)
        #chunk = self.normalize_audio(chunk)


        chunk = chunk.T  # Convert (channels, frames) → (frames, channels)

        #if np.max(np.abs(chunk)) > 0.8:  # Threshold for attenuation
        #    chunk = chunk * 0.8  # Attenuate by scaling down


        outdata[:chunk.shape[0], :self.num_channels] = chunk
        
        #update playback position
        self.current_position += frames
    """

    def play_audio(self):
        if self.audio_data is None or len(self.audio_data) == 0:
            print("No Audio Loaded")
            return
        
        editor = self.controller.waveform_editors[self.pad_id]
        self.current_position = editor.playback_start  # Reset to playback start


        if self.stream is None or not self.stream.active:
            self.stream = sd.OutputStream(samplerate=self.sample_rate, blocksize=0, latency='low', channels=self.num_channels, callback=self.call_back,dtype='float32')
            self.stream.start()
        # If the stream is already active, just reset the current_position and continue playback
        else:
            self.current_position = editor.playback_start 

"""
    def play_audio(self, controller):
        #plays audio when pad is pressed
        if self.audio_path:
            try:
                editor = controller.waveform_editors[self.pad_id] #access associated editor in waveform_editors dict
                start_time = editor.playback_start #retrieve start and stop times from editor
                end_time = editor.playback_end  
                sliced_sample = self.audio_data[start_time:end_time] 
                sd.play(sliced_sample, samplerate=self.sample_rate, blocksize=128, latency='low')
            except:
                print(f"Error Playing Audio")
        else: 
            print ('No Audio File Selected')
"""
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


        
    