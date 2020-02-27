#A long time ago in a galaxy far far away, this was their way for converting python program to exe 

import os
import sys
import re
import subprocess

my_command='pip install pyinstaller'

#adding "pip install module" command to the string
def for_god_sake(a,b):
    b+=(' && pip install {}'.format(a))
    return b

#adding cd directory command to the string
def for_god_sake2(s,b):
    b+=(' && cd {}'.format(s))
    return b

#adding the pyinstaller command to the string
def for_god_sake3(d,b):
    b+=(' && pyinstaller --onefile {}'.format(d))
    return b

#os.system('cmd /c "{}"'.format())
#os.system('cmd /c "pip install"'.format())
#os.system('cmd /c "pypy"')
list_of_modules=[]
print('enter modules that your program use and they are not in the python standard library.\nplease seprate them with comma. here is an example: \nrequests,pyaudio,psutill')
string_of_modules=input()
list_of_modoles=re.split(',',string_of_modules)
#print(list_of_modoles)
#a= "pip install "%(list_of_modules[0])

for i in list_of_modoles:
    my_command=for_god_sake(i,my_command)

#modules are going to be installed
os.system(my_command)
  
my_command='dir'

print()
print()

print('enter the directory location which your file is in\nfor example-> F:\\Users\\pds\\Desktop\\less-wire-rb-master ')
#os.system('cmd /c "pip install pyinstaller"')

#location of the project is here
my_location=input()


my_command=for_god_sake2(my_location,my_command)

print()
print()

print("please enter name of the file you wanna convert to exe. example: Roobin.py")

#the main file is here
bb=input()

my_command=for_god_sake3(bb,my_command)

#the pyinstaller process is going to be done
os.system(my_command)


name1=bb[0:len(bb)-2]
trash=name1
name1+='exe'

#a.spec is trash
trash+='spec'
a=my_location+'\\dist\\{}'.format(name1)
a2=my_location+'\\dist'
a3=my_location+'\\build'
my_command='move {0} {1}'.format(a,my_location)
os.system(my_command)
my_command+='del {}'.format(a2)
os.system(my_command)
my_command='rmdir /s {}'.format(a3)
os.system(my_command)
my_command='del {}'.format(trash)
os.system(my_command)


print("the exe file has been created and it is in the same \ndirectory as the .py file... enjoy it")
print()
input("press the Enter key")