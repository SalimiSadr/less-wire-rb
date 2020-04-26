# coding=utf-8
from __future__ import unicode_literals
import sys
import os
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
from blockext import *
from tkinter import PhotoImage
from PIL import ImageTk, Image
import speech_recognition as sr
from playsound import playsound
from os.path import isfile, join
from num2fawords import words, ordinal_words
from persiantools.jdatetime import JalaliDate
from future.backports.http.client import BadStatusLine


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

A_PROGRAM_IS_RUNNING = False


def init(portName):
    # pickup global instances of port, ser and sapi variables
    global port, ser

    # Search for the Roobin serial port
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        # print ("p0:" + p[0])
        # print ("p1:" + p[1])
        # If port has Roobin connected save the location
        if portName in p[1]:
            port = p[0]
            print ("Roobin found on port:" + port)
        elif portName in p[0]:
            port = p[0]
            print ("Roobin found on port:" + port)

    # If not found then try the first port
    if port == "":
        for p in ports:
            port = p[0]
            print ("Roobin probably found on port:" + port)
            break

    if port == "":
        print ("Roobin port " + portName + " not found")
        return False

    # Open the serial port
    ser = serial.Serial(port, 19200)

    # Set read timeout and write timeouts to blocking
    ser.timeout = None
    ser.write_timeout = None

    # Make an initial call to Festival without playing the sound to check it's all okay
    text = "Hi"

    # Create a bash command with the desired text. The command writes two files, a .wav with the speech audio and a .txt file containing the phonemes and the times.
    # speak (text)

    return True

def listen_and_record(path):

    global r
    print("now listening!")
    global m
    with m as source:
        try:
            print("trying!!!")
            r.adjust_for_ambient_noise(source)
            playsound("Sounds/beep1.mp3")
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
    text_file_path='text.txt'
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

def say(text):
    print("In say func 1...")
    vcname = agptts(text)
    print("In say func 2...")
    phonemes, times = RoobinControl.phonemes_gen(vcname)
    print("In say func 3...")
    # Set up a thread for the speech sound synthesis, delay start by soundDelay
    # Set up a thread for the speech movement
    t2 = threading.Thread(target=RoobinControl.moveSpeechMouth, args=(phonemes,times, vcname))
    t2.start() 
    print("In say func 4...")
    # Set up a thread for the speech sound synthesis
    t = threading.Thread(target=playthesound, args=(vcname,))      
    t.start()
    print("In say func 5...")
    global time_from_start
    time_from_start = time.time()
    # if untilDone, keep running until speech has finished    
    #if untilDone:
    #    totalTime = times[len(times) - 1]
    #    startTime = time.time()
    #    while time.time() - startTime < totalTime:
    #        continue
    # playsound(vcname)
    # os.remove(vcname)

def server_run_forever_func():
    extension.run_forever(debug=True)

def save_generated_s2e():
    time.sleep(2)
    link = "http://localhost:1234/_generate_blocks/scratch/en/Scratch%20Fancy%20Spaceship%20English.s2e"
    print(requests.get(link))
    urllib.request.urlretrieve(link, 'S2e_file/Roobin.s2e')

def delete_all_voices():
    mydir = "robot_voices"
    filelist = [ f for f in os.listdir(mydir) ]
    for f in filelist:
        os.remove(os.path.join(mydir, f))

class Roobin:

    def __init__(self):
        self.foo = 0
        """
         P (THE THREAD USED FOR SOME OF BLOCKS FOR EASE OF TERMINATION WITH RED BUTTON)
        """
        self.p = "FOR SOUND PLAYING"
        self.stt_var = ""

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
        try:
            # TERMINATE P (THE THREAD USED FOR SOME OF BLOCKS FOR EASE OF TERMINATION WITH RED BUTTON)
            self.p.terminate()
        except:
            print("DO NOT TRY ON THIS BLOCK")

    @command("تغییر زبان به  %m.lang_list", defaults=['fa'])
    def set_language(self, lang_list):
        global LANG
        selected_lang = {
            "fa": 1,
            "en": 2
        }[lang_list]

        if selected_lang == 1:
            LANG = "fa"
        elif selected_lang == 2:
            LANG = "en"

    @command("سرعت گفتار = %s")
    def set_speak_speed(self, text):
        global SPEAKING_SPEED
        SPEAKING_SPEED = int(text)
        print(f"SPEAKING SPEED CHANGED TO {SPEAKING_SPEED}")

    @command("نازکی صدا = %s")
    def set_speak_pitch(self, text):
        global SPEAKING_PITCH
        SPEAKING_PITCH = int(text)
        print(f"SPEAKING PITCH CHANGED TO {SPEAKING_PITCH}")

    @reporter("x")
    def get_stt_var(self):
        return self.stt_var

    @command("صدا را بشنو و در x ذخبره کن .")
    def set_stt_var(self):

        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            file_path = "./voice_commands/query.wav"
            print('befor listening!')
            listen_and_record(file_path)
            print('after listneing!!!')
            speech_to_text_text = speech_to_text(file_path)
            print("speech_to_text")
            try:
                print("I HEARD A NUMBER !")
                speech_to_text_text = int(speech_to_text_text)
            except:
                pass

            self.stt_var = speech_to_text_text
            time.sleep(1)
            A_PROGRAM_IS_RUNNING = False

        else:
            print("A PROGRAM IS RUNNING..")

    @command("عدد رندوم بین %s و %s")
    def myRandom(self,FNum,SNum):

        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            try:
                A=max(int(FNum),int(SNum))
                B=min(int(FNum),int(SNum))
                res=random.randint(B,A)
                print(res)
                #dg hamin stt_var ro copy kardam
                self.stt_var = res
                time.sleep(0.5)
            except:
                pass
            A_PROGRAM_IS_RUNNING = False
        else:
            print("A PROGRAM IS RUNNING..")

    @command("ریکاوری")
    def recovery(self):
        RoobinControl.recovery_util()        

    @command("معرفی")
    def introduce(self):
        print("IN INTRODUCE !!!!")
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass
        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            text = "سلام ، من روبین هستم ، دوسته خوبه شما"
            w = say_offline(text)
            time.sleep(w * 1.1)
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("سلام کن")
    def say_hello(self):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass
        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            file_path = "./voice_commands/query.wav"
            print('befor listening!')
            listen_and_record(file_path)
            print('after listneing!!!')
            speech_to_text_text = speech_to_text(file_path)
            print("speech_to_text")
            if "سلام" in speech_to_text_text:
                text = "سلام.من روبین هستم.از آشنایی با شما خوشحالم"
                w = say_offline(text)
                time.sleep(w * 1.1)

            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("بگو آفلاین %s")
    def begoo(self,text):
        print("IN BEGOO !!!!")
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass
        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            w = say_offline(text)
            time.sleep(w * 1.1)
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")
        #os.system()

    @command("جست و جو در ویکی پدیا")
    def search_in_wikipedia(self):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            file_path = "./voice_commands/Gamequery.wav"
            print('befor listening!')
            listen_and_record(file_path)
            print('after listneing!!!')
            speech_to_text_text = speech_to_text(file_path)
            print("speech_to_text")
            print(speech_to_text_text)
            wiki_wiki = wikipediaapi.Wikipedia('fa')
            page_py = wiki_wiki.page(speech_to_text_text)
            if page_py.exists() == True:
                try:
                    result=page_py.summary.split('.')[0] + page_py.summary.split('.')[1]
                    #say(result)
                    #feel free to use online version of say function(say()) instead of say_offline()
                    # freeze_support()
                    # print("WTFFFFFFF")
                    # self.p = Process(target=say_offline, args=(result,))
                    # self.p.start()
                    w = say_offline(result)
                    time.sleep(w * 1.1)
                    # self.p.terminate()
                    #print('yes')
                except:
                    #print('no')
                    # freeze_support()
                    # self.p = Process(target=say_offline, args=(page_py.summary,))
                    # self.p.start()
                    w = say_offline(page_py.summary)
                    time.sleep(w * 1.1)
                    # self.p.terminate()
            else:
                say_offline('این صفحه وجود ندارد')
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("چیستان")
    def riddle_game(self):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            riddles_list=[]
            erfan=[]
            nn=0
            a=0
            #a is my index for df['C']
            file_path = "./voice_commands/Gamequery.wav"
            the_path="./facts-numbers-riddles/ForGodSake.xls"

            the_list=[]
            #yes_list=['بله','بلی','آره','آری','بریم','بریم چیستان بعدی','اره','ار','آر','بعدی','برو','بر']
            while nn==0:
                nn==1
                gg=0
                the_Flist=[]

                wb = xlrd.open_workbook(the_path) 
                sheet = wb.sheet_by_index(0)


                for i in range(sheet.nrows):
                    the_Flist.append([sheet.cell_value(i, 0),sheet.cell_value(i, 1),sheet.cell_value(i, 2)])

                a=0

                if sheet.cell_value(0,2)==sheet.cell_value(sheet.nrows - 2,2):
                    a=0
                    if type(the_Flist[0][2]==type(1.23)):
                        the_Flist[0][2]+=1
                    else:
                        temp=float(the_Flist[0][2])
                        temp+=1
                        the_Flist[0][2]=temp
                        
                else:
                    for i in range(sheet.nrows-1):
                        if sheet.cell_value(i,2) == sheet.cell_value(sheet.nrows - 2,2):
                            a=i
                            if type(the_Flist[i][2])==type(1.23):
                                the_Flist[i][2]+=1
                            else:
                                temp=float(the_Flist[i][2])
                                temp+=1
                                the_Flist[i][2]=temp                
                            break

                w = say_offline(sheet.cell_value(a,0))
                time.sleep(w * 1.1)
                #print(sheet.cell_value(a,1))
                the_list=sheet.cell_value(a,1).split(',')
                #print(the_list)


                wbk = xlwt.Workbook()
                sheet = wbk.add_sheet('python')
                i=0

                while i<len(the_Flist):
                    sheet.write(i,0,the_Flist[i][0])
                    sheet.write(i,1,the_Flist[i][1])
                    sheet.write(i,2,the_Flist[i][2])
                    
                    i+=1
                wbk.save(the_path)



                #the_list=df['B'][a].split(',')
                #print(the_list)
                #say(df['A'][a])
                #feel free to use online version of say function(say()) instead of say_offline()
                #say_offline(df['A'][a])
                #time.sleep(10)
                try:
                    url='http://www.google.com/'
                    requests.get(url, timeout=5)
                    print('befor listening!')
                    listen_and_record(file_path)
                    print('after listneing!!!')
                    speech_to_text_text = speech_to_text(file_path)
                    print("speech_to_text")
                    print(speech_to_text_text)
                except:
                    window = tkinter.Tk()
                    window.title("Roobin")
                    window.geometry('240x170')
                    window.configure(bg='red')
                    window.attributes("-topmost", True)
                    window.iconbitmap('.\photo6019163393241493720__1___4__rCb_icon.ico')
                    e = tkinter.Entry(window,width=35,borderwidth=5)
                    e.grid(row=0, column=0, columnspan=1, padx=10, pady=10)
                    e.insert(0, "Enter Your Answer: ")
                    def clear(event):
                        e.delete(0, tkinter.END)

                    e.bind("<Button-1>", clear)


                    def button_done():
                        erfan.append(e.get())
                        window.destroy()

                    myButton_done = tkinter.Button(window, text="Done!",borderwidth=5,font='boldfont',padx=80,pady=40 ,command=button_done,fg="#1227D3",bg="#209139")

                    myButton_done.grid(row=1,column=0,columnspan=2)
                    window.mainloop()
                    speech_to_text_text=str(erfan[-1])


                for i in the_list:
                    if speech_to_text_text in i:
                        gg=1
                        break
                if gg==1:
                    print('barikallaaaaaaa')
                    w = say_offline("تبریک میگم. جوابت درست بود")
                    #playsound("./GameVoice/well_done.mp3")
                    time.sleep(w * 1.1)

                else:
                    print('i dont think so')
                    w = say_offline(".جوابه شما اشتباه بود")
                    #playsound("./GameVoice/sorry.mp3")
                    time.sleep(w * 1.1)

                nn=1
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("تاریخ امروز")
    def today(self):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            erfan = (JalaliDate.today().strftime("%c"))
            ls_erfan=erfan.split(" ")
            rooz=ls_erfan[0]
            chandom=ls_erfan[1]
            maah=ls_erfan[2]
            saal=ls_erfan[3]
            if rooz == "Yekshanbeh":
                rooz="يکشنبه"
            elif rooz == "Doshanbeh":
                rooz="دوشنبه"
            elif rooz == "Seshanbeh":
                rooz="سه شنبه"
            elif rooz == "Chaharshanbeh":
                rooz="چهار شنبه"
            elif rooz == "Panjshanbeh":
                rooz="پنج شنبه"
            elif rooz == "Jomeh":
                rooz="جمعه"
            else:
                rooz = "شنبه"


            chandom= ordinal_words(int(chandom)) + "ه"

            if maah=="Farvardin":
                maah="فروردينه"
            elif maah=="Ordibehesht":
                maah="ارديبهشته"
            elif maah=="Khordad":
                maah="خرداده"
            elif maah=="Tir":
                maah="تيره"
            elif maah=="Mordad":
                maah="مرداده"
            elif maah=="Shahrivar":
                maah="شهريوره"
            elif maah=="Mehr":
                maah="مهره"
            elif maah=="Aban":
                maah="آبانه"
            elif maah=="Azar":
                maah="آذره"
            elif maah=="Dey":
                maah="ديه"
            elif maah=="Bahman":
                maah="بهمنه"
            elif maah=="Esfand":
                maah="اسفنده"


            result = "امروز" + " , " + rooz + " , " + chandom + " , " + maah + " , " + saal + " , " + "مي باشد."
            w = say_offline(result)
            time.sleep(w * 1.1)
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("اون روز چند شنبه بود")
    def chan_shanbeh(self):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            answers=[]
            window = tkinter.Tk()
            window.title("Roobin")
            #window.geometry('240x170')
            window.configure(bg='red')
            window.attributes("-topmost", True)
            window.iconbitmap('.\photo6019163393241493720__1___4__rCb_icon.ico')
            e = tkinter.Entry(window,width=5,borderwidth=5)
            e.grid(row=0, column=1)
            e.insert(0, "1399")

            e1 = tkinter.Entry(window,width=5,borderwidth=5)
            e1.grid(row=0,column=2)
            e1.insert(0,"10")

            e2 = tkinter.Entry(window,width=5,borderwidth=5)
            e2.grid(row=0,column=3)
            e2.insert(0,"15")


            def button_done():
                answers.append(e.get())
                answers.append(e1.get())
                answers.append(e2.get())
                window.destroy()

            myButton_done = tkinter.Button(window, text="چند شنبه",borderwidth=5,padx=40,font='boldfont' ,command=button_done,fg="#1227D3",bg="#209139")

            myButton_done.grid(row=1,column=0,columnspan=4)
            window.mainloop()

            erfan = (JalaliDate(int(answers[0]),int(answers[1]),int(answers[2])).strftime("%c"))
            ls_erfan=erfan.split(" ")
            rooz=ls_erfan[0]
            if rooz == "Yekshanbeh":
                rooz="يکشنبه"
            elif rooz == "Doshanbeh":
                rooz="دوشنبه"
            elif rooz == "Seshanbeh":
                rooz="سه شنبه"
            elif rooz == "Chaharshanbeh":
                rooz="چهار شنبه"
            elif rooz == "Panjshanbeh":
                rooz="پنج شنبه"
            elif rooz == "Jomeh":
                rooz="جمعه"
            else:
                rooz = "شنبه"
            w = say_offline(rooz)
            time.sleep(w*1.1)

            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("بازی جهت ها %m.pattern_game_difficulty",defaults=['متوسط'])
    def arrow_game(self,pattern_game_difficulty):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            game_difficulty=0
            little_mother = {
                "آسان":4,
                "متوسط":3,
                "سخت":2,
                "غیر ممکن":1
            }[pattern_game_difficulty]
            game_difficulty=little_mother
            a=(4-game_difficulty)+1

            GD="./High Scores/arrow game/GD={}.txt"
            High_Score=0
            HSS=0
            n=3
            new_score=0

            #playsound("./GameVoice/arrow_guide.mp3")
            # say_offline(
            #     "در این بازی در چشم های ربات , جهت هایی به طرف بالا , پایین , چپ و راست نمایش داده می شود."
            #     " اگر در چشم راست ربات بود , خلاف آن را و اگر در چشم چپ ربات بود خود"
            #     " آن جهت را در پنجره ای که برایتان باز می شود , وارد نمایید.")
            # time.sleep(25)
            #time.sleep(20)

            F=open("./High Scores/arrow game/GD={}.txt".format(a),"r")
            line=F.readline()
            High_Score=int(line)
            F.close()
            print("game difficulty is {}".format(a))
            if High_Score==0:
                print("you have no score with this game diffuculty")
            else:
                w = say_offline(f"بیشترین امتیازی که در این بازی کسب کرده اید ، {High_Score} بوده است.")
                #roobin must show the score from "./High Scores/repeating pattern game2/GD={}.txt".format(a)
                print("your high score is in this game difficulty is {}".format(str(High_Score)))

            time.sleep(w * 1.1)
            #playsound("./GameVoice/Readdy.mp3")
            w = say_offline("آماده باشید")
            os.system('cls' if os.name == 'nt' else 'clear')
            time.sleep(w * 1.1)


            mylist=[]
            result=[]
            os.system('cls' if os.name == 'nt' else 'clear')
            print("the pattern will show in 2 seconds")
            #playsound("./GameVoice/in 2 secconds.mp3")
            w = say_offline("الگو تا دو ثانیه ی دیگر نمایش داده می شود")
            time.sleep(w * 1.1)
            print("==============================SENDING======================================")
            for i in range(1000):
                jjj=random.randint(0,7)
                if jjj==0:
                    mylist.append("0")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - left arrow in left eye".format(str(i+1)))
                    #displaying the left arrow in left eye for game_difficulty second(s)
                    RoobinControl.eye("left","leftArrow",game_difficulty)
                    # time.sleep(game_difficulty)
                    #os.system('cls' if os.name == 'nt' else 'clear')

                elif jjj==1 :
                    mylist.append("1")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - up arrow in left eye".format(str(i+1)))
                    #displaying the up arrow in left eye for game_difficulty second(s)
                    RoobinControl.eye("left","upArrow",game_difficulty)
                    # time.sleep(game_difficulty)
                    #os.system('cls' if os.name == 'nt' else 'clear')

                elif jjj==2 :
                    mylist.append("2")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - right arrow in left eye".format(str(i+1)))
                    #displaying the right arrow in left eye for game_difficulty second(s)
                    RoobinControl.eye("left","rightArrow",game_difficulty)
                    # time.sleep(game_difficulty)
                    #os.system('cls' if os.name == 'nt' else 'clear')

                elif jjj==3 :
                    mylist.append("3")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - down arrow in left eye".format(str(i+1)))
                    #displaying the down arrow in left eye for game_difficulty second(s)
                    RoobinControl.eye("left","downArrow",game_difficulty)
                    # time.sleep(game_difficulty)
                    #os.system('cls' if os.name == 'nt' else 'clear')

                elif jjj==4 :
                    mylist.append("4")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - left arrow in right eye".format(str(i+1)))
                    #displaying the left arrow in right eye for game_difficulty second(s)
                    RoobinControl.eye("right","leftArrow",game_difficulty)
                    # time.sleep(game_difficulty)
                    #os.system('cls' if os.name == 'nt' else 'clear')

                elif jjj==5 :
                    mylist.append("5")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - up arrow in right eye".format(str(i+1)))
                    #displaying the up arrow in right eye for game_difficulty second(s)
                    RoobinControl.eye("right","upArrow",game_difficulty)
                    # time.sleep(game_difficulty)
                    #os.system('cls' if os.name == 'nt' else 'clear')

                elif jjj==6 :
                    mylist.append("6")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - right arrow in right eye".format(str(i+1)))
                    #displaying the right arrow in right eye for game_difficulty second(s)
                    RoobinControl.eye("right","rightArrow",game_difficulty)
                    # time.sleep(game_difficulty)
                    #os.system('cls' if os.name == 'nt' else 'clear')

                else:
                    mylist.append("7")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - down arrow in right eye".format(str(i+1)))
                    #displaying the down arrow in right eye for game_difficulty second(s)
                    RoobinControl.eye("right","downArrow",game_difficulty)
                    # time.sleep(game_difficulty)
                    #os.system('cls' if os.name == 'nt' else 'clear')

                start=time.time()
                window = tkinter.Tk()
                window.title("Roobin")
                window.attributes("-topmost", True)
                window.iconbitmap('.\photo6019163393241493720__1___4__rCb_icon.ico')


                def button_click_left():
                    mylabel=tkinter.Label(window,text="left ")
                    result.append(("0","6"))
                    window.destroy()

                def button_click_right():
                    mylabel=tkinter.Label(window,text="right")
                    result.append(("2","4"))
                    window.destroy()

                def button_click_top():
                    mylabel=tkinter.Label(window,text="right")
                    result.append(("1","7"))
                    window.destroy()

                def button_click_bot():
                    mylabel=tkinter.Label(window,text="right")
                    result.append(("3","5"))
                    window.destroy()

                left = ImageTk.PhotoImage(file = ".\\arrow keys\\download.jpg")
                bot = ImageTk.PhotoImage(file =".\\arrow keys\\download(1).jpg")
                right = ImageTk.PhotoImage(file =".\\arrow keys\\download(2).jpg")
                top = ImageTk.PhotoImage(file =".\\arrow keys\\download(3).jpg")

                myButton_left = tkinter.Button(window,image=left, text="left",font='boldfont',padx=28,pady=40, command=button_click_left, fg="gray", bg="#fc0394")
                myButton_right = tkinter.Button(window,image=right, text="right",font='boldfont',padx=26,pady=40, command=button_click_right, fg="gray", bg="#EF1839")
                myButton_bot = tkinter.Button(window,image=bot, text="bot",font='boldfont',padx=26,pady=40 ,command=button_click_bot,fg="gray",bg="#209139")
                myButton_top = tkinter.Button(window,image=top ,text="top",font = 'boldfont',padx = 27,pady=40,command = button_click_top, fg ="gray" , bg = "yellow")
                myButton_left.grid(row=1,column=0)
                myButton_right.grid(row=1,column=2)
                myButton_bot.grid(row=1,column=1)
                myButton_top.grid(row=0,column=1)

                window.mainloop()
                end=time.time()
                quest_time=(end-start)

                wrong=0
                if (mylist[-1]!=result[-1][0] and  mylist[i]!=result[-1][1]) or quest_time>game_difficulty+1.5:
                    if mylist[-1]!=result[-1][0] and  mylist[i]!=result[-1][1]:
                        wrong=1
                    new_score=i
                    break

            if wrong==1:
                print("your answer was wrong")
                #playsound("./GameVoice/wrong answer(arrow).mp3")
                w = say_offline("جوابه شما اشتباه بود")
                print("REAL ANSWER = ",mylist)
                print("MY ANSWER = ", result)
                time.sleep(w * 1.1)
            else:
                print("you answered soooo late")
                #playsound("./GameVoice/late.mp3")
                w = say_offline("خیلی دیر جواب دادی")
                time.sleep(w * 1.1)

            print("you lost in level {} with difficulty{}".format(str(len(mylist)),str(a)))
            #playsound("./GameVoice/Game over.mp3")
            if new_score>High_Score:
                print("this is the highest score!")
                #playsound("./GameVoice/new_record.mp3")
                w = say_offline("تبریک. رکورده جدیدی با این درجه سختی کسب کردی")
                F = open("./High Scores/arrow game/GD={}.txt".format(str(a)),"w")
                F.write(str(new_score))
                F.close()
                time.sleep(w * 1.1)

            """
            RELEASES MUTEX
            """
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("الگوها آفلاین  %m.pattern_game_difficulty",defaults=['متوسط'])
    def repeating_pattern_game2(self,pattern_game_difficulty):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            game_difficulty=0
            little_mother = {
                "آسان":4,
                "متوسط":3,
                "سخت":2,
                "غیر ممکن":1
            }[pattern_game_difficulty]
            game_difficulty=little_mother
            a=(4-game_difficulty)+1
            #GD="./High Scores/repeating pattern game2/GD={}.txt"
            High_Score=0
            HSS=0
            n=3

            voice1 = 'متوجه نشدم. لطفا تکرار کنید'
            voice2 = 'تا دو ثانیه ی دیگر , بازی شروع می شود'
            guide1 = "در این بازی چشم های ربات،  به صورت رندوم چشمک میزنند. وظیفه ی شما تکرار کردنه الگوها می باشد"
            guide2 = "لطفا الگو را با صدای بلند و بدون توقف زیاد تکرار کنید. به این مثال توجه کنید"


            #playsound("./GameVoice/guide1.mp3")
            #say_offline(guide1)
            #time.sleep(11)


            F=open("./High Scores/repeating pattern game2/GD={}.txt".format(a),"r")
            line=F.readline()
            High_Score=int(line)
            F.close()
            print("game difficulty is {}".format(a))
            if High_Score==0:
                print("you have no score with this game diffuculty")
            else:
                #roobin must show the score from "./High Scores/repeating pattern game2/GD={}.txt".format(a)
                print("your high score is in this game difficulty is {}".format(str(High_Score)))
            time.sleep(3.5)
            #playsound("./GameVoice/Readdy.mp3")
            w = say_offline("آماده باشید")
            os.system('cls' if os.name == 'nt' else 'clear')
            time.sleep(w * 1.1)

            gg=0
            while(gg==0):
                mylist=[]
                result=[]
                os.system('cls' if os.name == 'nt' else 'clear')
                print("the pattern will show in 2 seconds")
                #playsound("./GameVoice/in 2 secconds.mp3")
                w = say_offline(voice2)
                print("level{}".format(str(n-2)))
                #say('مرحله {}'.format(str(n-2)))
                time.sleep(w * 1.1)

                for i in range(n):
                    if random.randint(0,1)==0:
                        mylist.append("left")
                        #os.system('cls' if os.name == 'nt' else 'clear')
                        print("{} - left".format(str(i+1)))
                        #blinking the left eye for game_difficulty seconds
                        RoobinControl.eye("left","full_on",game_difficulty)
                        # time.sleep(game_difficulty)
                        #os.system('cls' if os.name == 'nt' else 'clear')

                    else:
                        mylist.append("right")
                        #os.system('cls' if os.name == 'nt' else 'clear')
                        print("{} - right".format(str(i+1)))
                        #blinking the right eye for game_difficulty seconds
                        RoobinControl.eye("right","full_on",game_difficulty)
                        # time.sleep(game_difficulty)
                        #os.system('cls' if os.name == 'nt' else 'clear')

                window = tkinter.Tk()
                window.title("Roobin")
                window.attributes("-topmost", True)
                window.iconbitmap('.\photo6019163393241493720__1___4__rCb_icon.ico')

                def button_click_left():
                    mylabel=tkinter.Label(window,text="left ")
                    result.append("left")

                def button_click_right():
                    mylabel=tkinter.Label(window,text="right")
                    result.append("right")

                def button_done():
                    window.destroy()


                myButton_left = tkinter.Button(window, text="<- left",font='boldfont',padx=28,pady=40, command=button_click_left, fg="gray", bg="#FFDA33")
                myButton_right = tkinter.Button(window, text="right ->",font='boldfont',padx=26,pady=40, command=button_click_right, fg="gray", bg="#EF1839")
                myButton_done = tkinter.Button(window, text="Done!",font='boldfont',padx=80,pady=40 ,command=button_done,fg="gray",bg="#209139")

                myButton_left.grid(row=0,column=0)
                myButton_right.grid(row=0,column=1)
                myButton_done.grid(row=1,column=0,columnspan=2)
                window.mainloop()

                if result==mylist:
                    print("you won level {}".format(str(n-2)))
                    #playsound("./GameVoice/you won.mp3")
                    w = say_offline("تبریک میگم. این مرحله را رد کردی")
                    time.sleep(w * 1.1)
                    if n-2 > High_Score:

                        print("this is the highest score!")
                        F=open("./High Scores/repeating pattern game2/GD={}.txt".format(str(a)),"w")
                        F.write(str(n-2))
                        F.close()
                        if HSS==0:
                            w = say_offline("رکورده جدیدی با این درجه سختی کسب کردی. آفرین")
                            #playsound("./High Scores/repeating pattern game2/Record{}.mp3".format(str(a)))
                            HSS=1
                            time.sleep(w * 1.1)
                    n+=1
                else:
                    print("you lost in level {} with difficulty{}".format(str(n-2),str(a)))
                    #playsound("./GameVoice/Game over.mp3")
                    w = say_offline("با عرض پوزش. شما باختید")
                    print("======================================")
                    print(mylist)
                    print("======================================")
                    time.sleep(w * 1.1)
                    break
                    gg=1
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("دنباله اعداد %m.difficulty ",defaults=["سطح 2"])
    def number_series(self,difficulty):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            a=0
            repeated=[]
            answers=[]
            erfan=[]
            the_path = {
                "سطح 1":"./facts-numbers-riddles/numbers1.xls",
                "سطح 2":"./facts-numbers-riddles/numbers2.xls",
                "سطح 3":"./facts-numbers-riddles/numbers3.xls",

            }[difficulty]

            
            nn=0
            while nn==0:
                nn=1

                loc = (the_path)

                the_Flist=[]

                wb = xlrd.open_workbook(loc) 
                sheet = wb.sheet_by_index(0)


                for i in range(sheet.nrows):
                    the_Flist.append([sheet.cell_value(i, 0),sheet.cell_value(i, 1),sheet.cell_value(i, 2)])

                a=0

                if sheet.cell_value(0,2)==sheet.cell_value(sheet.nrows - 2,2):
                    a=0
                    if type(the_Flist[0][2]==type(1.23)):
                        the_Flist[0][2]+=1
                    else:
                        temp=float(the_Flist[0][2])
                        temp+=1
                        the_Flist[0][2]=temp
                        
                else:
                    for i in range(sheet.nrows-1):
                        if sheet.cell_value(i,2) == sheet.cell_value(sheet.nrows - 2,2):
                            a=i
                            if type(the_Flist[i][2])==type(1.23):
                                the_Flist[i][2]+=1
                            else:
                                temp=float(the_Flist[i][2])
                                temp+=1
                                the_Flist[i][2]=temp                
                            break

                print(sheet.cell_value(a,0))
                numbersss=sheet.cell_value(a,0)
                print(sheet.cell_value(a,1))
                javab=sheet.cell_value(a,1)


                wbk = xlwt.Workbook()
                sheet = wbk.add_sheet('python')
                i=0

                while i<len(the_Flist):
                    sheet.write(i,0,the_Flist[i][0])
                    sheet.write(i,1,the_Flist[i][1])
                    sheet.write(i,2,the_Flist[i][2])
                    
                    i+=1
                wbk.save(the_path)

                print('reading the numbers, pls listen carefully!')
                #playsound("./GameVoice/numbers comming!.mp3")
                w = say_offline("تا ثانیه ای دیگر ، اعداد خوانده خواهند شد. دقت کنید")
                time.sleep(w * 1.1)
                #numbersss=df['A'][a]
                say_offline(numbersss)


                window = tkinter.Tk()
                window.title("Roobin")
                window.geometry('240x170')
                window.configure(bg='red')
                window.attributes("-topmost", True)
                window.iconbitmap('.\photo6019163393241493720__1___4__rCb_icon.ico')
                e = tkinter.Entry(window,width=35,borderwidth=5)
                e.grid(row=0, column=0, columnspan=1, padx=10, pady=10)
                e.insert(0, "Enter Your Answer: ")
                def clear(event):
                    e.delete(0, tkinter.END)

                e.bind("<Button-1>", clear)


                def button_done():
                    answers.append(e.get())
                    window.destroy()

                myButton_done = tkinter.Button(window, text="Done!",borderwidth=5,font='boldfont',padx=80,pady=40 ,command=button_done,fg="#1227D3",bg="#209139")

                myButton_done.grid(row=1,column=0,columnspan=2)
                window.mainloop()

                #print(answers[-1])
                #print(df['B'][a])
                if int(answers[-1]) == int(javab):
                    #playsound("./GameVoice/True answer.mp3")
                    say_offline("آفرین جوابه شما درست بود")

                else:
                    #playsound("./GameVoice/wrong answer(numbers).mp3")
                    say_offline("جوابه شما اشتباه بود. بیشتر دقت کن")
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("آیا میدانستید؟")
    def amazing_facts(self):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            the_path="./facts-numbers-riddles/facts.xls"

            loc = (the_path)

            the_Flist=[]

            wb = xlrd.open_workbook(loc) 
            sheet = wb.sheet_by_index(0)


            for i in range(sheet.nrows):
                the_Flist.append([sheet.cell_value(i, 0),sheet.cell_value(i, 1)])

            a=0

            if sheet.cell_value(0,1)==sheet.cell_value(sheet.nrows - 2,1):
                a=0
                if type(the_Flist[0][1]==type(1.23)):
                    the_Flist[0][1]+=1
                else:
                    temp=float(the_Flist[0][1])
                    temp+=1
                    the_Flist[0][1]=temp
                    
            else:
                for i in range(sheet.nrows-1):
                    if sheet.cell_value(i,1) == sheet.cell_value(sheet.nrows - 2,1):
                        a=i
                        if type(the_Flist[i][1])==type(1.23):
                            the_Flist[i][1]+=1
                        else:
                            temp=float(the_Flist[i][1])
                            temp+=1
                            the_Flist[i][1]=temp                
                        break

            print(sheet.cell_value(a,0))
            javab=sheet.cell_value(a,0)

            wbk = xlwt.Workbook()
            sheet = wbk.add_sheet('python')
            i=0

            while i<len(the_Flist):
                sheet.write(i,0,the_Flist[i][0])
                sheet.write(i,1,the_Flist[i][1])
                
                i+=1
            wbk.save(the_path)

            w = say_offline(javab)
            time.sleep(w * 1.1)
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")


# --------------------------------------------------

#------------------------------------------------------------

    @command("توضیحات %m.guide", defaults=["جست و جو در ویکی پدیا"])
    def arrow_explanation(self,guide):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            little_mother = {
                "جست و جو در ویکی پدیا":4,
                "چیستان":3,
                "بازی جهت ها":2,
                "الگوها آفلاین":1,
                "دنباله اعداد":0
            }[guide]

            if little_mother==0:
                w = say_offline("در این بازی دنباله ای از اعداد با الگوی خاصی به شما داده می شود")
                time.sleep(w * 1.1)
                w = say_offline("وظیفه ی شما پیدا کردنه آن الگو و حدسه عدده بعد می باشد. آن عدد را در پنجره ای که برایتان باز می شود وارد کنید")
                time.sleep(w * 1.1)
            elif little_mother==1:
                guide1 = "در این بازی چشم های ربات،  به صورته رندوم چشمک میزنند. وظیفه ی شما تکرار کردنه الگوها در پنجره می باشد"
                w = say_offline(guide1)
                time.sleep(w * 1.1)
            elif little_mother==2:
                w = say_offline(
                    "در این بازی در چشم های ربات , جهت هایی به طرفه بالا , پایین , چپ و راست نمایش داده می شود.")
                time.sleep(w * 1.1)
                w = say_offline(" اگر در چشمه راسته ربات بود , برعکسه آن را ")
                time.sleep(w * 1.1)
                w = say_offline("و اگر در چشمه چپ ربات بود همان"
                            "  جهت را در پنجره ای که برایتان باز می شود , وارد نمایید.")
                time.sleep(w * 1.1)
            elif little_mother==3:
                w = say_offline("بعد از اجرایه این بازی , چیستانی از شما پرسیده می شود. سعی کنید جوابه خود را با صدای رسا اعلام کنید")
                time.sleep(w * 1.1)
            elif little_mother==4:
                w = say_offline("بعد از شنیدنه صدای بوق , کلمه ای را بگویید. من آن را در ویکی پدیا سرچ می کنم و خلاصه ای از نتیجه را برای شما می خوانم")
                time.sleep(w * 1.1)

            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("انتخاب داستان %m.story ", defaults=["قلعه حیوانات 1"])
    def story_telling(self, story):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass
        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            a = {
                "دماغ": "./story/127-hamechiz-darbareye-damagh.mp3",
                "عینکم": "./story/einakam65519.mp3",
                "یکی زیر یکی رو": "./story/قصه-صوتی-کودکانه-یکی-زیر-یکی-رو.mp3",
                "پسری در طبل": "./story/قصه-صوتی-کودکانه-پسری-در-طبل.mp3",
                "شازده کوچولو 1": "./story/Shazdeh.Koochooloo.Part 1.mp3",
                "شازده کوچولو 2": "./story/Shazdeh.Koochooloo.Part 2.mp3",
                "قلعه حیوانات 1": "./story/A-fasl-1.mp3",
                "قلعه حیوانات 2": "./story/B-fasl-2.mp3",
                "قلعه حیوانات 3": "./story/C-fasl-3.mp3",
                "آدم برفی": "./story/آدم برفی خندان.mp3",
                "لباس پادشاه": "./story/Lebase Jadide Padeshah Audio.mp3",
                "پسرک بند انگشتی": "./story/pesarak.mp3",
                "سیندرلا": "./story/Cinderella.mp3",
                "گالیور": "./story/galiver.mp3",
                "حاکم جوان": "./story/hakem javan.mp3",
                "گربه چکمه پوش": "./story/gorbe chakme poosh.mp3",
                "جک و لوبیای سحرآمیز": "./story/jack.mp3",

            }[story]
            '''freeze_support()
            self.p = Process(target=playsound, args=(a,))
            self.p.start()
            self.p.terminate()'''
            playsound(a)
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("موتور %s را به %s درجه بچرخان")
    def move_motor(self, motor, angle):
        print("move {motor} by {angle} degrees!".format(motor=motor, angle=angle))
        print("*" * 10)
        print(int(motor),int(angle))
        print("*" * 10)
        RoobinControl.move(int(motor),int(angle),10)
        print("...")

    @command(" تغییر چشم %m.eyes_side_list  به %m.eyes_list",defaults=['دایره ای', "چپ"])
    def change_eye(self, eyes_side_list, eyes_list):
    # Changes eyes form
        eye_state = {
            'دایره ای':4,
            'لوزی':3,
            'مربعی':2,
            'مثلثی': 1,
        }[eyes_list]

        eye_side = {
            'راست':2,
            'چپ': 1,
        }[eyes_side_list]

        print(f"Eye {eye_side} state changed to {eye_state}")
        print("*" * 10)
        print("*" * 10)
        RoobinControl.change_eye_command(eye_state, eye_side)

    @command(" تغییر فرم دهان به فرم %m.mouth_list" , defaults=['روبین'])
    def change_mouth(self, mouth_list):
        # Changes mouth form
        mouth_state = {
            'روبین':1,
            'غنچه':2,
        }[mouth_list]

        print(f"Mouth state changed to {mouth_state}")
        print("*" * 10)
        print("*" * 10)
        RoobinControl.change_mouth_command(mouth_state)

    @command("چشمک بزن")
    def roobinBlink(self):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True
            # ========================FUNCTION BODY COMES HERE============================
            print("Blinking..")
            RoobinControl.eye("both", "blink")
            print("Blinked..")
            # ============================================================================
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("به اطراف نگاه کن")
    def roobinLookSides(self):
        global A_PROGRAM_IS_RUNNING
        """
        CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
        """
        # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
        while A_PROGRAM_IS_RUNNING:
            pass

        if A_PROGRAM_IS_RUNNING == False:
            A_PROGRAM_IS_RUNNING = True

            print("LookingSides..")
            RoobinControl.eye("both","looksides")
            time.sleep(4.5)
            print("Looked Sides.")
            A_PROGRAM_IS_RUNNING = False

        elif A_PROGRAM_IS_RUNNING == True:
            print("A PROGRAM IS RUNNING !!")

    @command("به روبرو نگاه کن")
    def roobinNeutral(self):
        print("Being Neutral")
        RoobinControl.eye("both","neutral")
        print("Neutralled :)")



descriptor = Descriptor(
    name = "Roobin blocks",
    port = 1234,
    blocks = get_decorated_blocks_from_class(Roobin),
    menus= dict(
        story = ["دماغ" , "عینکم" , "یکی زیر یکی رو","پسری در طبل","لباس پادشاه","قلعه حیوانات 1","قلعه حیوانات 2","قلعه حیوانات 3","شازده کوچولو 1","شازده کوچولو 2","پسرک بند انگشتی","آدم برفی","سیندرلا","گالیور","حاکم جوان","گربه چکمه پوش","جک و لوبیای سحرآمیز"],
        difficulty = ["سطح 1","سطح 2","سطح 3"],
        pattern_game_difficulty = ["آسان","متوسط","سخت","غیر ممکن"],
        speak_please = ["روش یک(آنلاین)","روش دو"],
        eyes_list = ["مربعی" ,"دایره ای" ,"لوزی","مثلثی"],
        eyes_side_list = ["راست","چپ"],
        mouth_list = ["غنچه","روبین"],
        guide=["جست و جو در ویکی پدیا","چیستان","بازی جهت ها","الگوها آفلاین","دنباله اعداد"],
        lang_list = ["en", "fa"]
    ),
)

extension = Extension(Roobin, descriptor)


if __name__ == "__main__":

    delete_all_voices()
    t1_s2e = threading.Thread(target=save_generated_s2e) 
    t2_server = threading.Thread(target=server_run_forever_func)

    t1_s2e.start() 
    t2_server.start()  
    t1_s2e.join() 
    t2_server.join() 