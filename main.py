'''
IMPORTS
'''
from tkinter import *
from scipy.io.wavfile import read
from scipy.io.wavfile import write
from scipy import signal
from pydub import AudioSegment
from tkinter import filedialog
import pygame
import os
import glob
import random
from urllib.request import Request, urlopen
from html.parser import HTMLParser

'''
GLOBAL VARIABLES
'''
Pause = False
curPlaylist = ""
Songs = []
index = None

'''
STARTING PYGAME.MIXER
'''
pygame.mixer.init()

'''
PLAYLIST CONFIGURATIONS
'''


class ListConfigure:

    def __init__(self, parent):

        self.add_img = PhotoImage(file="images/List/open.png")  # IMAGE OF ADDING TO LIST

        self.parent = parent  # Tk OBJECT

        self.add = Button(self.parent, image=self.add_img, width=40, height=35, command=self.add_bt,
                          background="gray")  # ADD TO PLAYLIST BUTTON

        self.create()  # SHOWING THE BUTTON(S)

    def create(self):
        self.add.place(x=7, y=20)

    def add_bt(self):
        flag = True  # FLAG TO CHECK FOR DUPLICATES

        '''
        GETTING CURRENT PLAYLIST PLAYING (TXT FILE)
        '''
        global curPlaylist
        fileName = curPlaylist

        '''
        CHOOSING NEW SONG TO ADD TO PLAYLIST
        '''
        songWithDir = filedialog.askopenfilename(initialdir="songs/", title="Choose A Song", filetypes=(
            ("mp3 Files", "*.mp3"), ("wav Files", "*.wav")))  # Accepting only MP3 and wav files

        '''
        CHECKING IF SONG ALREADY EXISTS IN PLAYLIST
        '''
        ffile = open(fileName)
        content2 = ffile.readlines()

        for line in content2:
            if (line.strip()[:-4] == songWithDir[:-4]):
                flag = False
                break
        ffile.close()

        '''
        IF SONG NOT ALREADY FOUND, ADD IT TO PLAYLIST
        '''
        if (flag):

            ffile = open(fileName, "a")
            sound = AudioSegment.from_mp3(songWithDir)
            sound.export(songWithDir.replace(".mp3", ".wav"), format="wav")
            ffile.write(songWithDir.replace(".mp3", ".wav") + '\n')
            ffile.close()

            global Songs
            Songs = []
            songs_list.delete(0, END)

            ffile = open(fileName)
            content = ffile.readlines()

            for line in content:
                Songs.append(line[:-1])

            ffile.close()

            '''
            GETTING ACTUAL NAME OF SONG
            '''
            for Song in Songs:
                songList = Song.split('/')
                Song = songList[-1]
                songs_list.insert(END, Song[:-4])


class Control:

    def __init__(self, parent):
        self.parent = parent  # Tk OBJECT

        '''
        BUTTON IMAGES
        '''
        self.play_img = PhotoImage(file="images/Control/play.png")
        self.pause_img = PhotoImage(file="images/Control/pause.png")
        self.stop_img = PhotoImage(file="images/Control/stop.png")
        self.prev_img = PhotoImage(file="images/Control/prev.png")
        self.next_img = PhotoImage(file="images/Control/next.png")
        self.stop_rec_img = PhotoImage(file="images/Control/rec_stop.png")
        self.shuffle_img = PhotoImage(file="images/Control/shuffle.png")
        self.volume_img = PhotoImage(file="images/Control/volume.png")

        '''
        CREATING BUTTONS AND ADJUSTING VOLUME SLIDER
        '''
        self.play = Button(self.parent, image=self.play_img, width=60, height=45, command=self.play_btn,
                           activebackground="cyan")
        self.prev = Button(self.parent, image=self.prev_img, width=60, height=45, command=self.prev_btn,
                           activebackground="cyan")
        self.next = Button(self.parent, image=self.next_img, width=60, height=45, command=self.next_btn,
                           activebackground="cyan")
        self.stop = Button(self.parent, image=self.stop_img, width=60, height=45, command=self.stop_btn,
                           activebackground="cyan")
        self.shuffle = Button(self.parent, image=self.shuffle_img, width=60, height=45, command=self.shuffle_btn,
                              activebackground="cyan")
        self.volume = Scale(self.parent, from_=0, to=100, orient=HORIZONTAL, activebackground="cyan", command=setVolume)
        pygame.mixer_music.set_volume(70 / 100)
        self.volume.set(value=70)
        self.volume_label = Label(self.parent, image=self.volume_img, width=60, height=40)

        self.play.bind("<Button-3>", self.left_click)

        self.create()  # SHOWING BUTTONS AND VOLUME

    def create(self):
        self.play.place(x=250, y=242)
        self.prev.place(x=180, y=242)
        self.next.place(x=320, y=242)
        self.stop.place(x=10, y=242)
        self.shuffle.place(x=80, y=242)
        self.volume_label.place(x=410, y=247)
        self.volume.place(x=480, y=247)

    def play_btn(self):
        play()  # CALLING PLAY FUNCTION

        '''
        CHANGING PLAY AND PAUSE BUTTON BASED ON PLAYING CONDITION
        '''
        if Pause:

            self.play.configure(image=self.play_img)
            self.play.image = self.play_img
        else:

            self.play.configure(image=self.pause_img)
            self.play.image = self.pause_img

    def stop_btn(self):
        '''
        CHANGING TO PLAY BUTTON
        '''
        self.play.configure(image=self.play_img)
        self.play.image = self.play_img

        stop()  # CALLING STOP FUNCTION

    def shuffle_btn(self):
        '''
        PLAYING A RANDOM SONG FROM CURRENT PLAYLIST
        '''
        size = songs_list.size()
        r = random.randint(0, size - 1)

        songs_list.selection_clear(0, END)
        songs_list.select_set(r)

        pygame.mixer.music.load(Songs[r])
        pygame.mixer_music.play()

        self.play.configure(image=self.pause_img)
        self.play.image = self.pause_img

    def prev_btn(self):
        '''
        PLAYING PREVIOUS SONG IN PLAYLIST
        '''
        index = songs_list.curselection()  # Get highlighted song in box

        songs_list.selection_clear(0, END)

        try:
            i = (len(Songs) + (index[0] - 1)) % len(Songs)
            pygame.mixer.music.load(Songs[i])
        except (ValueError, IndexError):
            i = (len(Songs) + (index[0])) % len(Songs)
            pygame.mixer.music.load(Songs[i])

        songs_list.select_set(i)
        pygame.mixer_music.play()

        self.play.configure(image=self.pause_img)
        self.play.image = self.pause_img

    def next_btn(self):
        '''
        PLAYING NEXT SONG IN PLAYLIST
        '''
        index = songs_list.curselection()  # Get highlighted song in box

        songs_list.selection_clear(0, END)

        try:
            i = (len(Songs) + (index[0] + 1)) % len(Songs)
            pygame.mixer.music.load(Songs[i])
        except (ValueError, IndexError):
            i = (len(Songs) + (index[0])) % len(Songs)
            pygame.mixer.music.load(Songs[i])

        songs_list.select_set(i)
        pygame.mixer_music.play()

        self.play.configure(image=self.pause_img)
        self.play.image = self.pause_img

    def left_click(self, event):
        event.widget.configure(bg="green")


def choosePlayList():
    '''
    CREATES A NEW WINDOW FOR USER TO CHOOSE FROM ALREADY CREATED PLAYLISTS
    '''
    Gui = Tk()
    Gui.geometry('400x400')
    Gui.title('Choose a play list')

    lst = glob.glob("*.txt")  # LIST OF FILES WITH (.txt) FORMAT

    playListsList = Listbox(Gui, bg="white", fg="black", width="40",
                            selectbackground="teal", borderwidth=0)
    playListsList.pack(pady=20)

    for playlist in lst:
        playListsList.insert(END, playlist[:-4])

    '''
    BUTTON TO CONFIRM PLAYLIST SELECTION
    '''
    newButton = Button(Gui, text='next', command=lambda: displayPlayList(Gui, playListsList.get(ANCHOR) + '.txt'))
    newButton.pack()

    Gui.mainloop()


def displayPlayList(Gui, fileName):
    '''
    DISPLAY SONGS OF PLAYLIST TO USER
    '''
    Gui.destroy()  # DESTROYING PREVIOUS WINDOW

    global curPlaylist
    curPlaylist = fileName

    global Songs
    Songs = []
    songs_list.delete(0, END)

    ffile = open(fileName)
    content = ffile.readlines()
    for line in content:
        Songs.append(line[:-1])
    ffile.close()

    '''
    GETTING ACTUAL NAME OF SONG
    '''
    for Song in Songs:
        songList = Song.split('/')
        Song = songList[-1]
        songs_list.insert(END, Song[:-4])


def Create():
    '''
    CREATES A NEW PLAYLIST
    '''
    PlayList = newPlayList()


class newPlayList:
    '''
    CLASS FOR DEALING WITH NEW PLAYLISTS
    '''

    def __init__(self):

        self.SongsList = None  # CLASS VARIABLE

        '''
        NEW WINDOW
        '''
        gui = Tk()
        gui.geometry('300x300')
        gui.title('Create a playlist')

        '''
        ASKING USER TO ENTER NAME OF PLAYLIST
        '''
        gLabel = Label(gui, text='Enter the name of the playlist').grid(row=0)
        user_input = StringVar(gui)

        gEntry = Entry(gui, textvariable=user_input)
        gEntry.grid(row=1)

        '''
        BUTTON TO MOVE TO NEXT WINDOW
        '''
        gButton = Button(gui, text='next',
                         command=lambda: [gui.destroy(), self.createPlayList(user_input.get() + '.txt')])
        gButton.grid(row=2)

        gui.mainloop()

    def createPlayList(self, fileName):
        '''
        ADDING AND REMOVING SONGS TO PLAYLIST
        '''

        ffile = open(fileName, 'w')  # create file to store the playlist
        ffile.close()

        '''
        NEW WINDOW
        '''
        root2 = Tk()
        root2.title("Music Player")
        root2.iconbitmap()
        root2.geometry("500x350")

        '''
        LIST TO SHOW CHOSEN SONGS
        '''
        self.SongsList = Listbox(root2, bg="white", fg="black", width="40", selectbackground="teal",
                                 borderwidth=0)  # Change background and text color and width, and selection color
        self.SongsList.pack(pady=20)

        # Create Player Control Frames
        controls_frame = Frame(root2)
        controls_frame.pack()

        # Create Menu
        newMenu = Menu(root2)
        root2.config(menu=newMenu)

        # Add Song to Menu
        addSongMenu = Menu(newMenu)
        newMenu.add_cascade(label="Add", menu=addSongMenu)
        addSongMenu.add_command(label="Insert Songs", command=lambda: self.addSong(fileName, self.SongsList))

        # Remove Song from Menu
        RemoveSongMenu = Menu(newMenu)
        newMenu.add_cascade(label="Delete", menu=RemoveSongMenu)
        RemoveSongMenu.add_command(label="Remove from playlist", command=lambda: self.Delete(fileName))

        root2.mainloop()

    def addSong(self, fileName, SongsList):  # Add Song Function
        count = 0

        '''
        CHOOSE NEW SONG FROM DIRECTORY
        '''
        songWithDir = filedialog.askopenfilenames(initialdir="songs/", title="Choose A Song", filetypes=(
        ("mp3 Files", "*.mp3"), ("wav Files", "*.wav")))  # Accepting only MP3 and wav files

        '''
        Remove Directory From Name
        '''
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

            '''
            CHECKING FOR DUPLICATION BEFORE ADDING
            '''
            ffile = open(fileName)
            content = ffile.readlines()
            ffile.close()

            ffile = open(fileName, 'a')

            if (songWithDir[count] + '\n') not in content:
                ffile.write(songWithDir[count][:-3] + 'wav' + '\n')
                self.SongsList.insert(END, song)
            count += 1

    def Delete(self, fileName):
        '''
        REMOVE SELECTED SONG FROM PLAYLIST
        '''
        ffile = open(fileName)
        content = ffile.readlines()
        ffile.close()

        for i in range(len(content)):
            if self.SongsList.get(ANCHOR) in content[i]:
                content.pop(i)

        ffile = open(fileName, 'w')
        for line in content:
            ffile.write(line)
        ffile.close()

        self.SongsList.delete(ANCHOR)


def trimSong():
    '''
    DISPLAY WINDOW FOR USER TO SPECIFY START AND END TIMES
    '''

    mGUI = Tk()
    mGUI.geometry('400x400')

    mGUI.title('Specify the start and end times')

    sLabel = Label(mGUI, text='Start time').grid(row=0)

    sHrsLabel = Label(mGUI, text='Hours').grid(row=1, column=0)
    sMinsLabel = Label(mGUI, text='Mins').grid(row=1, column=1)
    sSecLabel = Label(mGUI, text='Sec').grid(row=1, column=2)

    spaceLabel = Label(mGUI, text='|').grid(row=0, column=3)

    eLabel = Label(mGUI, text='End time').grid(row=0, column=4)

    eHrsLabel = Label(mGUI, text='Hours').grid(row=1, column=4)
    eMinsLabel = Label(mGUI, text='Mins').grid(row=1, column=5)
    eSecLabel = Label(mGUI, text='Sec').grid(row=1, column=6)

    startHoursEntry = Entry(mGUI)
    startHoursEntry.grid(row=2, column=0)

    startMinsEntry = Entry(mGUI)
    startMinsEntry.grid(row=2, column=1)

    startSecEntry = Entry(mGUI)
    startSecEntry.grid(row=2, column=2)

    endHoursEntry = Entry(mGUI)
    endHoursEntry.grid(row=2, column=4)

    endMinsEntry = Entry(mGUI)
    endMinsEntry.grid(row=2, column=5)

    endSecEntry = Entry(mGUI)
    endSecEntry.grid(row=2, column=6)

    mButton = Button(mGUI, text='Done',
                     command=lambda: Trim(mGUI, startHoursEntry.get(), startMinsEntry.get(), startSecEntry.get(),
                                          endHoursEntry.get(), endMinsEntry.get(), endSecEntry.get())).grid(row=3,
                                                                                                            columnspan=7)
    mGUI.mainloop()


def Trim(mGUI, startHours, startMins, startSec, endHours, endMins, endSec):
    mGUI.destroy()

    '''
    SET ANY EMPTY ENTRY TO ZERO
    '''
    if startHours == '':
        startHours = 0

    if startMins == '':
        startMins = 0

    if startSec == '':
        startSec = 0

    if endHours == '':
        endHours = 0

    if endMins == '':
        endMins = 0

    if endSec == '':
        endSec = 0

    startTime = int(startSec) * 1000 + int(startMins) * 1000 * 60 + int(startHours) * 1000 * 60 * 60

    endTime = int(endSec) * 1000 + int(endMins) * 1000 * 60 + int(endHours) * 1000 * 60 * 60

    index = songs_list.curselection()  # Get highlighted song in box
    currentSong = Songs[index[0]]

    if 'wav' in currentSong:
        newAudio = AudioSegment.from_wav(currentSong)
        newAudio = newAudio[startTime:endTime]
        newAudio.export(out_f=currentSong[:len(currentSong) - 4] + '_Trimmed' + '.wav', format='wav')

    else:
        newAudio = AudioSegment.from_mp3(currentSong)
        newAudio = newAudio[startTime:endTime]
        newAudio.export(out_f=currentSong[:len(currentSong) - 4] + '_Trimmed' + '.mp3')


def play():  # Play Song
    '''
    GLOBAL VARIABLES
    '''
    global Pause
    global index

    '''
    CHECK IF A SONG IS ALREADY PLAYING OR NOT AND IF THE CURSOR IS AT THE CURRENTLY PLAYING SONG
    '''
    if pygame.mixer.music.get_busy() and index == songs_list.curselection():
        if Pause:
            pygame.mixer_music.unpause()  # Unpause the song
            Pause = False
        else:
            pygame.mixer_music.pause()  # Pause the song
            Pause = True

    else:

        index = songs_list.curselection()  # Get highlighted song in box
        pygame.mixer.music.load(Songs[index[0]])
        pygame.mixer_music.play()


def stop():  # Stop song
    pygame.mixer_music.stop()  # Stop playing music
    songs_list.selection_clear(ACTIVE)  # Unselect the highlighted song


def setVolume(val):
    pygame.mixer_music.set_volume(int(val) / 100)


def DeleteSong():
    songs_list.delete(ANCHOR)


def removeNoise():
    index = songs_list.curselection()  # Get highlighted song in box
    currentSong = Songs[index[0]]

    '''READING .WAV FILE
    '''
    # get currentSong
    (freq, data) = read(currentSong)

    '''
    FILTERING
    '''
    s1, s2 = signal.butter(5, 1000 / (freq / 2), btype='highpass')
    f_s = signal.lfilter(s1, s2, data)

    s3, s4 = signal.butter(5, 380 / (freq / 2), btype='lowpass')
    new_s = signal.lfilter(s3, s4, f_s)

    '''
    SAVING
    '''
    write(currentSong[:len(currentSong) - 4] + '_WITHOUT_NOISE.wav', freq, new_s)


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.id = ""
        self.song_name = ""
        self.artist_name = ""
        self.image_link = ""
        self.top_songs = []
        self.top_artists = []

    def handle_starttag(self, tag, attrs):
        '''
        LOOKS FOR THE SPAN TAG TO COLLECT THE REQUIRED DATA
        '''
        if (tag == 'span'):
            for name, value in attrs:
                if (name == 'class' and value == 'chart-element__rank__number'):
                    self.id = 'found'
                elif (name == 'class' and value == 'chart-element__information__song text--truncate color--primary'):
                    self.song_name = "found"
                elif (
                        name == 'class' and value == 'chart-element__information__artist text--truncate color--secondary'):
                    self.artist_name = "found"

    def handle_data(self, data):
        if (self.id == 'found'):
            self.id = ""

        if (self.song_name == 'found'):
            self.top_songs.append(data)
            self.song_name = ""

        if (self.artist_name == "found"):
            self.top_artists.append(data)
            self.artist_name = ""


def get_top():
    '''
    GET TOP 10 SONGS FROM LINK
    '''
    req = Request('http://www.billboard.com/charts/hot-100', headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read().decode()

    parser = MyHTMLParser()
    parser.feed(webpage)

    '''
    NEW WINDOW TO DISPLAY SONGS
    '''
    gui = Tk()
    gui.geometry("400x200")
    gui.title("TOP 10 SONGS")

    top_list = Listbox(gui, width=60, height=10)
    top_list.pack()

    for i in range(10):
        top_list.insert(END, parser.top_songs[i] + " - " + parser.top_artists[i])

    gui.mainloop()


'''
MAIN WINDOW
'''
root = Tk()
root.title("Melody")
root.geometry("600x300")
root.resizable(0, 0)


class DropDownMenu:
    main_menu = Menu(root)

    def __init__(self, parent, title="Add title", command={}):
        self.parent = parent
        self.title = title
        self.command = command
        self.create()

    def create(self):
        self.parent.config(menu=self.main_menu)
        menu = Menu(self.main_menu)
        self.main_menu.add_cascade(label="{}".format(self.title), menu=menu)
        for (label, func) in self.command.items(): menu.add_command(label="{}".format(label), command=func)
        menu.add_separator()


# Drop down menu section
DropDownMenu(root, "Options", {"Trim": trimSong, "Remove Noise": removeNoise, "Get Top 10 Trends!": get_top})
DropDownMenu(root, "Playlist", {"Create playlist": Create, "Choose playlist": choosePlayList})
DropDownMenu(root, "Delete", {"Delete Selected": DeleteSong})

# Main screen section
screen_frame = Frame(root, width=590, height=230, bg="gray")
screen_frame.place(x=5, y=5)
ListConfigure(root)

# List screen section
songs_list = Listbox(screen_frame, width=100, height=10)
songs_list.place(x=0, y=60)

# Control Frame section
control_fame = Frame(root, width=590, height=57, background="grey")
control_fame.place(x=5, y=239)
Control(root)

root.mainloop()
