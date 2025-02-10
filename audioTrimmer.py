import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment

def open_audio_file():
    filepath = filedialog.askopenfilename(
        defaultextension=".wav",
        filetypes=[("Audio Files", "*.wav"), ("MP3 Files", "*.mp3"), ("OGG Files", "*.ogg")]
    )

    if filepath:
        global audio
        audio = AudioSegment.from_file(filepath)
        duration = len(audio) / 1000  # duration in seconds
        print(f"File loaded, duration: {duration} seconds")  # Debugging statement
        
        # Update sliders
        time_slider.config(to=duration)  # set end time slider max value to audio duration
        start_time_slider.config(to=duration)  # set start time slider max value to audio duration

        # Set sliders to start and end points
        time_slider.set(duration)  # set slider to full duration
        start_time_slider.set(0)

        # Update labels
        update_end_time_label(duration)  # update end time label
        update_start_time_label(0)  # update start time label

def update_start_time_label(value):
    start_time_label.config(text=f"Start Time: {float(value):.2f}s")

def update_end_time_label(value):
    end_time_label.config(text=f"End Time: {float(value):.2f}s")

def trim_audio():
    start_time = start_time_slider.get() * 1000  # convert to milliseconds
    end_time = time_slider.get() * 1000  # convert to milliseconds
    trimmed_audio = audio[start_time:end_time]
    trimmed_audio.export("Trimmed_Audio.wav", format='wav')  # save as a .wav file
    print('Audio trimmed and saved as Trimmed_Audio.wav')

# GUI initialization
window = tk.Tk()
window.title("Audio Trimmer")
window.geometry("500x400")  # Ensure a larger window size for better visibility

# Open button
open_button = tk.Button(window, text='Open Audio File', command=open_audio_file)
open_button.pack(pady=10)

# Start time label and slider
start_time_label = tk.Label(window, text='Start Time: 0.00s')
start_time_label.pack(pady=10)
start_time_slider = tk.Scale(window, from_=0, to=100, orient="horizontal", length=100, command=lambda value: update_start_time_label(value))
start_time_slider.pack(pady=10)

# End time label and slider
end_time_label = tk.Label(window, text='End Time: 0.00s')
end_time_label.pack(pady=10)
time_slider = tk.Scale(window, from_=0, to=100, orient='horizontal', command=lambda value: update_end_time_label(value))
time_slider.pack(pady=10)

# Trim button
trim_button = tk.Button(window, text='Trim Audio', command=trim_audio)
trim_button.pack(pady=20)

window.mainloop()
