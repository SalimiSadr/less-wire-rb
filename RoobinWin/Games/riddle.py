from utils import *

m = sr.Microphone()
r = sr.Recognizer()

A_PROGRAM_IS_RUNNING = False

def riddle_game():

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
        file_path = "voice_commands/Gamequery.wav"
        the_path="facts-numbers-riddles/ForGodSake.xls"
        cwd = os.getcwd()
        the_path = dirname(cwd) + "\\" + the_path

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

            # try:
            url='http://www.google.com/'
            requests.get(url, timeout=5)
            print('befor listening!')
            listen_and_record(file_path)
            print('after listneing!!!')
            speech_to_text_text = speech_to_text(file_path)
            print("speech_to_text")
            print(speech_to_text_text)
            # except:
            #     window = tkinter.Tk()
            #     window.title("Roobin")
            #     window.geometry('240x170')
            #     window.configure(bg='red')
            #     window.attributes("-topmost", True)
            #     window.iconbitmap('./static/logo.ico')
            #     e = tkinter.Entry(window,width=35,borderwidth=5)
            #     e.grid(row=0, column=0, columnspan=1, padx=10, pady=10)
            #     e.insert(0, "Enter Your Answer: ")
            #     def clear(event):
            #         e.delete(0, tkinter.END)

            #     e.bind("<Button-1>", clear)


            #     def button_done():
            #         erfan.append(e.get())
            #         window.destroy()

            #     myButton_done = tkinter.Button(window, text="Done!",borderwidth=5,font='boldfont',padx=80,pady=40 ,command=button_done,fg="#1227D3",bg="#209139")

            #     myButton_done.grid(row=1,column=0,columnspan=2)
            #     window.mainloop()
            #     speech_to_text_text=str(erfan[-1])


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

if __name__ == "__main__":
    riddle_game()