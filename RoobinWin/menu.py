from tkinter import *
from PIL import Image, ImageTk
from utils import *

root=Tk()

root.title('Roobin')

root.attributes("-topmost", True)
root.iconbitmap("photo6019163393241493720__1___4__rCb_icon.ico")


m = sr.Microphone()
r = sr.Recognizer()

A_PROGRAM_IS_RUNNING = False

root.resizable(0,0)

lefti = ImageTk.PhotoImage(file=(".\\arrow keys\\download.jpg"))
boti = ImageTk.PhotoImage(file=(".\\arrow keys\\download(1).jpg"))
righti = ImageTk.PhotoImage(file=(".\\arrow keys\\download(2).jpg"))
topi = ImageTk.PhotoImage(file=(".\\arrow keys\\download(3).jpg"))

myimage1 = ImageTk.PhotoImage(Image.open(".\\images\\Webp.net-resizeimage(final).png"))

the_label = Label(image=myimage1)
the_label.grid(row=0,column=0,columnspan=2)
##################################################################################################################

BACKGROUND_COLOR = "#1f0d4a"

frame = LabelFrame(root,padx=10,pady=10,background=BACKGROUND_COLOR)
# making inside bigger(padx and pady)

frame.grid(row=1,column=0,padx=1,pady=1,sticky="we")
# making outside bigger(padx and pady)

F1myimage1 = ImageTk.PhotoImage(Image.open(".\\images\\lamp.png"))

the_label = Label(frame,image=F1myimage1,padx=20,border=0)
the_label.grid(row=0,column=6,sticky='NE')
#the_label.pack(side='top')

mylabel=Label(frame, text="",font='boldfont',fg="white",bg=BACKGROUND_COLOR)
mylabel.grid(row=1,column=2)


#mylabel=Label(frame, text="داستان ها",padx=10,pady=10,font='boldfont',fg="white",bg="#271c42")
#mylabel.grid(row=1,column=1)

mylabel=Label(frame, text="آيا مي دانستيد؟",pady=10,font='boldfont',fg="white",bg=BACKGROUND_COLOR)
mylabel.grid(row=2,column=1)

facts_image = ImageTk.PhotoImage(file = ".\\images\\aya midanestid.png")

stories_image = ImageTk.PhotoImage(file = ".\\images\\dastan ha.png")

def fact_def():
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

story = ["دماغ" , "عینکم" , "یکی زیر یکی رو","پسری در طبل","لباس پادشاه","قلعه حیوانات 1","قلعه حیوانات 2","قلعه حیوانات 3","شازده کوچولو 1","شازده کوچولو 2","پسرک بند انگشتی","آدم برفی","سیندرلا","گالیور","حاکم جوان","گربه چکمه پوش","جک و لوبیای سحرآمیز"]

clicked = StringVar()
clicked.set("داستان ها")
#,image=stories_image,border=0,bg="#271c42"
b0 = OptionMenu(frame,clicked,*story)
b0.config(bg="#271c42",fg="white",width=15)
b0.grid(row=1,column=1)

def playS():
    global A_PROGRAM_IS_RUNNING
    """
    CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
    """
    # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
    while A_PROGRAM_IS_RUNNING:
        pass
    if A_PROGRAM_IS_RUNNING == False:
        A_PROGRAM_IS_RUNNING = True


        story = ["دماغ" , "عینکم" , "یکی زیر یکی رو","پسری در طبل","لباس پادشاه","قلعه حیوانات 1","قلعه حیوانات 2","قلعه حیوانات 3","شازده کوچولو 1","شازده کوچولو 2","پسرک بند انگشتی","آدم برفی","سیندرلا","گالیور","حاکم جوان","گربه چکمه پوش","جک و لوبیای سحرآمیز"]

        if clicked.get()==story[0]:
            playsound("./story/127-hamechiz-darbareye-damagh.mp3")
        elif clicked.get()==story[1]:
            playsound("./story/einakam65519.mp3")
        elif clicked.get()==story[2]:
            playsound("./story/قصه-صوتی-کودکانه-یکی-زیر-یکی-رو.mp3")
        elif clicked.get()==story[3]:
            playsound("./story/قصه-صوتی-کودکانه-پسری-در-طبل.mp3")
        elif clicked.get()==story[4]:
            playsound("./story/Shazdeh.Koochooloo.Part 1.mp3")
        elif clicked.get()==story[5]:
            playsound("./story/Shazdeh.Koochooloo.Part 2.mp3")
        elif clicked.get()==story[6]:
            playsound("./story/A-fasl-1.mp3")
        elif clicked.get()==story[7]:
            playsound("./story/B-fasl-2.mp3")
        elif clicked.get()==story[8]:
            playsound("./story/C-fasl-3.mp3")
        elif clicked.get()==story[9]:
            playsound("./story/آدم برفی خندان.mp3")
        elif clicked.get()==story[10]:
            playsound("./story/Lebase Jadide Padeshah Audio.mp3")
        elif clicked.get()==story[11]:
            playsound("./story/pesarak.mp3")
        elif clicked.get()==story[12]:
            playsound("./story/Cinderella.mp3")
        elif clicked.get()==story[13]:
            playsound("./story/galiver.mp3")
        elif clicked.get()==story[14]:
            playsound("./story/hakem javan.mp3")
        elif clicked.get()==story[15]:
            playsound("./story/gorbe chakme poosh.mp3")
        elif clicked.get()==story[16]:
            playsound("./story/jack.mp3")
        else:
            w = say_offline("لطفا يک داستان انتخاب کنيد")
            time.sleep(w * 1.1)
        #root.destroy()
        A_PROGRAM_IS_RUNNING = False
        
    elif A_PROGRAM_IS_RUNNING == True:
        print("A PROGRAM IS RUNNING !!")

b= Button(frame, text="Click N1",image=stories_image,border=0,bg="#271c42",command=playS)
b.grid(row=1,column=0)

b1= Button(frame, text="Click N2",image=facts_image,border=0,bg="#271c42",command=fact_def)
b1.grid(row=2,column=0)
####################################################################################################################
#frame2 = LabelFrame(root,padx=60,text="بازي ها",pady=24,background='#aaaec6')
frame2 = LabelFrame(root,padx=5,pady=13,background='#271c42')

frame2.grid(row=2,column=0,padx=1,pady=1,sticky="we")

Fmyimage1 = ImageTk.PhotoImage(Image.open(".\\images\\game.png"))

the_label = Label(frame2,image=Fmyimage1,padx=20,border=0)
the_label.grid(row=0,column=6,sticky='E')



mylabel=Label(frame2, text="",pady=13,font='boldfont',fg="black",bg="#271c42")
mylabel.grid(row=1,column=2)

#mylabel=Label(frame2, text="",padx=8,font='boldfont',fg="black",bg="#271c42")
#mylabel.grid(row=1,column=3)

mylabel=Label(frame2, text="",padx=4,font='boldfont',fg="black",bg="#271c42")
mylabel.grid(row=1,column=4)

mylabel=Label(frame2, text="",pady=13,font='boldfont',fg="black",bg="#271c42")
mylabel.grid(row=2,column=3)

mylabel=Label(frame2, text="",pady=13,font='boldfont',fg="black",bg="#271c42")
mylabel.grid(row=3,column=4)


def chEstan():
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
        



mylabel=Label(frame2, text="چيستان!",font='boldfont',fg="white",bg="#271c42")
mylabel.grid(row=1,column=1)

#mylabel=Label(frame2, text="بازي جهت ها",padx=5,pady=15,font='boldfont',fg="white",bg="#271c42")
#mylabel.grid(row=2,column=1)

#mylabel=Label(frame2, text="الگوها",pady=15,font='boldfont',fg="white",bg="#271c42")
#mylabel.grid(row=3,column=1)

#mylabel=Label(frame2, text="دنباله اعداد",pady=6,font='boldfont',fg="white",bg="#271c42")
#mylabel.grid(row=4,column=1)

arrow_image = ImageTk.PhotoImage(file = ".\\images\\Webp.net-resizeimage(a).png")

cheestan_image = ImageTk.PhotoImage(file = ".\\images\\Webp.net-resizeimage(2).png")

pattern_image = ImageTk.PhotoImage(file = ".\\images\\Webp.net-resizeimage(b).png")

numbers_image = ImageTk.PhotoImage(file = ".\\images\\numbers.png")

pattern_game_difficulty = ["آسان","متوسط","سخت","غیر ممکن"]

def playAG():
    global A_PROGRAM_IS_RUNNING
    """
    CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
    """
    # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
    while A_PROGRAM_IS_RUNNING:
        pass

    if A_PROGRAM_IS_RUNNING == False:
        A_PROGRAM_IS_RUNNING = True
        pattern_game_difficulty = ["آسان","متوسط","سخت","غیر ممکن"]

        game_difficulty=0

        if clicked1.get()==pattern_game_difficulty[0]:
            game_difficulty=4
        elif clicked1.get()==pattern_game_difficulty[1]:
            game_difficulty=3
        elif clicked1.get()==pattern_game_difficulty[2]:
            game_difficulty=2
        elif clicked1.get()==pattern_game_difficulty[3]:
            game_difficulty=1
        
        a=(4-game_difficulty)+1
        
        try:
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
                time.sleep(w * 1.1)
                #roobin must show the score from "./High Scores/repeating pattern game2/GD={}.txt".format(a)
                print("your high score is in this game difficulty is {}".format(str(High_Score)))

            
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
                window1 = Tk()
                window1.title("ROOBIN")
                window1.attributes("-topmost", True)
                window1.iconbitmap('.\photo6019163393241493720__1___4__rCb_icon.ico')
                window1.config(bg="black")

                def button_click_left():
                    mylabel=Label(window1,text="left ")
                    result.append(("0","6"))
                    window1.quit()
                    window1.destroy()

                def button_click_right():
                    mylabel=Label(window1,text="right")
                    result.append(("2","4"))
                    window1.quit()
                    window1.destroy()

                def button_click_top():
                    mylabel=Label(window1,text="right")
                    result.append(("1","7"))
                    window1.quit()
                    window1.destroy()

                def button_click_bot():
                    mylabel=Label(window1,text="right")
                    result.append(("3","5"))
                    window1.quit()
                    window1.destroy()


                #there is a problem with adding image to buttons
                myButton_left = Button(window1, text="left",font='boldfont',padx=28,pady=40, command=button_click_left, fg="black", bg="#fc0394")
                myButton_right = Button(window1, text="right",font='boldfont',padx=26,pady=40, command=button_click_right, fg="black", bg="#EF1839")
                myButton_bot = Button(window1, text="bot",font='boldfont',padx=26,pady=40 ,command=button_click_bot,fg="black",bg="#209139")
                myButton_top = Button(window1, text="top",font = 'boldfont',padx = 27,pady=40,command = button_click_top, fg ="black" , bg = "yellow")
                
                myButton_left.grid(row=1,column=0)
                myButton_right.grid(row=1,column=2)
                myButton_bot.grid(row=1,column=1)
                myButton_top.grid(row=0,column=1)

                window1.mainloop()
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
        except:
            say_offline("لطفا درجه سختي را انتخاب کنيد")
        A_PROGRAM_IS_RUNNING = False

    elif A_PROGRAM_IS_RUNNING == True:
        print("A PROGRAM IS RUNNING !!")    

clicked1=StringVar()
clicked1.set("درجه سختي جهت ها")

d0=OptionMenu(frame2,clicked1,*pattern_game_difficulty)
d0.config(bg="#271c42",fg="white",width=14)
d0.grid(row=2,column=1)


def patternn():
    global A_PROGRAM_IS_RUNNING
    """
    CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
    """
    # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
    while A_PROGRAM_IS_RUNNING:
        pass

    if A_PROGRAM_IS_RUNNING == False:
        A_PROGRAM_IS_RUNNING = True
        pattern_game_difficulty = ["آسان","متوسط","سخت","غیر ممکن"],

        if clickk.get()==optionss[0]:
            game_difficulty=4
            gg=0
        elif clickk.get()==optionss[1]:
            game_difficulty=3
            gg=0
        elif clickk.get()==optionss[2]:
            game_difficulty=2
            gg=0
        elif clickk.get()==optionss[3]:
            game_difficulty=1
            gg=0
        else:
            w = say_offline("لطفا درجه سختي را انتخاب کنيد")
            time.sleep(w * 1.1)
            gg=1
            
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

            window = Tk()
            window.title("roobin")
            window.attributes("-topmost", True)
            window.iconbitmap('.\photo6019163393241493720__1___4__rCb_icon.ico')

            def button_click_left():
                mylabel=tkinter.Label(window,text="left ")
                result.append("left")

            def button_click_right():
                mylabel=tkinter.Label(window,text="right")
                result.append("right")

            def button_done():
                window.quit()
                window.destroy()


            myButton_left = Button(window, text="<- left",font='boldfont',padx=28,pady=40, command=button_click_left, fg="gray", bg="#FFDA33")
            myButton_right = Button(window, text="right ->",font='boldfont',padx=26,pady=40, command=button_click_right, fg="gray", bg="#EF1839")
            myButton_done = Button(window, text="Done!",font='boldfont',padx=80,pady=40 ,command=button_done,fg="gray",bg="#209139")

            myButton_left.grid(row=0,column=0)
            myButton_right.grid(row=0,column=1)
            myButton_done.grid(row=1,column=0,columnspan=2)
            window.mainloop()
            print(result)
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


optionss = ["آسان","متوسط","سخت","غیر ممکن"]


clickk=StringVar()
clickk.set("درجه سختي الگوها")

dropp = OptionMenu(frame2,clickk,*optionss)
dropp.config(bg="#271c42",fg="white",width=14)
dropp.grid(row=3,column=1)


def fnum():
    global A_PROGRAM_IS_RUNNING
    """
    CHECKING THE MUTEX FOR NOT RUNNING SIMULTANEOUSLY 
    """
    # FOR RUNNING BLOCKS SEQUENTIALLY - IF A COMMAND REACHES HERE , IT HAS TO WAIT FOR THE MUTEX(BLOCK) TO BE FREED.
    while A_PROGRAM_IS_RUNNING:
        pass

    if A_PROGRAM_IS_RUNNING == False:
        A_PROGRAM_IS_RUNNING = True
        fucktard = ["سطح 1","سطح 2","سطح 3"]

        a=0
        repeated=[]
        answers=[]
        erfan=[]
        if flick.get()==fucktard[0]:
            the_path="./facts-numbers-riddles/numbers1.xls"
            nn=0
        elif flick.get()==fucktard[1]:
            the_path="./facts-numbers-riddles/numbers2.xls"
            nn=0
        elif flick.get()==fucktard[2]:
            the_path="./facts-numbers-riddles/numbers3.xls"
            nn=0
        else:
            w = say_offline("لطفا درجه سختي را اتخاب کنيد")
            nn=1

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
                window.quit()
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
    


fucktard = ["سطح 1","سطح 2","سطح 3"]

flick = StringVar()
flick.set("درجه سختي دنباله ها")

frop = OptionMenu(frame2,flick,*fucktard)
frop.config(bg="#271c42",fg="white",width=14)
frop.grid(row=4,column=1)


b2= Button(frame2, text="Click N1",image=cheestan_image,border=0,bg="#271c42",command=chEstan)
b2.grid(row=1,column=0)

b3= Button(frame2, text="Click N2",image=arrow_image,border=0,bg="#271c42",command=playAG)
b3.grid(row=2,column=0)

b3_2 = Button(frame2, text="Click N3",image=pattern_image,border=0,bg="#271c42",command=patternn)
b3_2.grid(row=3,column=0)

b3_8 = Button(frame2, text="Click N4",image=numbers_image,border=0,bg="#271c42",command=fnum)
b3_8.grid(row=4,column=0)
################################################################################################################################
frame3 = LabelFrame(root,padx=35,pady=20,background='#271c42')

frame3.grid(row=1,column=1,padx=1,pady=1,sticky='nwes')

mylabel=Label(frame3, text="",padx=20,font='boldfont',fg="black",bg="#271c42")
mylabel.grid(row=1,column=0)

mylabel=Label(frame3, text="جست و جو در ويکي پديا",font='boldfont',pady=10,fg="white",bg="#271c42")
mylabel.grid(row=1,column=1)

def searching():
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

search_image = ImageTk.PhotoImage(file = ".\\images\\wikipedia.png")

b4= Button(frame3, text="Click N1",image=search_image,border=0,bg="#271c42",command=searching)
b4.grid(row=0,column=1)
###############################################################################################################################
frame4 = LabelFrame(root,padx=60,pady=20,background='#271c42')

frame4.grid(row=2,column=1,padx=1,pady=1,sticky='nwe')

mylabel=Label(frame4, text="اجراي نرم افزار روبين",font='boldfont',pady=10,fg="white",bg="#271c42")
mylabel.grid(row=1,column=0)

def run_it_pls():
    os.system("start RS_runner_hide.vbs")
    root.destroy()
    
scrach_image = ImageTk.PhotoImage(file = ".\\images\\Roobin.png")

b5 = Button(frame4,text="Roobin",image = scrach_image,border=0,bg="#271c42",command=run_it_pls)
b5.grid(row=0,column=0)
root.mainloop()