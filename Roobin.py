# coding=utf-8
from __future__ import unicode_literals

import os
import time
import wave
import random
import pyaudio
import requests
import subprocess
import urllib.parse
import RoobinControl
import urllib.request
from os import listdir
from blockext import *
import speech_recognition as sr
from playsound import playsound
from os.path import isfile, join


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

def speech_to_text(file_path, Lang="fa-IR"):
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
                    data = speech_to_text('speech.wav')
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
                    data = speech_to_text('speech.wav', Lang)
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

def agptts(txt):
    text = urllib.parse.quote(txt, safe='')
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

def say(text):
    vcname = agptts(text)
    playsound(vcname)
    os.remove(vcname)

class Roobin:

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

    @command("سلام چطوری")
    def salam(self):
    	print("hoorayyyyyy")

    @command("سلام کن")
    def say_hello(self):
        file_path = "./voice_commands/query.wav"
        print('befor listening!')
        listen_and_record(file_path)
        print('after listneing!!!')
        speech_to_text_text = speech_to_text(file_path)
        print("speech_to_text")
        if "سلام" in speech_to_text_text:
            text = "سلام.من ربات شما هستم.نام شما چیست ؟"
            say(text)
            print(text)
            print(" Congrats Baby :* ")
        print(speech_to_text_text)

    @command("بگو %s")
    def text_to_speech(self, text):
        print("trying to speak!!!!")
        say(text)
        print("just said!")

    @command("بازی حدس عدد")
    def play_game(self):
        number_from_client = 0
        generated_num = random.randint(1, 100)
        print("*" * 100)
        print(generated_num)
        print("*" * 100)
        win = False
        say("اگه میتوانی عدد من را حدس بزن")
        for i in range(3):
            try:
                print("===============Here at getting Voice ..================")
                print("==============----------------------------------------------=========================================")
                file_path = "./voice_commands/Gamequery.wav"
                print('Waiting for the query.')
                listen_and_record(file_path)
                print('Got the answer')
                number_from_client = int(speech_to_text(file_path))
                print(number_from_client)
            except Exception as e :
                print(e)
                print("Problem in Play Game Func")

            if number_from_client > generated_num:
                print("===============Less than.================")
                print("==============----------------------------------------------=========================================")
                say("پایین تر")
            elif number_from_client < generated_num:
                print("===============Bigger.================")
                print("==============----------------------------------------------=========================================")
                say("بالاتر")
            else:
                print("===============You Won.================")
                print("==============----------------------------------------------=========================================")
                say("تو بردی. تبریک")
                win = True
                break

        if not win:
            say("من بردم")
            print("===============I Won.================")
            print("==============----------------------------------------------=========================================")

        print("ANY BUG ????")

    @command("موتور %s را به %s درجه بچرخان")
    def move_motor(self, motor, angle):
        print("move {motor} by {angle} degrees!".format(motor=motor, angle=angle))
        print("*" * 10)
        print(int(motor),int(angle))
        print("*" * 10)
        RoobinControl.move(int(motor),int(angle),10)
        print("...")



descriptor = Descriptor(
    name = "Fancy Spaceship",
    port = 1234,
    blocks = get_decorated_blocks_from_class(Roobin),
    menus = dict(
        pizza = ["tomato", "cheese", "hawaii"],
    ),
)

extension = Extension(Roobin, descriptor)

if __name__ == "__main__":
    extension.run_forever(debug=True)
