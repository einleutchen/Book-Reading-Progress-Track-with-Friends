#!/usr/bin/env/python3

import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import firebase_admin
from firebase_admin import credentials, firestore
import threading
import pygame

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Firestore Document Reference
PROGRESS_DOC = "reading_progress"
doc_ref = db.collection("progress").document(PROGRESS_DOC)

# Initialize pygame mixer for music
pygame.mixer.init()     


# Create the main application class
class PixelProgressWidget:
    def __init__(self, master):

        self.master = master
        self.master.title("Reading Progress")
        self.master.geometry("360x280")
        self.master.attributes('-topmost', True)  # Always on top
        self.master.config(cursor= "arrow")
        self.master.resizable(False, False) #avoid resize the window, but if True, True it will be resizable

          # Load and resize animated GIF
        self.gif_image = Image.open("combined_ghibli.gif")
        self.frames = [ImageTk.PhotoImage(img.resize((360, 280))) for img in ImageSequence.Iterator(self.gif_image)]
        self.frame_index = 0
        
        self.image_label = tk.Label(master)
        self.image_label.place(x=0, y=0, width=360, height=280)
        self.update_gif()

        #Entry box of strings (book title)
        self.label_box = StringVar()
        self.label_box = Entry(master, bg="white", justify="center", textvariable=self.label_box, font="bold", borderwidth=0)
        self.label_box.place(x=85, y=70)

        # Labels and progress bars 
            #customize the progress bar style
        style = ttk.Style()
        style.theme_use("default")  # Ensure using a customizable theme
        #add text to progress bars
        style.layout('text.Horizontal.TProgressbar', [('Horizontal.Progressbar.trough', {'children': [('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})],'sticky': 'nswe'}),('Horizontal.Progressbar.padding', {'side':'left'}),('Horizontal.Progressbar.label', {'side':'left','sticky': ''})])
        #style.configure("Custom.Horizontal.TProgressbar", troughcolor = "white", background="lightblue", thickness=10)  
        style.configure('text.Horizontal.TProgressbar', anchor='center', troughcolor = "white", background="lightblue", thickness=10)
        
            #labels and button A
        self.update_button_A = tk.Button(self.master, text="Pham", command=self.update_progress_A, height=1, bg="white", borderwidth=0)
        self.update_button_A.place(x=50, y=100)
                
            #Progress bar A
        self.progress_var_A = tk.IntVar()
        self.progress_bar_A = ttk.Progressbar(self.master, orient="horizontal", length=50, maximum = 50, mode="determinate", variable=self.progress_var_A, style="text.Horizontal.TProgressbar")
        self.progress_bar_A.place(x=150, y=105)
        self.progress_text_A = tk.Label(self.master, text="0/50", bg="white")
        self.progress_text_A.place(x=230, y=105)

            #labels and button B
        self.update_button_B = tk.Button(self.master, text="Nguyen", command=self.update_progress_B, height=1, bg="white", borderwidth=0)
        self.update_button_B.place(x=50, y=145)
        
            #Progress bar B
        self.progress_var_B = tk.IntVar()
        self.progress_bar_B = ttk.Progressbar(self.master, orient="horizontal", length=50, maximum = 50, mode="determinate", variable=self.progress_var_B, style="text.Horizontal.TProgressbar")
        self.progress_bar_B.place(x=150, y=150)
        self.progress_text_B = tk.Label(self.master, text="0/50", bg="white")
        self.progress_text_B.place(x=230, y=150)

            #minus button 
        self.minus_button_A = tk.Button(self.master, text="-", command=self.subtract_progress_A, height=1, bd=1, bg="white")
        self.minus_button_A.place(x=290, y=105)
        self.minus_button_B = tk.Button(self.master, text="-", command=self.subtract_progress_B, height=1, bd=1, bg="white")
        self.minus_button_B.place(x=290, y=150)
        
        #set fetch thread
        self.fetch_progress_thread = threading.Thread(target=self.fetch_progress, daemon=True)
        self.fetch_progress_thread.start()
        
        #add Play and pause button
        self.master.after(50, self.play_music) # Delay the music start by 3 seconds (3000 milliseconds)

        self.music_button = tk.Button(master, text = "Play/Pause", command = self.pause, bg="white")
        self.music_button.place(x=80, y=190)

        #add reset button
        self.reset_button = tk.Button(master, text = "Reset", command = self.reset_progress, bg="white")
        self.reset_button.place(x=210, y=190)
 
    def update_gif(self):
        self.image_label.config(image=self.frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.master.after(50, self.update_gif)

    def update_progress_A(self):
        new_progress_A = self.progress_var_A.get() + 1  # Increase progress by 2
        if new_progress_A > 50:
            new_progress_A = 50
        self.progress_var_A.set(new_progress_A)
        self.progress_text_A.config(text=f"{new_progress_A}/50")
        doc_ref.set({"progress_A": new_progress_A}, merge=True)

    def update_progress_B(self):
        new_progress_B = self.progress_var_B.get() + 1  # Increase progress by 2
        if new_progress_B > 50:
            new_progress_B = 50
        self.progress_var_B.set(new_progress_B)
        self.progress_text_B.config(text=f"{new_progress_B}/50")
        doc_ref.set({"progress_B": new_progress_B}, merge=True)
    
    def fetch_progress(self): #if the fetch crashes, create a new private key, and save it as serviceAccountKey.json then update in the env, DON'T delete anything on Firebase
        def on_snapshot(doc_snapshot, changes, read_time):
            for doc in doc_snapshot:
                new_progress_A = doc.to_dict().get("progress_A", 0)
                new_progress_B = doc.to_dict().get("progress_B", 0)
                self.progress_var_A.set(new_progress_A)
                self.progress_text_A.config(text=f"{new_progress_A}/50")
                self.progress_var_B.set(new_progress_B)
                self.progress_text_B.config(text=f"{new_progress_B}/50")
                self.label_box.config(text=f"{self.label_box}")
        doc_ref.on_snapshot(on_snapshot)
  
    def subtract_progress_A(self):
        new_progress_A = self.progress_var_A.get() - 1 
        if new_progress_A < 0:
            new_progress_A = 0
        self.progress_var_A.set(new_progress_A)
        self.progress_text_A.config(text=f"{new_progress_A}/50")
        doc_ref.set({"progress_A": new_progress_A}, merge=True)
    
    def subtract_progress_B(self):
        new_progress_B = self.progress_var_B.get() - 1 
        if new_progress_B < 0:
            new_progress_B = 0
        self.progress_var_B.set(new_progress_B)
        self.progress_text_B.config(text=f"{new_progress_B}/50")
        doc_ref.set({"progress_B": new_progress_B}, merge=True)
    
    def reset_progress(self):
        self.progress_var_A.set(0)
        self.progress_text_A.config(text="0/100")
        doc_ref.set({"progress_A": 0}, merge=True)
        self.progress_var_B.set(0)
        self.progress_text_B.config(text="0/100")
        doc_ref.set({"progress_B": 0}, merge=True)  
    
    def play_music(self):
        pygame.mixer.music.load("music_track.mp3")  # Load the lofi track
        pygame.mixer.music.play(-1)  # Loop indefinitely

    global paused
    paused = False
    def pause(self):
        global paused 
        if paused:
            pygame.mixer.music.unpause()
            paused = False
        else:
            pygame.mixer.music.pause()
            paused = True     

# Run the app
if __name__ == "__main__":
    window = tk.Tk()
    app = PixelProgressWidget(window)
    window.mainloop()
