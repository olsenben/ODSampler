import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES #make sure to pip install tkinterdnd2-universal
from Pad import Pad



class mainWindow(TkinterDnD.Tk): 
    #Let MainWindow be the child class of TkinterDnD.Tk allows us to copy functionality of TkinterDnD.Tk and define our own additonal stuff - kj
    def __init__(self, title="ODSampler", window_size="800x600"): #allows us to recall this function and but set these as parameters for now - kj
        super().__init__() #initialize parent class - kj

        # Set window title and size dynamically
        self.title(title)
        self.geometry(window_size)
        
        # Mframe for waveform editors
        self.display_frame = ttk.Frame(self, height=250)
        self.display_frame.pack(fill=tk.X, pady=5)

        #dict to store waveform_editors
        self.waveform_editors = {}
        self.active_editor = None

        #frame for pads
        self.pads_frame = ttk.Frame(self)
        self.pads_frame.pack()

        # create 4x4 grid for pads
        self.pads = []
        for i in range(4):
            for j in range(4):
                pad_id = i * 4 + j + 1
                pad = Pad(self.pads_frame, self, pad_id)
                pad.grid(row=i, column=j,padx=10, pady=10)
                self.pads.append(pad)

    def show_editor(self, pad_id):
        """raise te waveform editor associated with pad"""
        print(pad_id)
        if pad_id in self.waveform_editors: #check waveform_editors dict to see if a waveforeditor exists for this pad
            if self.active_editor:
                self.active_editor.place_forget() #hide acitve editor
            editor = self.waveform_editors[pad_id] #set new editor
            editor.place(relx=0, rely=0, relwidth=1, relheight=1) #make it visible
            self.active_editor = editor 



if __name__ == "__main__":
    ODSampler = mainWindow()
    ODSampler.mainloop()
