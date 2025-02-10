import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import pygame
import os



class mainWindow:
    def __init__(self, root):
        self.container = ttk.Frame(root) #container
        root.title("pervcore")
        self.container.pack()

# Make sure drag and drop events are triggered for the entire window
        root.drop_target_register(DND_FILES)
        root.dnd_bind("<<DROP>>", self.drop)

        self.pad_1 = Pad(root)
        self.pad_1.pack(pady=100)
        
        

    def drop(self, event):
        print("Main Window Drop event triggered!")  # Debugging line to confirm event firing
        # Forward to pad's drop method
        self.pad_1.drop(event)



class Pad(ttk.Button):
    def __init__(self, master, **kw): #pass through arguments to tk.Button class upon initilization
        print ("pad initilized")
        super().__init__(master, **kw)
        self.audio_path = None #whatever the master container is
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<DROP>>', self.drop)
        self.config(command=self.play_audio)


    def drop(self, event):
        print("Drop event triggered")  # Debugging line to check if the event is fired

        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        self.audio_path = file_path

        file_name = os.path.basename(file_path)
        self.config(text=file_name)
        print("Dropped file: ", file_path)

        if not file_path.lower().endswith('.wav'):
            print("This is not a valid .wav file")
            self.audio_path = None
            self.config(text="Invalid file type")

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


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    root.geometry("500x500")
    pervcore = mainWindow(root)
    root.mainloop()
