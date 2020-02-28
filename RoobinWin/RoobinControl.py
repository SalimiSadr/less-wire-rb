   
#!/usr/bin/env python3
import os
import re
import sys
import json
import wave
import time
import psutil
import pigpio
import serial
import pyaudio
import logging
import subprocess
import traceback
import threading
import subprocess
from lxml import etree
from subprocess import call
import serial.tools.list_ports
from os import path,getcwd,system
from future.backports.http.client import BadStatusLine
from SimpleWebSocketServer import SimpleWebSocketServer,WebSocket


# define constants for motors
HEADNOD = 6
HEADTURN = 1
EYETURN = 2
LIDBLINK = 3
TOPLIP = 4
BOTTOMLIP = 5
EYETILT = 0


FORMAT = pyaudio.paInt16
RATE = 44100

# array to hold 
sensors = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]

# define a module level variable for the serial port
port=""
# define library version
version ="2.85"
global writing, voice, synthesizer
# flag to stop writing when writing for threading
writing = False
# global to set the params to speech synthesizer which control the voice
voice = ""
# Global flag to set synthesizer, default is festival, espeak also supported.
# If it's not festival then it needs to support -w parameter to write to file e.g. espeak or espeak-NG
synthesizer = "festival"

ser = None

# Function to check if a number is a digit including negative numbers
def is_digit(n):
    try:
        int(n)
        return True
    except ValueError:
        return  False
# speak depending on synthesizer

def init(portName):
    # pickup global instances of port, ser and sapi variables   
    global port,ser
    
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
    #speak (text)

    return True

# Startup Code
# xml file for motor definitions
dir = "./"
file = os.path.join(dir, 'MotorDefinitionsv21.omd')
tree = etree.parse(file)
root = tree.getroot()

# Put motor ranges into lists
motorPos = [11,11,11,11,11,11,11,11]
motorMins = [0,0,0,0,0,0,0,0]
motorMaxs = [0,0,0,0,0,0,0,0]
motorRev = [False,False,False,False,False,False,False,False]
restPos = [0,0,0,0,0,0,0,0]
isAttached = [False,False,False,False,False,False,False,False]

# For each line in motor defs file
for child in root:
    indexStr = child.get("Motor")
    index = int(indexStr)
    motorMins[index] = int(int(child.get("Min"))/1000*180)
    motorMaxs[index] = int(int(child.get("Max"))/1000*180)
    motorPos[index] = int(child.get("RestPosition"))
    restPos[index] = int(child.get("RestPosition"))

    if child.get("Reverse") == "True":
        rev = True
        motorRev[index] = rev
    else:
        rev = False
        motorRev[index] = rev
        
# initialise with any port that has Arduino in the name
init("Arduino")

# Function to move Roobin's motors. Arguments | m (motor) → int (0-6) | pos (position) → int (0-10) | spd (speed) → int (0-10) **eg move(4,3,9) or move(0,9,3)**
def move(m, pos, spd=3):
    
    # Limit values to keep then within range
    pos = limit(pos)
    spd = limit(spd)
    absPos = pos

    # Reverse the motor if necessary   
    if motorRev[m]:
        pos = 10 - pos

    # Attach motor       
    attach(m)
    
    # Ensure the lips do not crash into each other. 
    # if m == TOPLIP and pos + motorPos[BOTTOMLIP] > 10:
    #     pos = 10 - motorPos[BOTTOMLIP]

    # if m == BOTTOMLIP and pos + motorPos[TOPLIP] > 10:
    #     pos = 10 - motorPos[TOPLIP]
        
    # Convert position (0-10) to a motor position in degrees

    # Only for Jaws babe :)
    
    # absPos = int(getPos(m,pos))

    # Scale range of speed
    spd = (250/10)*spd

    # Construct message from values
    msg = "m0"+str(m)+","+str(absPos)+","+str(spd)+"\n"

    # Write message to serial port
    serwrite(msg)

    # Update motor positions list
    motorPos[m] = pos  
 
# Function to write to serial port
# The serial port write_timeout doesn't work reliably on multiple threads so this
# blocks using a global variable
def serwrite(s):
    global writing
    # wait until previous write is finished
    while (writing):
        pass
        # print ('waiting on write')

    writing = True
    print("=======================================")
    print()
    print(s.encode('latin-1'))
    print()
    print()
    print(s)
    print()
    print("=======================================")
    ser.write(s.encode('latin-1')) 
    writing = False
    
# Function to attach Roobin's motors. Argument | m (motor) int (0-6)
def attach(m):
    if isAttached[m] == False:
        # Construct message
        msg = "a0"+str(m)+"\n"

        # Write message to serial port
        serwrite(msg)

        # Update flag
        isAttached[m] = True
    
# Function to detach Roobin's motors.  Argument | m (motor) int (0-6)
def detach(m):
    msg = "d0"+str(m)+"\n"    
    serwrite(msg)
    isAttached[m] = False
    
# Function to find the scaled position of a given motor. Arguments | m (motor) → int (0-6) | pos (position) → int (0-10) | Returns a position
def getPos(m, pos):
    mRange = motorMaxs[m]-motorMins[m]
    scaledPos = (mRange/10)*pos
    return scaledPos + motorMins[m]

# Function to set a different speech synthesizer - defaults to festival
def setSynthesizer(params):
    global synthesizer
    synthesizer = params
        
# Function to limit values so they are between 0 - 10
def limit(val):
     if int(val) > 50:
       return 50
     elif int(val) < 0: 
        return 0
     else:
        return val
   
# Function to move Roobin's lips in time with speech. Arguments | phonemes → list of phonemes[] | waits → list of waits[]
def moveSpeech(phonemes, times):
    startTime = time.time()
    timeNow = 0
    totalTime = times[len(times)-1]
    currentX = -1
    while timeNow < totalTime:     
        timeNow = time.time() - startTime
        for x in range (0,len(times)):
            if timeNow > times[x] and x > currentX:                
                posTop = phonememapTop(phonemes[x])
                posBottom = phonememapBottom(phonemes[x])
                move(TOPLIP,posTop,10)
                move(BOTTOMLIP,posBottom,10)
                currentX = x
    move(TOPLIP,5)
    move(BOTTOMLIP,5)
    
# Function to move Roobin's lips in time with speech. Arguments | phonemes → list of phonemes[] | waits → list of waits[]
def moveSpeechFest(phonemes, times):
    startTime = time.time()
    timeNow = 0
    totalTime = times[len(times)-1]
    currentX = -1
    while timeNow < totalTime:     
        timeNow = time.time() - startTime
        for x in range (0,len(times)):
            if timeNow > times[x] and x > currentX:                
                posTop = phonememapTopFest(phonemes[x])
                posBottom = phonememapBottomFest(phonemes[x])
                move(TOPLIP,posTop,10)
                move(BOTTOMLIP,posBottom,10)
                currentX = x
    move(TOPLIP,5)
    move(BOTTOMLIP,5)

# Function mapping phonemes to top lip positions. Argument | val → phoneme | returns a position as int
def phonememapTopFest(val):
    return {
        'p': 5,
        'b': 5,
        'm': 5,
        'ae': 7,
        'ax': 7,
        'ah': 7,
        'aw': 10,
        'aa': 10,
        'ao': 10,
        'ow': 10,
        'ey': 7,
        'eh': 7,
        'uh': 7,
        'ay': 7,
        'h': 7,
        'er': 8,
        'r': 8,
        'l': 8,
        'y': 6,
        'iy': 6,
        'ih': 6,
        'ix':6,
        'w': 6,
        'uw': 6,
        'oy': 6,
        's': 5,
        'z': 5,
        'sh': 5,
        'ch': 5,
        'jh': 5,
        'zh': 5,
        'th': 5,
        'dh': 5,
        'd': 5,
        't': 5,
        'n': 5,
        'k': 5,
        'g': 5,
        'ng': 5,
        'f': 6,
        'v': 6
}.get(val, 5)

# Function mapping phonemes to lip positions. Argument | val → phoneme | returns a position as int
def phonememapBottomFest(val):
    return {
        'p': 5,
        'b': 5,
        'm': 5,
        'ae': 8,
        'ax': 8,
        'ah': 8,
        'aw': 5,
        'aa': 10,
        'ao': 10,
        'ow': 10,
        'ey': 7,
        'eh': 7,
        'uh': 7,
        'ay': 7,
        'h': 7,
        'er': 8,
        'r': 8,
        'l': 8,
        'y': 6,
        'iy': 6,
        'ih': 6,
        'ix':6,
        'w': 6,
        'uw': 6,
        'oy': 6,
        's': 6,
        'z': 6,
        'sh': 6,
        'ch': 6,
        'jh': 6,
        'zh': 6,
        'th': 6,
        'dh': 6,
        'd': 6,
        't': 6,
        'n': 6,
        'k': 6,
        'g': 6,
        'ng': 6,
        'f': 5,
        'v': 5
}.get(val,5)  
          
# Function mapping phonemes to top lip positions.
def phonememapTop(val):
        
    return 5 + val / 2;

# Function mapping phonemes to top lip positions.
# Bottom lip is 2/3 the movement of top lip
def phonememapBottom(val):
    return 5 + val / 3;

# Wait function
def wait(seconds):
    time.sleep(float(seconds))
    return

# Close the connection.
def close():       
    for x in range(0, len(motorMins)-1):
        detach(x)   

# Reset Roobin back to start position
def reset():
    #eyeColour(0,0,0)
    for x in range(0,len(restPos)-1):
        move(x,restPos[x]) 

# Attach all motors.
def adjust():
    for i in range(7):
        move(i, restPos[i], 2)
        wait(1)

def adjust_again():
    for i in range(7):
        move(i, 2, 2)
        wait(1)

def eye (side="both", statement="neutral"):
    spd = 0
    # stateSel = {"blink_left":1 , "blink": 2 , "blink_right" : 3, "look_left": 4 , "look_right" : 5 , "neutral" : 6 }
    stateSel = {"looksides":1 , "blink": 2 , "neutral" : 3 }
    sideSel =  {"right":1 , "left" : 2 , "both" : 3}
	# right --> 01 # left  --> 10 # both  --> 11
    msg = "q0"+str(stateSel[statement])+","+str(sideSel[side])+","+str(spd)+"\n"
	# Write message to serial port
    serwrite(msg)








if __name__ == "__main__":

    adjust()
    # wait(5)
    reset()

    try:
        print("here")
        # move(5,1,10)
        # move(5,5,10)
        # move(5,10,3)
        # wait(2)
    except KeyboardInterrupt:
        sys.exit(0)

    

