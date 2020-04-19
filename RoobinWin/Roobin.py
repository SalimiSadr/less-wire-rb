# coding=utf-8
from __future__ import unicode_literals
import sys
import os
import time
import wave
import random
import pyaudio
import tkinter
import requests
import threading
import xlsxwriter
import subprocess
import pandas as pd
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
from future.backports.http.client import BadStatusLine


m = sr.Microphone()
r = sr.Recognizer()


FORMAT = pyaudio.paInt16
RATE = 44100
VOICES_PATH = "./robot_voices/"
SPEAKING_SPEED = 155
SPEAKING_PITCH = 100
NAME_COUNTER = 0

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

def playthesound(vcname):
    playsound(vcname)
    # os.remove(vcname)

def text_to_speech_espeak(text):
    global NAME_COUNTER
    NAME_COUNTER += 1
    rvcfilename = VOICES_PATH + "vcm" + str(NAME_COUNTER) + ".wav" 
    text_file_path='text.txt'
    F=open(text_file_path,"w", encoding="utf8")
    F.write(text)
    F.close()
    os.system(f'espeak -vmb-ir1 -p{SPEAKING_PITCH} -g13 -s{SPEAKING_SPEED} -w {rvcfilename} -f {text_file_path}')
    return rvcfilename

def say_offline(text):
    print("__In say_offline funcion__")
    vcname = text_to_speech_espeak(text)
    phonemes, times = RoobinControl.phonemes_gen(vcname)
    # Set up a thread for the speech sound synthesis, delay start by soundDelay
    # Set up a thread for the speech movement
    t2 = threading.Thread(target=RoobinControl.moveSpeechMouth, args=(phonemes,times, vcname))
    t2.start() 
    # Set up a thread for the speech sound synthesis
    t = threading.Thread(target=playthesound, args=(vcname,))      
    t.start()

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

    @command("معرفی")
    def introduce(self):
        text = "سلام ، من روبین هستم ، دوسته خوبه شما"
        say_offline(text) 

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

    @command("بگو %s")
    def text_to_speech(self, text):
        print("trying to speak!!!!")
        say(text)
        print("just said!")
    
    @command("بگو آفلاین %s")
    def begoo(self,text):
            say_offline(text)
            #os.system()

    @command("جست و جو در ویکی پدیا")
    def search_in_wikipedia(self):
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
                say_offline(result) 
                #print('yes')
            except:
                #print('no')
                say_offline(page_py.summary)
        else:
            say_offline('این صفحه وجود ندارد')

    @command("چیستان")
    def riddle_game(self):
        riddles_list=[]
        erfan=[]
        nn=0
        a=0
        #a is my index for df['C']
        file_path = "./voice_commands/Gamequery.wav"
        the_path="./facts-numbers-riddles/riddles.xlsx"
        df=pd.read_excel(the_path)
        the_list=[]
        #yes_list=['بله','بلی','آره','آری','بریم','بریم چیستان بعدی','اره','ار','آر','بعدی','برو','بر']
        while nn==0:
            nn==1
            gg=0

            
            if df['C'][0]==df['C'][len(df['C'])-1]:
                a=0
                df.loc[0,'C']+=1     
            else:
                for i in range(len(df['C'])):
                    if df['C'][i] == df['C'][len(df['C'])-1]:
                        df.loc[i,'C']+=1
                        a=i
                        break
            df.to_excel(the_path,index=False)


            the_list=df['B'][a].split(',')
            #print(the_list)
            #say(df['A'][a])
            #feel free to use online version of say function(say()) instead of say_offline()
            say_offline(df['A'][a])
            time.sleep(7)
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
                say_offline("تبریک میگم. جوابت درست بود")
                #playsound("./GameVoice/well_done.mp3")
                time.sleep(1)

            else:
                print('i dont think so')
                say_offline(".جوابه شما اشتباه بود")
                #playsound("./GameVoice/sorry.mp3")
                time.sleep(1)

            nn=1

    @command("بازی جهت ها %m.pattern_game_difficulty",defaults=['متوسط'])
    def arrow_game(self,pattern_game_difficulty):
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
            say_offline(f"بیشترین امتیازی که در این بازی کسب کرده اید ، {High_Score} بوده است.")
            #roobin must show the score from "./High Scores/repeating pattern game2/GD={}.txt".format(a)
            print("your high score is in this game difficulty is {}".format(str(High_Score)))

        time.sleep(8)
        #playsound("./GameVoice/Readdy.mp3")
        say_offline("آماده باشید")
        os.system('cls' if os.name == 'nt' else 'clear')
        time.sleep(3)

          
        mylist=[]
        result=[]
        os.system('cls' if os.name == 'nt' else 'clear')
        print("the pattern will show in 2 seconds")
        #playsound("./GameVoice/in 2 secconds.mp3")
        say_offline("الگو تا دو ثانیه دیگر نمایش داده می شود")
        time.sleep(7)
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
                RoobinControl.eye("right","rightArrow",game_difficulty)
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
            say_offline("جواب شما اشتباه بود")
            time.sleep(3)
        else:
            print("you answered soooo late")
            #playsound("./GameVoice/late.mp3")
            say_offline("خیلی دیر جواب دادی")
            time.sleep(3)

        print("you lost in level {} with difficulty{}".format(str(len(mylist)),str(a)))
        #playsound("./GameVoice/Game over.mp3")
        if new_score>High_Score:
            print("this is the highest score!")
            #playsound("./GameVoice/new_record.mp3")
            say_offline("تبریک. رکورد جدیدی با این درجه سختی کسب کردی")
            F=open("./High Scores/arrow game/GD={}.txt".format(str(a)),"w")
            F.write(str(new_score))
            F.close()
            time.sleep(1) 

    @command("الگوها آفلاین  %m.pattern_game_difficulty",defaults=['متوسط'])
    def repeating_pattern_game2(self,pattern_game_difficulty):
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
        voice2 = 'تا دو ثانیه دیگر , بازی شروع می شود'
        guide1 = "به بازی الگو ها خوشامدید. در این بازی چشم های ربات به صورت رندوم چشمک میزنند. وظیفه شما تکرار کردن الگوها می باشد"
        guide2 = "لطفا الگو را با صدای بلند و بدون توقف زیاد تکرار کنید. به این مثال توجه کنید"
        
        
        #playsound("./GameVoice/guide1.mp3")
        say_offline(guide1)
        time.sleep(7.5)


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
        time.sleep(2.5)
        #playsound("./GameVoice/Readdy.mp3")
        say_offline("آماده باشید")
        os.system('cls' if os.name == 'nt' else 'clear')
        time.sleep(3)

        gg=0
        while(gg==0):
            mylist=[]
            result=[]
            os.system('cls' if os.name == 'nt' else 'clear')
            print("the pattern will show in 2 seconds")
            #playsound("./GameVoice/in 2 secconds.mp3")
            say_offline(voice2)
            print("level{}".format(str(n-2)))
            #say('مرحله {}'.format(str(n-2)))
            time.sleep(4)

            for i in range(n):
                if random.randint(0,1)==0:
                    mylist.append("left")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - left".format(str(i+1)))
                    #blinking the left eye for game_difficulty seconds <<=======================================================
                    time.sleep(game_difficulty)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    
                else:
                    mylist.append("right")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - right".format(str(i+1)))
                    #blinking the right eye for game_difficulty seconds <<=======================================================
                    time.sleep(game_difficulty)
                    os.system('cls' if os.name == 'nt' else 'clear')

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
                say_offline("تبریک میگم. این مرحله را رد کردین")
                time.sleep(4)
                if n-2 > High_Score:
                    
                    print("this is the highest score!")
                    F=open("./High Scores/repeating pattern game2/GD={}.txt".format(str(a)),"w")
                    F.write(str(n-2))
                    F.close()
                    if HSS==0:
                        say_offline("رکورد جدیدی با این درجه سختی کسب کردی. آفرین")
                        #playsound("./High Scores/repeating pattern game2/Record{}.mp3".format(str(a)))
                        HSS=1
                        time.sleep(4)
                n+=1
            else:
                print("you lost in level {} with difficulty{}".format(str(n-2),str(a)))
                #playsound("./GameVoice/Game over.mp3")
                say_offline("با عرض پوزش. شما باختید")
                time.sleep(3)
                gg=1

    @command(" بازی الگوها %m.pattern_game_difficulty",defaults=['متوسط'])
    def repeating_pattern_game(self,pattern_game_difficulty):

        little_mother = {
            'آسان':4,
            'متوسط':3,
            'سخت':2,
            'غیر ممکن':1
        }[pattern_game_difficulty]
        game_difficulty=little_mother
        file_path = "./voice_commands/Gamequery.wav"

        n=3

        voice1 = 'متوجه نشدم. لطفا تکرار کنید'
        voice2 = 'تا دو ثانیه دیگر , بازی شروع می شود'
        guide1 = "به بازی الگو ها خوشامدید. در این بازی چشم های ربات به صورت رندوم چشمک میزنند. وظیفه شما تکرار کردن الگوها می باشد"
        guide2 = "لطفا الگو را با صدای بلند و بدون توقف زیاد تکرار کنید. به این مثال توجه کنید"


        say_offline(guide1)
        time.sleep(10)
        say_offline(guide2)
        time.sleep(7)
        playsound("./GameVoice/right-left.mp3")
        time.sleep(3)
        os.system('cls' if os.name == 'nt' else 'clear')
              
        gg=0
        while(gg==0):
            mylist=[]
            result=[]
            os.system('cls' if os.name == 'nt' else 'clear')
            print("the pattern will show in 2 seconds")
            say_offline(voice2)
            time.sleep(3)
            print("level{}".format(str(n-2)))
            say_offline('مرحله {}'.format(str(n-2)))
            time.sleep(3)

            for i in range(n):
                if random.randint(0,1)==0:
                    mylist.append("left")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - left".format(str(i+1)))
                    #blinking the left eye for game_difficulty seconds <<=======================================================
                    time.sleep(game_difficulty)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    
                else:
                    mylist.append("right")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("{} - right".format(str(i+1)))
                    #blinking the right eye for game difficulty seconds <<=======================================================
                    time.sleep(game_difficulty)
                    os.system('cls' if os.name == 'nt' else 'clear')

            
            flag=0
            while(flag==0):
                result=[]
                flag=1
                os.system('cls' if os.name == 'nt' else 'clear')
                print("please repeat the pattern")
                #say("لطفا الگو را تکرار کنید")
                
                print('befor listening!')
                listen_and_record(file_path)
                print('after listneing!!!')
                speech_to_text_text = speech_to_text(file_path)
                print("speech_to_text")
                print(speech_to_text_text)
                result0=speech_to_text_text.split(' ')
                print(result0)
                
                for i in range(len(result0)):
                    if 'ر' in result0[i]:
                        print('right')
                        result.append('right')
                    elif 'چ' in result0[i] or 'ش' in result0[i]:
                        print('left')
                        result.append('left')
                    else:
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print('roobin did not undrestand what you said. please repeat again.')
                        say_offline(voice1)
                        time.sleep(3)
                        flag=0


            if result==mylist:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("you won level{}".format(str(n-2)))
                say_offline("شما مرحله {} را رد کردین".format(str(n-2)))
                time.sleep(4)
                n+=1
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("you lost in level{}".format(str(n-2)),end=' ')
                print("with difficulty{}".format(str(game_difficulty)))
                say_offline("شما در مرحله {} باختید".format(str(n-2)))
                time.sleep(2)
                gg=1

    @command("دنباله اعداد %m.difficulty ",defaults=["سطح 2"])
    def number_series(self,difficulty):

        a=0
        repeated=[]
        answers=[]
        erfan=[]
        the_path = {
            "سطح 1":"./facts-numbers-riddles/numbers1.xlsx",
            "سطح 2":"./facts-numbers-riddles/numbers2.xlsx",
            "سطح 3":"./facts-numbers-riddles/numbers3.xlsx",

        }[difficulty]
        df=pd.read_excel(the_path)
        nn=0
        while nn==0:
            nn=1
            
            if df['C'][0] == df['C'][len(df['C'])-1]:
                a=0
                df.loc[0,'C']+=1
            else:
                for i in range(len(df['C'])):
                    if df['C'][i]==df['C'][len(df['C'])-1]:
                        df.loc[i,'C']+=1
                        a=i
                        break
            df.to_excel(the_path,index=False)

            print('reading the numbers, pls listen carefully!')
            #playsound("./GameVoice/numbers comming!.mp3")
            say_offline("تا ثانیه ای دیگر ، اعداد خوانده خواهند شد. دقت کنید")
            time.sleep(5)
            numbersss=df['A'][a]
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
            if int(answers[-1]) == int(df['B'][a]):
                #playsound("./GameVoice/True answer.mp3")
                say_offline("آفرین جواب شما درست بود")

            else:
                #playsound("./GameVoice/wrong answer(numbers).mp3")
                say_offline("جواب شما اشتباه بود. بیشتر دقت کن")

    @command("آیا میدانستید؟")
    def amazing_facts(self):
        the_path="./facts-numbers-riddles/facts.xlsx"
        df=pd.read_excel(the_path)
        nn=0

        if df['B'][0] == df['B'][len(df['B'])-1]:
            a=0
            df.loc[0,'B']+=1
        else:
            for i in range(len(df['B'])):
                if df['B'][i] == df['B'][len(df['B'])-1]:
                    a=i
                    df.loc[i,'B']+=1
                    break
        df.to_excel(the_path,index=False)

        say_offline(df['A'][a])

    @command("توضیحات بازی جهت ها")
    def arrow_explanation(self):
        say_offline(
            "در این بازی در چشم های ربات , جهت هایی به طرفه بالا , پایین , چپ و راست نمایش داده می شود.")
        time.sleep(10)
        say_offline(" اگر در چشمه راست ربات بود , برعکسه آن را و اگر در چشمه چپ ربات بود همان"
            "  جهت را در پنجره ای که برایتان باز می شود , وارد نمایید.")

    @command("بازی حدس عدد")
    def play_game(self):
        number_from_client = 0
        generated_num = random.randint(1, 100)
        print("*" * 100)
        print(generated_num)
        print("*" * 100)
        win = False
        say_offline("اگه میتونی عدد من را حدس بزن")
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
                say_offline("پایین تر")
            elif number_from_client < generated_num:
                print("===============Bigger.================")
                print("==============----------------------------------------------=========================================")
                say_offline("بالاتر")
            else:
                print("===============You Won.================")
                print("==============----------------------------------------------=========================================")
                say_offline("تو بردی. تبریک")
                win = True
                break

        if not win:
            say_offline("من بردم")
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

    @command(" تغییر چشم %m.eyes_side_list  به %m.eyes_list",defaults=['دایره ای', "چپ"])
    def change_eye(self, eyes_side_list, eyes_list):
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

    @command("چشمک بزن")
    def roobinBlink(self):
        print("Blinking..")
        RoobinControl.eye("both","blink")
        print("Blinked..")

    @command("به اطراف نگاه کن")
    def roobinLookSides(self):
        print("LookingSides..")
        RoobinControl.eye("both","looksides")
        print("Looked Sides.")

    @command("به روبرو نگاه کن")
    def roobinNeutral(self):
        print("Being Neutral")
        RoobinControl.eye("both","neutral")
        print("Neutralled :)")

    @command("انتخاب داستان %m.story ",defaults=["قلعه حیوانات 1"])
    def story_telling(self, story):
        a = {
            "دماغ": "./story/127-hamechiz-darbareye-damagh.mp3",
            "عینکم": "./story/einakam65519.mp3",
            "یکی زیر یکی رو": "./story/قصه-صوتی-کودکانه-یکی-زیر-یکی-رو.mp3",
            "پسری در طبل":"./story/قصه-صوتی-کودکانه-پسری-در-طبل.mp3",
            "شازده کوچولو 1":"./story/Shazdeh.Koochooloo.Part 1.mp3",
            "شازده کوچولو 2":"./story/Shazdeh.Koochooloo.Part 2.mp3",
            "قلعه حیوانات 1":"./story/A-fasl-1.mp3",
            "قلعه حیوانات 2":"./story/B-fasl-2.mp3",
            "قلعه حیوانات 3":"./story/C-fasl-3.mp3",
            "آدم برفی":"./story/آدم برفی خندان.mp3",
            "لباس پادشاه":"./story/Lebase Jadide Padeshah Audio.mp3",
            "پسرک بند انگشتی":"./story/pesarak.mp3",
            "سیندرلا":"./story/Cinderella.mp3",
            "گالیور":"./story/galiver.mp3",
            "حاکم جوان":"./story/hakem javan.mp3",
            "گربه چکمه پوش":"./story/gorbe chakme poosh.mp3",
            "جک و لوبیای سحرآمیز":"./story/jack.mp3",

        }[story]
        print("salam")
        playsound(a)


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
        eyes_side_list = ["راست","چپ    "]
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