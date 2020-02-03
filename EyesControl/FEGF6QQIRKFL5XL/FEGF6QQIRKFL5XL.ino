// LED display v1.0 By Igor Fonseca Albuquerque, Thiago Farrauche, Diego Augustus and Yhan Christian

//include libraries
#include "LedControl.h"

LedControl lc = LedControl(13,12,11,5); //Pin 13 = DIN, Pin 12 = CLK, Pin 11 = CS. 5 = number of displays

//************************
// Definition of the faces
//************************

// neutral eye
byte neutral_eye[8] = {B00000000,
                       B00011000,
                       B00111100,
                       B01111110,
                       B01111110,
                       B00111100,
                       B00011000,
                       B00000000};

// spooky eye
byte spooky_eye[8] = {B00111100,
                      B01111110,
                      B11111111,
                      B11111111,
                      B11111111,
                      B11111111,
                      B01111110,
                      B00111100};

// closed eye (up)
byte closed_eye_up[8] = {B00000000,
                         B00001100,
                         B00011000,
                         B00011000,
                         B00011000,
                         B00011000,
                         B00001100,
                         B00000000};
                        
// closed eye (down)
byte closed_eye_down[8] ={B00000000,
                          B00001100,
                          B00001100,
                          B00000110,
                          B00000110,
                          B00001100,
                          B00001100,
                          B00000000};                        

// happy mouth           //part 1 
byte happy_mouth[24] = { B00000000,
                         B00000000,
                         B00000000,
                         B00000000,
                         B01100000,
                         B00110000,
                         B00011000,
                         B00001100,    
                         //part 2
                         B00001110,
                         B00000110,
                         B00000110,
                         B00000110,
                         B00000110,
                         B00000110,
                         B00000110,
                         B00001100,
                         //part 3 
                         B00001100,
                         B00011000,
                         B00110000,
                         B01100000,
                         B00000000,
                         B00000000,
                         B00000000,
                         B00000000 };
                         
                                                  
// sad mouth            //part 1
byte sad_mouth[24] = {   B00000000,
                         B00000000,
                         B00000000,
                         B00000000,
                         B00000110,
                         B00001100,
                         B00011000,
                         B00110000,
                         //part 2
                         B00110000,
                         B01100000,
                         B01100000,
                         B01100000,
                         B01100000,
                         B01100000,
                         B01100000,
                         B00110000,
                         //part 3
                         B00110000,
                         B00011000,
                         B00001100,
                         B00000110,
                         B00000000,
                         B00000000,
                         B00000000,
                         B00000000 };

//very happy mouth            //part 1
byte very_happy_mouth[24] = { B00000000,
                              B00000000,
                              B01110000,
                              B01111100,
                              B01100110,
                              B01100110,
                              B01100011,
                              B01100011,
                              //part 2
                              B01100011,
                              B01100011,
                              B01100011,
                              B01100011,
                              B01100011,
                              B01100011,
                              B01100011,
                              B01100011,                        
                              //part 3
                              B01100011,
                              B01100011,
                              B01100110,
                              B01100110,
                              B01111100,
                              B01110000,
                              B00000000,
                              B00000000 };                         
                         
// neutral mouth              //part 1
byte neutral_mouth[24] = {    B00000000,
                              B00000000,
                              B00010000,
                              B00010000,
                              B00010000,
                              B00010000,
                              B00010000,
                              B00010000,
                              //part 2
                              B00010000,
                              B00010000,
                              B00010000,
                              B00010000,
                              B00010000,
                              B00010000,
                              B00010000,
                              B00010000,
                              //part 3
                              B00010000,
                              B00010000,
                              B00010000,
                              B00010000,
                              B00010000,
                              B00010000,
                              B00000000,
                              B00000000 };
                         
// tongue out            //part 1
byte tongue_mouth[24] = {B00000000,
                         B00000000,
                         B00000100,
                         B11001110,
                         B01111110,
                         B00111110,
                         B00011100,
                         B00001100,    
                         //part 2
                         B00001110,
                         B00000110,
                         B00000110,
                         B00000110,
                         B00000110,
                         B00000110,
                         B00000110,
                         B00001100,
                         //part 3 
                         B00001100,
                         B00011000,
                         B00110000,
                         B01100000,
                         B00000000,
                         B00000000,
                         B00000000,
                         B00000000 };

// opened mouth            //part 1
byte opened_mouth[24] = {  B00000000,
                           B00000000,
                           B00000000,
                           B00000000,
                           B00000000,
                           B00000000,
                           B00000000,
                           B00000000,
                           // part 2
                           B00000000,
                           B00011100,
                           B00100010,
                           B01000001,
                           B01000001,
                           B00100010,
                           B00011100,
                           B00000000,
                           // part 3
                           B00000000,
                           B00000000,
                           B00000000,
                           B00000000,
                           B00000000,
                           B00000000,
                           B00000000,
                           B00000000 };

//**************
// Arduino Setup
//**************
void setup()
{
  //initialize displays (configure light intensity and clear all)
  lc.shutdown(0,false);
  lc.setIntensity(0,1);
  lc.clearDisplay(0);
  lc.shutdown(1,false);
  lc.setIntensity(1,1);
  lc.clearDisplay(1);
  lc.shutdown(2,false);
  lc.setIntensity(2,1);
  lc.clearDisplay(2);
  lc.shutdown(3,false);
  lc.setIntensity(3,1);
  lc.clearDisplay(3);
  lc.shutdown(4,false);
  lc.setIntensity(4,1);
  lc.clearDisplay(4);
 
  //start serial communication
  Serial.begin(19200);
  
}

//**********
// Main Loop
//**********
void loop()
{
  display_eyes(neutral_eye, neutral_eye);
  if (Serial.available())  //verifies if there is serial data available
  {
    char cmd = Serial.read();
              
    if(cmd == ':') {
      display_eyes(neutral_eye, neutral_eye);
    }
    if(cmd == ';') {
      display_eyes(neutral_eye, closed_eye_up);
    }
    if(cmd == '8') {
      display_eyes(spooky_eye, spooky_eye);
    }
    if(cmd == ')'){
      display_mouth(happy_mouth);
    }    
    if(cmd == '('){
      display_mouth(sad_mouth);
    }    
    if((cmd == 'D')||(cmd == 'd')){
      display_mouth(very_happy_mouth);
    }
    if((cmd == 'p')||(cmd == 'P')){
      display_mouth(tongue_mouth);
    }    
    if((cmd == 'o')||(cmd == 'O')){
      display_mouth(opened_mouth);
    }    
    if(cmd == '|'){
      display_mouth(neutral_mouth);
    }    

  }
}


//********************
// Auxiliary functions
//********************

//change eyes
void display_eyes(byte right_eye[], byte left_eye[]) {
  for(int i=0;i<8;i++) {
   lc.setRow(0,i,left_eye[i]);
   lc.setRow(1,i,right_eye[i]);
  } 
}


//change mouth
void display_mouth(byte mouth[]) {
  for(int i=0;i<8;i++) {
    lc.setRow(2,i,mouth[i]);
    lc.setRow(3,i,mouth[i+8]);
    lc.setRow(4,i,mouth[i+16]);
  }
}

//setRow is used instead of setColumn because it runs faster! Although, characters must be declared rotated 90 degrees counter-clockwise
