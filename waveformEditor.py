from pydub import AudioSegment
from pydub.playback import play
import numpy as np 
import wave, sys 
import matplotlib.pyplot as plt

file_path = "/Users/agyakarki/Documents/pervCore/Trimmed_audio.wav"


audio = AudioSegment.from_file(file_path)

audio = audio.set_frame_rate(44100).set_channels(2).set_sample_width(2)

start_time = 0 # 10 seconds
end_time = len(audio) # 3 seconds after the start
print(end_time)
segment = audio[start_time:end_time]



def visualize(path: str, start_time, end_time): 
    
    # reading the audio file 
    raw = wave.open(path) 
      
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
  
    # using matplotlib to plot 
    # creates a new figure 
    plt.figure(1) 
      
    # title of the plot 
    plt.title("Sound Wave") 
      
    # label of x-axis 
    plt.xlabel("Time") 
     
    # actual plotting 
    plt.plot(time, signal) 
    
    # Draw vertical line
    #plt.axvline(x=start_time, color='r', linestyle='--')
    #plt.axvline(x=end_time, color='r', linestyle='--')

    # shows the plot  
    # in new window 
    plt.show() 
  
    # you can also save 
    # the plot using 
    # plt.savefig('filename') 

if __name__ == "__main__": 
    visualize(file_path,start_time,end_time)

play(segment)
