import os
from tkinter import *
from tkinter import filedialog
import pygame
from pydub import AudioSegment

root = Tk()
root.title("Music Player")
root.iconbitmap()
root.geometry("500x350")

pygame.mixer.init()  # To use pygame with sounds

# Global Variables
songsDir = {}  # Current list of songs
global Pause  # is paused or not
Pause = False


def addSong():  # Add Song Function
    songWithDir = filedialog.askopenfilenames(initialdir="songs/", title="Choose A Song", filetypes=(
        ("mp3 Files", "*.mp3"), ("wav Files", "*.wav")))  # Accepting only MP3 and wav files
    # Remove Directory From Name
    for i in songWithDir:  # Getting all .mp3 and .wav, converting .mp3 to .wav and saving in directory songs/
        song = i[::-1]
        if song[0:4] == '3pm.':
            song = song[song.find('3pm.') + 4: song.find('/')]
            sound = AudioSegment.from_mp3(i)
            sound.export(i.replace(".mp3", ".wav"), format="wav")
            os.remove(i)
        elif song[0:4] == 'vaw.':
            song = song[song.find('vaw.') + 4: song.find('/')]

        song = song[::-1]
        if song not in songsDir:  # No dublicate songs allowed
            SongsList.insert(END, song)  # Adding song to screen
            songsDir[song] = i.replace(".mp3", ".wav")


def deleteSong():  # Delete Song Function
    os.remove(songsDir[SongsList.get(ACTIVE)])
    SongsList.delete(ANCHOR)
    pygame.mixer_music.stop()  # Stop playing music


def softDelete():
    SongsList.delete(ANCHOR)
    pygame.mixer_music.stop()  # Stop playing music


def play():  # Play Song
    song = SongsList.get(ACTIVE)  # Get highlighted song in box
    pygame.mixer.music.load(songsDir[song])
    pygame.mixer_music.play()


def stop():  # Stop song
    pygame.mixer_music.stop()  # Stop playing music
    SongsList.selection_clear(ACTIVE)  # Unselect the highlighted song


def pause(isPaused):  # Pause/Unpause song
    global Pause
    Pause = isPaused
    if Pause:
        pygame.mixer_music.unpause()  # Unpause the song
        Pause = False
    else:
        pygame.mixer_music.pause()  # Pause the song
        Pause = True


def forward():  # Next song
    currentSong = SongsList.get(ACTIVE)
    temp = list(songsDir)
    try:
        nextSong = temp[temp.index(currentSong) + 1]
        pygame.mixer.music.load(songsDir[nextSong])
        pygame.mixer_music.play(loops=0)
    except (ValueError, IndexError):
        nextSong = currentSong
    SongsList.selection_clear(0, END)  # Clear Selection

    SongsList.activate(temp.index(nextSong))
    SongsList.selection_set(temp.index(nextSong), last=None)


def back():  # Previous song
    currentSong = SongsList.get(ACTIVE)
    temp = list(songsDir)
    try:
        nextSong = temp[temp.index(currentSong) - 1]
        pygame.mixer.music.load(songsDir[nextSong])
        pygame.mixer_music.play(loops=0)
    except (ValueError, IndexError):
        nextSong = currentSong
    SongsList.selection_clear(0, END)  # Clear Selection

    SongsList.activate(temp.index(nextSong))
    SongsList.selection_set(temp.index(nextSong), last=None)


def setVolume(val):
    pygame.mixer_music.set_volume(int(val) / 100)


# Create playlist box
SongsList = Listbox(root, bg="white", fg="black", width="40",
                   selectbackground="teal",borderwidth=0)  # Change background and text color and width, and selection color
SongsList.pack(pady=20)

# Control Button Images Import
backButtonImg = PhotoImage(file="images/Control/prev.png")
forwardButtonImg = PhotoImage(file="images/Control/next.png")
playButtonImg = PhotoImage(file="images/Control/play.png")
stopButtonImg = PhotoImage(file="images/Control/stop.png")
pauseButtonImg = PhotoImage(file="images/Control/pause.png")

# Create Player Control Frames
controls_frame = Frame(root)
controls_frame.pack()

# Volume Slider
scale = Scale(root, from_=0, to=100, orient=HORIZONTAL, command=setVolume)
pygame.mixer_music.set_volume(70 / 100)
scale.set(value=70)
scale.pack()

# Create Player Control Buttons
backButton = Button(controls_frame, image=backButtonImg, borderwidth=0, command=back)
forwardButton = Button(controls_frame, image=forwardButtonImg, borderwidth=0, command=forward)
playButton = Button(controls_frame, image=playButtonImg, borderwidth=0, command=play)
stopButton = Button(controls_frame, image=stopButtonImg, borderwidth=0, command=stop)
pauseButton = Button(controls_frame, image=pauseButtonImg, borderwidth=0, command=lambda: pause(Pause))

backButton.grid(row=0, column=0, padx=10)
forwardButton.grid(row=0, column=1, padx=10)
playButton.grid(row=0, column=2, padx=10)
stopButton.grid(row=0, column=3, padx=10)
pauseButton.grid(row=0, column=4, padx=10)

# Create Menu
newMenu = Menu(root)
root.config(menu=newMenu)

# Add Song to Menu
addSongMenu = Menu(newMenu)
newMenu.add_cascade(label="Add", menu=addSongMenu)
addSongMenu.add_command(label="Insert Songs", command=addSong)

# Remove Song from Menu
RemoveSongMenu = Menu(newMenu)
newMenu.add_cascade(label="Delete", menu=RemoveSongMenu)
RemoveSongMenu.add_command(label="Remove from playlist", command=softDelete)
RemoveSongMenu.add_command(label="Delete from directory", command=deleteSong)

root.mainloop()
