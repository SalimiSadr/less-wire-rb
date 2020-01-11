   
#!/usr/bin/env python3

"""
s2_pi.py
 Copyright (c) 2016-2018 Alan Yorinks All right reserved.
 Python Banyan is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.
 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""


###############################################################################################SAY THING.

# This is a script to help control an Ohbot Robot on a Raspberry Pi. www.ohbot.co.uk
# Requires festival or espeak to be installed

import serial
import serial.tools.list_ports
import time
import threading
import os
import sys
import wave
import subprocess
from lxml import etree
import re


# define constants for motors
HEADNOD = 0
HEADTURN = 1
EYETURN = 2
LIDBLINK = 3
TOPLIP = 4
BOTTOMLIP = 5
EYETILT = 6

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
def speak(text):

        # Remove any characters that are unsafe for a subprocess call
        safetext = re.sub(r'[^ .a-zA-Z0-9?\']+', '', text)
        bashcommand = synthesizer + ' -w ohbotspeech.wav ' + voice + ' "' + safetext + '"'
        # Execute bash command.
        subprocess.call(bashcommand,shell=True)

        
def init(portName):
    # pickup global instances of port, ser and sapi variables   
    global port,ser
    
    # Search for the Ohbot serial port 
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        # print ("p0:" + p[0])
        # print ("p1:" + p[1])
        # If port has Ohbot connected save the location
        if portName in p[1]:
            port = p[0]
            print ("Ohbot found on port:" + port)
        elif portName in p[0]:
            port = p[0]
            print ("Ohbot found on port:" + port)

    # If not found then try the first port
    if port == "":
        for p in ports:
            port = p[0]
            print ("Ohbot probably found on port:" + port)
            break
            
    if port == "":
        print ("Ohbot port " + portName + " not found")
        return False

    # Open the serial port
    ser = serial.Serial(port, 19200)

    # Set read timeout and write timeouts to blocking
    ser.timeout = None
    ser.write_timeout = None

    # Make an initial call to Festival without playing the sound to check it's all okay
    text = "Hi"
        
    # Create a bash command with the desired text. The command writes two files, a .wav with the speech audio and a .txt file containing the phonemes and the times.
    speak (text)

    return True

# Startup Code
# xml file for motor definitions
dir = os.path.dirname(os.path.abspath(__file__))
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

# Function to move Ohbot's motors. Arguments | m (motor) → int (0-6) | pos (position) → int (0-10) | spd (speed) → int (0-10) **eg move(4,3,9) or move(0,9,3)**
def move(m, pos, spd=3):
    
    # Limit values to keep then within range
    pos = limit(pos)
    spd = limit(spd)

    # Reverse the motor if necessary   
    if motorRev[m]:
        pos = 10 - pos

    # Attach motor       
    attach(m)
    
    # Ensure the lips do not crash into each other. 
    if m == TOPLIP and pos + motorPos[BOTTOMLIP] > 10:
        pos = 10 - motorPos[BOTTOMLIP]

    if m == BOTTOMLIP and pos + motorPos[TOPLIP] > 10:
        pos = 10 - motorPos[TOPLIP]
        
    # Convert position (0-10) to a motor position in degrees
    absPos = int(getPos(m,pos))

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
    ser.write(s.encode('latin-1')) 
    writing = False
    

# Function to attach Ohbot's motors. Argument | m (motor) int (0-6)
def attach(m):
    if isAttached[m] == False:
        # Construct message
        msg = "a0"+str(m)+"\n"

        # Write message to serial port
        serwrite(msg)

        # Update flag
        isAttached[m] = True
    
# Function to detach Ohbot's motors.  Argument | m (motor) int (0-6)
def detach(m):
    msg = "d0"+str(m)+"\n"    
    serwrite(msg)
    isAttached[m] = False
    
# Function to find the scaled position of a given motor. Arguments | m (motor) → int (0-6) | pos (position) → int (0-10) | Returns a position
def getPos(m, pos):
    mRange = motorMaxs[m]-motorMins[m]
    scaledPos = (mRange/10)*pos
    return scaledPos + motorMins[m]

# Function to set the voice used by the synthesiser
# params - dependent on which synthesizer is used
# for espeak use parameters e.g. -ven+f4 for a uk female voice - see http://espeak.sourceforge.net/commands.html
# This override will stay in use until it's next called
def setVoice(params):
    global voice
    voice = params

# Function to set a different speech synthesizer - defaults to festival
def setSynthesizer(params):
    global synthesizer
    synthesizer = params

# Function to make Ohbot Speak. Arguments | text String "Hello World" **eg say("Hello my name is Ohbot") or
# untilDone - wait in function until speech is complete, lipSync - move lips in time with speech, hdmiAudio - adds a delay to give hdmi channel time to activate.
# soundDelay - positive if lip movement is lagging behind sound, negative if sound is lagging behind lip movement.
def say(text, untilDone=True, lipSync=True, hdmiAudio=False, soundDelay=0):
    # init_servo_motors()
    if hdmiAudio:
        soundDelay = soundDelay - 1
    ######################


    if ("festival" in "s"):
        if hdmiAudio:
            soundDelay = soundDelay - 1
        
        safetext = re.sub(r'[^ .a-zA-Z0-9?\']+', '', text)
        
        # Create a bash command with the desired text. The command writes two files, a .wav with the speech audio and a .txt file containing the phonemes and the times. 
        bashcommand = "festival -b '(set! mytext (Utterance Text " + '"' + safetext + '"))' + "' '(utt.synth mytext)' '(utt.save.wave mytext " + '"ohbotspeech.wav")' + "' '(utt.save.segs mytext " + '"phonemes"' + ")'"

        # Execute bash command.
        subprocess.call(bashcommand,shell=True)
        
        # Open the text file containing the phonemes
        f = open("phonemes",'r')

        # Empty the lists that contain phoneme data and reset count
        phonemes = []
        times = []
        vals = []

        # Read a line to move past the first line
        line = f.readline()
        
        # While there are more lines to read.
        while line:

            # Read the line
            line = f.readline()

            # Split the line into values 
            vals = line.split()

            # If values exist add the phoneme to the phonemes list and the timecode to the times list. 
            if vals:
                phonemes.append(vals[2])
                times.append(float(vals[0]))
        
        if lipSync:
            if soundDelay > 0:
                # Set up a thread for the speech sound synthesis, delay start by soundDelay
                t = threading.Timer(soundDelay, saySpeech, args=(hdmiAudio,), kwargs=None)
                # Set up a thread for the speech movement
                t2 = threading.Thread(target=moveSpeechFest, args=(phonemes,times))
            else:
                # Set up a thread for the speech sound synthesis
                t = threading.Thread(target=saySpeech, args=(hdmiAudio,))
                # Set up a thread for the speech movement, delay start by - soundDelay
                t2 = threading.Timer(-soundDelay, moveSpeechFest, args=(phonemes,times), kwargs=None)
            t2.start() 
        else:
            # Set up a thread for the speech sound synthesis
            t = threading.Thread(target=saySpeech, args=(hdmiAudio,))      
        t.start()

        # if untilDone, keep running until speech has finished    
        if untilDone:
            totalTime = times[len(times)-1]
            startTime = time.time()
            while time.time()-startTime < totalTime:
                continue

    else:

    ######################
        # Create a bash command with the desired text. espeak.exe or another synthesizer must be in the current folder.  the -w parameter forces the speech to a file
        subprocess.call(["espeak","-a 200","-s 180","-ven+100","-g 10","-p 10", "-v", "mb-ir2","-w speech.wav", text])
        print("subprocessing")

        # open the file to calculate visemes. Festival on RPi has this built in but for espeak need to do it manually
        waveFile = wave.open('speech.wav', 'r')

        length = waveFile.getnframes()
        framerate = waveFile.getframerate()
        channels = waveFile.getnchannels()
        bytespersample = waveFile.getsampwidth()
        global duration
        duration = length / float(framerate)
        # How many samples per second for mouth position
        VISEMESPERSEC = 10

        # How many samples in 1/20th second
        # print ('framerate:', framerate, ' channels:', channels, ' length:', length, ' bytespersample:', bytespersample)

        chunk = int(waveFile.getframerate() / VISEMESPERSEC)
        # print ('chunk:', chunk)

        # Empty the lists that contain phoneme data and reset count
        phonemes = []
        times = []

        ms = 0

        for i in range(0, length - chunk, chunk):
            vol = 0
            buffer = waveFile.readframes(chunk)
            # frame is 1 sample for mono or 2 for stereo
            bytesread = chunk * channels * bytespersample
            # print ('bytesread:', bytesread)
            index = 0;
            for sample in range(0, int(bytesread / (channels * bytespersample))):
                vol += buffer[index]
                vol += buffer[index + 1] * 256
                index += bytespersample
                if channels > 1:
                    vol += buffer[index]
                    vol += buffer[index + 1] * 256
                    index += bytespersample

            # print ('viseme', i, ":", ms, ':', vol)
            ms += (1000 / VISEMESPERSEC);

            phonemes.append(float(vol))
            times.append(float(ms) / 1000)

    
    # Back to the beginning for next use
    waveFile.rewind()

    # Normalise the volume
    max = 0
    for i in range(0, len(phonemes) - 1):
        if (phonemes[i] > max):
            max = phonemes[i]

    for i in range(0, len(phonemes) - 1):
        phonemes[i] = phonemes[i] * 10 / max
        # print ('visnorm', i, ":", times[i], ':', phonemes[i])


    #print(phonemes)
    #phonemes = np.convolve(phonemes, np.ones((3,))/3, mode='valid')
    #print(phonemes)

    if lipSync:
        if soundDelay > 0:
            # Set up a thread for the speech sound synthesis, delay start by soundDelay
            t = threading.Timer(soundDelay, saySpeech, args=(hdmiAudio,), kwargs=None)
            # Set up a thread for the speech movement
            t2 = threading.Thread(target=moveSpeech, args=(phonemes, times))
        else:
            # Set up a thread for the speech sound synthesis
            t = threading.Thread(target=saySpeech, args=(hdmiAudio,))
            # Set up a thread for the speech movement, delay start by - soundDelay
            t2 = threading.Timer(-soundDelay, moveSpeech, args=(phonemes, times), kwargs=None)
        t2.start()
    else:
        # Set up a thread for the speech sound synthesis
        t = threading.Thread(target=saySpeech, args=(hdmiAudio,))
    t.start()
    global time_from_start
    time_from_start = time.time()
    # if untilDone, keep running until speech has finished    
    if untilDone:
        totalTime = times[len(times) - 1]
        startTime = time.time()
        while time.time() - startTime < totalTime:
            continue
        
# Function to limit values so they are between 0 - 10
def limit(val):
     if val > 10:
       return 10
     elif val < 0: 
        return 0
     else:
        return val

# Function to play back the speech wav file, if hmdi audio is being used play silence before speech sound
def saySpeech(addSilence):
    if addSilence:
        dir = os.path.dirname(os.path.abspath(__file__))
        silenceFile = os.path.join(dir, 'Silence1.wav')
        commandString = 'aplay ' + silenceFile + '\naplay speech.wav'
        os.system(commandString)        
    else:
        os.system('aplay speech.wav')
   
# Function to move Ohbot's lips in time with speech. Arguments | phonemes → list of phonemes[] | waits → list of waits[]
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
    
# Function to move Ohbot's lips in time with speech. Arguments | phonemes → list of phonemes[] | waits → list of waits[]
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
        
# Function to set the color of the LEDs in Ohbot's eyes.Arguments | r (red) → int (0-10) | g (green) → int (0-10) | b (blue) → int (0-10) 
# swapRandG is used to swap the red and green values on older Ohbots
def eyeColour(r, g, b, swapRandG = False):

    # Limit the values to keep them within range.
    r = limit(r)
    g = limit(g)
    b = limit(b)

    # Scale the values so they are between 0 - 255.
    r = int((255/10)*r)

    g = int((255/10)*g)

    b = int((255/10)*b)

    # Construct a message with the values.
    if swapRandG:

        msg1 = "l00,"+str(r)+","+str(g)+","+str(b)+"\n"
        msg2 = "l01,"+str(r)+","+str(g)+","+str(b)+"\n"

    else:       

        msg1 = "l00,"+str(g)+","+str(r)+","+str(b)+"\n"
        msg2 = "l01,"+str(g)+","+str(r)+","+str(b)+"\n"

    # Write message to serial port.
    serwrite(msg1)    
    serwrite(msg2)    

def wait(seconds):
    time.sleep(float(seconds))
    return

def close():       
    for x in range(0, len(motorMins)-1):
        detach(x)   

# Reset Ohbot back to start position
def reset():
    eyeColour(0,0,0)
    for x in range(0,len(restPos)-1):
        move(x,restPos[x])

# Return the sensor value between 0-10 for a given sensor number. Values stored in sensors[] array.
def readSensor(index):
    ser.flushInput()
    
    msg = "i0"+str(index)+"\n"
    serwrite(msg)

    line = ser.readline()
    lineStr = line.decode("utf-8")
    lines = lineStr.split(",")

    if len(lines) > 1:

        indexIn = lines[0]
        indexIn = indexIn[1]

        intdex = int(indexIn)
        
        newVal = int(lines[1])/1024
        newVal = newVal *10
        sensors[intdex] = limit(newVal)

    return sensors[index]
 
 
for i in range(7):
    move(i, 3 ,1)
    wait(2)

############################################################################################### SAY ENDS.


import json
import os
import sys
import time
import traceback
import logging
import serial
from subprocess import call
import subprocess
import pigpio
import psutil
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import speech_recognition as sr
from os import path, getcwd, system
import wave
import pyaudio
from future.backports.http.client import BadStatusLine

FORMAT = pyaudio.paInt16
RATE = 44100

m = sr.Microphone()
r = sr.Recognizer()
#ser = serial.Serial('/dev/ttyUSB0', 28800)


# This class inherits from WebSocket.
# It receives messages from the Scratch and reports back for any digital input
# changes.
class S2Pi(WebSocket):

    def handleMessage(self):
        # get command from Scratch2
        payload = json.loads(self.data)
        print(payload)
        client_cmd = payload['command']
        # When the user wishes to set a pin as a digital Input
        if client_cmd == 'input':
            pin = int(payload['pin'])
            self.pi.set_glitch_filter(pin, 20000)
            self.pi.set_mode(pin, pigpio.INPUT)
            self.pi.callback(pin, pigpio.EITHER_EDGE, self.input_callback)
        # when a user wishes to set the state of a digital output pin
        elif client_cmd == 'digital_write':
            pin = int(payload['pin'])
            self.pi.set_mode(pin, pigpio.OUTPUT)
            state = payload['state']
            if state == '0':
                self.pi.write(pin, 0)
            else:
                self.pi.write(pin, 1)
        # when a user wishes to set a pwm level for a digital input pin
        elif client_cmd == 'analog_write':
            pin = int(payload['pin'])
            self.pi.set_mode(pin, pigpio.OUTPUT)
            value = int(payload['value'])
            self.pi.set_PWM_dutycycle(pin, value)

        elif client_cmd == 'servo':
            # <------------------------<<<<<
            pin = int(payload['pin'])
            self.pi.set_mode(pin, pigpio.OUTPUT)
            value = int(payload['value'])
            DegreeMin = 0
            DegreeMax = 180
            PulseMin = 2500
            PulseMax = 690
            Pulsewidth = int((((PulseMax - PulseMin) / (DegreeMax - DegreeMin)) * value) + PulseMin)
            self.pi.set_servo_pulsewidth(pin, Pulsewidth)
            time.sleep(0.01)

        elif client_cmd == 'move':
            # <------------------------<<<<<
            parts_old = {'base': 2 , 'head' : 3, 'eyes': 4 ,'top lip' : 17, 'buttom lip' : 27, 'eyebrow': 22}
            parts = {'base': 5 , 'head' : 7, 'eyes': 9 ,'top lip' : 8, 'buttom lip' : 6, 'eyebrow': 1}
            motor = payload['pin']
            pin = parts[motor]
            self.pi.set_mode(pin, pigpio.OUTPUT)
            value = int(payload['value'])
            #DegreeMin = 0
            #DegreeMax = 180
            #PulseMin = 2500
            #PulseMax = 690
            #Pulsewidth = int((((PulseMax - PulseMin) / (DegreeMax - DegreeMin)) * value) + PulseMin)
            # self.pi.set_servo_pulsewidth(pin, Pulsewidth)
            if value <= 99:
                command = "M" + str(pin) + "_D0" + str(value)
            else:
                command = "M" + str(pin) + "_D" + str(value)
            print(command)
            ser.write(command.encode())
            time.sleep(0.01)
            

        elif client_cmd == 'speech_to_text':
            file_path = "query.wav"
            print('befor listening!')
            listen_and_record(file_path)
            print('after listneing!!!')
            stt_text = STT(file_path)
            print("stt")
            if "سلام" in stt_text:
                text = str("سلٓامْ.من قُلی هستمْ")
                subprocess.call(["espeak","-a 170","-s 190","-ven+100","-g 1.5","-p 10", "-v", "mb-ir2", text])
            print(stt_text)

        elif client_cmd == 'text_to_speech':
            text = str(payload['text'])
            #subprocess.call(["espeak","-a 170","-s 190","-ven+100","-g 1.5","-p 10", "-v", "mb-ir2", text])
            print("trying to speak!!!!")
            say(text)
            print("just said!")            
        
        
        elif client_cmd == "ask_name":
            text = str("سلٓامْ.من قُلی هستمْ.نامِ شُما چییست ؟")
            subprocess.call(["espeak","-a 170","-s 190","-ven+100","-g 1.5","-p 10", "-v", "mb-ir2", text])
            file_path = "query.wav"
            print('befor listening!')
            listen_and_record(file_path)
            print('after listneing!!!')
            stt_text = STT(file_path)
            text = str("سلٓامْ") + stt_text
            subprocess.call(["espeak","-a 170","-s 190","-ven+100","-g 1.5","-p 10", "-v", "mb-ir2", text])
            print(stt_text)    
        
        # when a user wishes to output a tone
        elif client_cmd == 'tone':
            pin = int(payload['pin'])
            self.pi.set_mode(pin, pigpio.OUTPUT)

            frequency = int(payload['frequency'])
            frequency = int((1000 / frequency) * 1000)
            tone = [pigpio.pulse(1 << pin, 0, frequency),
                    pigpio.pulse(0, 1 << pin, frequency)]

            self.pi.wave_add_generic(tone)
            wid = self.pi.wave_create()

            if wid >= 0:
                self.pi.wave_send_repeat(wid)
                time.sleep(0.01)
                self.pi.wave_tx_stop()
                self.pi.wave_delete(wid)
        elif client_cmd == 'ready':
            pass
        else:
            print("Unknown command received", client_cmd)

    # call back from pigpio when a digital input value changed
    # send info back up to scratch
    def input_callback(self, pin, level, tick):
        payload = {'report': 'digital_input_change', 'pin': str(pin), 'level': str(level)}
        print('callback', payload)
        msg = json.dumps(payload)
        self.sendMessage(msg)

    def handleConnected(self):
        self.pi = pigpio.pi()
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')


def run_server():
    # checking running processes.
    # if the backplane is already running, just note that and move on.
    found_pigpio = False

    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == "pigpiod":
            found_pigpio = True
            print("pigpiod is running")
        else:
            continue

    if not found_pigpio:
        call(['sudo', 'pigpiod'])
        print('pigpiod has been started')

    os.system('scratch2&')
    server = SimpleWebSocketServer('', 9000, S2Pi)
    server.serveforever()


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




if __name__ == "__main__":
    
    try:
        run_server()
    except KeyboardInterrupt:
        sys.exit(0)

    

