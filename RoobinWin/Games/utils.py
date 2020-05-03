# coding=utf-8
from __future__ import unicode_literals
import os
import sys
import xlwt
import xlrd
import time
import wave
import random
import pyaudio
import tkinter
import requests
import threading
import subprocess
import contextlib
import wikipediaapi
import urllib.parse
import RoobinControl
import urllib.request
from os import listdir
from os.path import dirname
from tkinter import PhotoImage
from PIL import ImageTk, Image
import speech_recognition as sr
from playsound import playsound
from os.path import isfile, join

m = sr.Microphone()
r = sr.Recognizer()


FORMAT = pyaudio.paInt16
RATE = 44100
VOICES_PATH = "./robot_voices/"
SPEAKING_SPEED = 155
SPEAKING_PITCH = 100
NAME_COUNTER = 0
LANG = "fa"

ser = None
port=""

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

def speech_to_text(file_path, Lang="fa-IR"):
    global LANG
    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), file_path)
    AUDIO_FILE = "./" + file_path
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)
        print ("Now recognizing...")
        if LANG == "fa-IR":
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
                Text = r.recognize_google(audio, language=LANG)
                print ("Recognized:  " + Text)
                return Text
            except sr.UnknownValueError:
                print("Didn't catch that.")
                data = "NONE"
                counter = 0
                # if it cannot recognize anything, it listens again for 100 times
                while (counter < 100) & (data == "NONE"):
                    listen_and_record('speech.wav')
                    data = speech_to_text('speech.wav', LANG)
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

def listen_and_record(path):

    global r
    print("now listening!")
    global m
    with m as source:
        try:
            print("trying!!!")
            r.adjust_for_ambient_noise(source)
            cwd = os.getcwd()
            beeppath = dirname(cwd) + "\\"
            playsound(f"{beeppath}Sounds\\beep1.mp3")
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

def playthesound(vcname):
    playsound(vcname)
    # Sleep to finish
    fname = vcname
    with contextlib.closing(wave.open(fname,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    # time.sleep(duration * 1.1)
    # os.remove(vcname)

def text_to_speech_espeak(text):
    global NAME_COUNTER, LANG
    NAME_COUNTER += 1
    rvcfilename = VOICES_PATH + "vcm" + str(NAME_COUNTER) + ".wav" 
    text_file_path='./static/text.txt'
    F=open(text_file_path,"w", encoding="utf8")
    F.write(text)
    F.close()
    if LANG == "fa":
        os.system(f'espeak -vmb-ir1 -p{SPEAKING_PITCH} -g13 -s{SPEAKING_SPEED} -w {rvcfilename} -f {text_file_path}')
    elif LANG == "en":
        os.system(f'espeak -p{SPEAKING_PITCH} -g13 -s{SPEAKING_SPEED} -w {rvcfilename} -f {text_file_path}')
    return rvcfilename

def say_offline(text):

    print("__In say_offline funcion__")
    vcname = text_to_speech_espeak(text)
    fname = vcname
    with contextlib.closing(wave.open(fname,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)

    phonemes, times = RoobinControl.phonemes_gen(vcname)
    # Set up a thread for the speech sound synthesis, delay start by soundDelay
    # Set up a thread for the speech movement
    t2 = threading.Thread(target=RoobinControl.moveSpeechMouth, args=(phonemes,times, vcname))
    t2.start()
    # Set up a thread for the speech sound synthesis
    t = threading.Thread(target=playthesound, args=(vcname,))
    t.start()
    return duration


if __name__ == "__main__":
    say_offline("salam")