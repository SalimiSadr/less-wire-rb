# coding=utf-8
from __future__ import unicode_literals

import os
import time
import wave
import pyaudio
import requests
import subprocess
import urllib.parse
import urllib.request
from os import listdir
from playsound import playsound
import speech_recognition as sr
from os.path import isfile, join


from blockext import *

m = sr.Microphone()
r = sr.Recognizer()

FORMAT = pyaudio.paInt16
RATE = 44100
VOICES_PATH = "./robot_voices/"
NAME_COUNTER = 0


def listen_and_record(path):

    global r
    print("now listening!")
    global m
    with m as source:
        try:
            print("trying!!!")
            r.adjust_for_ambient_noise(source)
            print("Set minimum energy threshold to {}".format(r.energy_threshold))
            print("*" * 100, "\n", "*" * 100)
            print("Start Speaking")
            data = r.listen(source, timeout=100)
            wavdata = data.get_wav_data()
            record_to_file(path, wavdata)

        except sr.WaitTimeoutError as e:
            print (e)
            print ("Listening again...")
            listen_and_record(path)

        except Exception as e:
            print(e)

def STT(file_path, Lang="fa-IR"):
    print("1")
    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), file_path)
    AUDIO_FILE = "./" + file_path
    print("2")
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)
        print ("Now recognizing...")
        if Lang == "fa-IR":
            print("In first fa-IR")
            try:
                print("Trying ..")
                Text = r.recognize_google(audio, language=Lang)
                print ("Recognized:  " + Text)
                return Text
            except sr.UnknownValueError:
                print("Didn't catch that.")
                data = "NONE"
                counter = 0
                while (counter < 100) & (data == "NONE"):
                    listen_and_record('speech.wav')
                    data = STT('speech.wav')
                if counter >= 100:
                    return "NONE"
                else:
                    return data
            except sr.RequestError as e:
                print("Couldn't request results from Google Speech Recognition service; {0}".format(e))
                # with open('speech.wav.txt', 'r') as f:
                #     Text = f.read()
                # print("Recognized:  " + Text)
                # return Text

            except BadStatusLine as e:
                with open('speech.wav.txt', 'r') as f:
                    Text = f.read().decode('utf-8')
                print ("Recognized:  " + Text)
                return Text
            except Exception as e:
                logging.error(traceback.format_exc())
                print(traceback.format_exc())
                print(e)
        else:
            try:
                Text = r.recognize_google(audio, language=Lang)
                print ("Recognized:  " + Text)
                return Text
            except sr.UnknownValueError:
                print("Didn't catch that.")
                data = "NONE"
                counter = 0
                # if it cannot recognize anything, it listens again for 100 times
                while (counter < 100) & (data == "NONE"):
                    listen_and_record('speech.wav')
                    data = STT('speech.wav', Lang)
                if counter >= 100:
                    return "NONE"
                else:
                    return data
            except sr.RequestError as e:
                print("Couldn't request results from Google Speech Recognition service; {0}".format(e))
                print("Recognizing the speech using PocketSphinx...")
                Text = r.recognize_sphinx(audio)
                print ("Recognized:  " + Text)
                return Text

def record_to_file(path, data):
    """
    Records from the microphone or wavdata and generates the resulting data to "path"

    :param path: output ".wav" audio file path
    :param data: input audio wavdata
    """
    p = pyaudio.PyAudio()
    sample_width = p.get_sample_size(FORMAT)
    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

def playvc(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy(): 
        pygame.time.Clock().tick(10)

def agptts(text):
    global NAME_COUNTER
    NAME_COUNTER += 1
    vcfilename = VOICES_PATH + "vcm" + str(NAME_COUNTER) + ".mp3"
    print("-------------==========================------------------")
    print("Requesting..")
    URL = f"http://api.farsireader.com/ArianaCloudService/ReadTextGET?APIKey=RS93OYTM9HOFBKA&Text={text}&Speaker=Male1&Format=mp3"
    r = requests.get(url = URL)
    print("-------------") 
    print("Done requesting")
    print("-------------==========================------------------")
    urllib.request.urlretrieve(URL, vcfilename)
    print(r)
    return vcfilename

class Example:
    def __init__(self):
        self.foo = 0

    def _problem(self):
        if time.time() % 8 > 4:
            return "The Scratch Sensor board is not connected. Foo."

    def _on_reset(self):
        print("""
        Reset! The red stop button has been clicked,
        And now everything is how it was.
        ...
        (Poetry's not my strong point, you understand.)
        """)

    @predicate("not %b")
    def not_(self, value):
        return not value

    @command("say %s for %n secs", is_blocking=True)
    def say_for_secs(self, text="Hello", duration=5):
        print(text)
        time.sleep(duration)

    @command("play note %n")
    def play_note(self, note):
        print("DING {note}".format(note=note))
        time.sleep(2)

    @reporter("colour of %m.pizza flavour pizza", defaults=["tomato"])
    def pizza_colour(self, pizza):
        return {
            "tomato": "red",
            "cheese": "yellow",
            "hawaii": "orange and blue",
        }[pizza]

    @reporter("id %s")
    def id(self, text):
        """Tests strings can get passed from Snap! to Python and back."""
        print(text)
        return text

    @command("set number to %n% units")
    def percent(self, number=42):
        print(number)

    @command("set foo to %s")
    def set_foo(self, value=''):
        self.foo = value

    @reporter("foo")
    def get_foo(self):
        return self.foo

    @command("ü")
    def x(self):
        pass

    @command("set color to %c")
    def set_color(self, c):
        print(c)

    @command("سلام چطوری")
    def salam(self):
    	print("hoorayyyyyy")

    @command("say hello")
    def say_hello(self):
        file_path = "./voice_commands/query.wav"
        print('befor listening!')
        listen_and_record(file_path)
        print('after listneing!!!')
        stt_text = STT(file_path)
        print("stt")
        if "سلام" in stt_text:
            text = urllib.parse.quote("سلام.من ربات شما هستم.نام شما چیست ؟", safe='')
            vcname = agptts(text)
            playsound(vcname)
            os.remove(vcname)
            print(text)
            print(" Congrats Baby :* ")
        print(stt_text)
    

descriptor = Descriptor(
    name = "Fancy Spaceship",
    port = 1234,
    blocks = get_decorated_blocks_from_class(Example),
    menus = dict(
        pizza = ["tomato", "cheese", "hawaii"],
    ),
)

extension = Extension(Example, descriptor)

if __name__ == "__main__":
    extension.run_forever(debug=True)

