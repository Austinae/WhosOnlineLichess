from threading import Thread
from time import sleep
from tkinter import Button, Label, Tk, Entry
from requests import get
from bs4 import BeautifulSoup
from playsound import playsound

class App(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.refreshRate = 3

        self.names = {}
        self.filepath = "names.txt"
        namesraw = []
        with open(self.filepath) as fp:
            line = fp.readline()
            while line:
                namesraw.append(line.strip())
                line = fp.readline()
        fp.close()

        for name in namesraw:
            self.names[name] = self.isPlayerOnline(name)

        self.labels = []
        for name in self.names:
            if self.isPlayerOnline(name) is False:
                label = Label(self, text=name + " is offline", font=("Helvetica", 16), bg="white")
            else:
                label = Label(self, text=name + " is online", font=("Helvetica", 16), bg="green")
            label.pack(side="top", expand="yes", fill="both")
            self.labels.append(label)

        self.entry = Entry(self)
        self.entry.pack(side="bottom", fill="x")
        self.button = Button(self, text="Add Name", command=lambda: self.addName(self.entry.get()))
        self.button.pack(side="bottom", fill="x")

        self.title("Lichess Friends Activity")
        self.geometry("500x800+300+100")

        self.isRunning = Label(self, text="Stopped.")
        self.isRunning.pack(side="bottom", fill="x")
        self.play_button = Button(self, text="Play", command=self.play)
        self.play_button.pack(side="bottom", pady=2)
        self.stop_button = Button(self, text="Stop", command=self.stop)
        self.stop_button.pack(side="bottom", pady=2)
        self._thread, self._pause, self._stop = None, False, True

    def isPlayerOnline(self, playername):
        page = get("https://lichess.org/@/" + playername)
        soup = BeautifulSoup(page.content, 'html.parser')
        div = soup.find("div", {"class": "box__top user-show__header"})
        try:
            if div.find("h1", {"class": "user-link online"}):
                return True
            return False
        except Exception:
            pass


    def action(self):
        for x, name in enumerate(self.names):
            if self._stop:
                return
            isOnline = self.names[name]
            try:
                # If we already know that the player is online then only check if he's offline
                if isOnline is True:
                    if self.isPlayerOnline(name) is False:
                        playsound('out.mp3')
                        self.names[name] = False
                        self.labels[x]["text"] = name + " is offline"
                        self.labels[x]["bg"] = "white"

                # If we already know that the player is offline then only check if he's online
                elif isOnline is False:
                    if self.isPlayerOnline(name) is True:
                        playsound('in.mp3')
                        self.names[name] = True
                        self.labels[x]["text"] = name + " is online"
                        self.labels[x]["bg"] = "green"

            except Exception:
                print("Your input or something went wrong")
                pass

        sleep(self.refreshRate)
        self.action()

    def play(self):
        if self._thread is None:
            self._stop = False
            self._thread = Thread(target=self.action)
            self._thread.start()
        self._pause = False
        self.isRunning["text"] = "Online"
        self.play_button.configure(text="Pause", command=self.pause)

    def pause(self):
        self._pause = True
        self.isRunning["text"] = "Pause"
        self.play_button.configure(text="Play", command=self.play)

    def stop(self):
        if self._thread is not None:
            self._thread, self._pause, self._stop = None, False, True
        self.isRunning["text"] = "Stopped"
        self.play_button.configure(text="Play", command=self.play)

    def addName(self, entry):
        self.stop()
        try:
            if len(entry) > 3 and entry not in self.names:
                self.names[entry] = False
                with open(self.filepath, "a") as fp:
                    fp.write("\n"+entry)
                fp.close()
                if self.isPlayerOnline(entry) is False:
                    label = Label(self, text=entry + " is offline", font=("Helvetica", 16), bg="white")
                else:
                    label = Label(self, text=entry + " is online", font=("Helvetica", 16), bg="green")
                label.pack(side="top", expand="yes", fill="both")
                self.labels.append(label)
        except Exception:
            pass
        self.play()


App().mainloop()