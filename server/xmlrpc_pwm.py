#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_PWM_Servo_Driver

import time

FULL_ON = 4095

pwm = None

def pwm_init():
   global pwm
   pwm = Adafruit_PWM_Servo_Driver.PWM(address=0x60)

   # Bridge Input PWMs based on schematic/datasheet
   pwm.setPWM(5,FULL_ON,0)
   pwm.setPWM(6,0,FULL_ON)
   pwm.setPWM(3,FULL_ON,0)
   pwm.setPWM(4,0,FULL_ON)
   pwm.setPWM(9,FULL_ON,0)
   pwm.setPWM(10,0,FULL_ON)
   pwm.setPWM(11,FULL_ON,0)
   pwm.setPWM(12,0,FULL_ON)

   # Duty cycle PWMs for each bridge - all off
   pwm.setPWM(8,FULL_ON,0)
   pwm.setPWM(13,FULL_ON,0)
   pwm.setPWM(2,FULL_ON,0)
   pwm.setPWM(7,FULL_ON,0)

def pwm_set(state):

   global pwm

   if not state:
     pwm.setPWM(8,FULL_ON,0)
     pwm.setPWM(13,FULL_ON,0)
     pwm.setPWM(2,FULL_ON,0)
     pwm.setPWM(7,FULL_ON,0)
     print("OFF")

   else:
     pwm.setPWM(8,0,FULL_ON)
     pwm.setPWM(13,0,FULL_ON)
     pwm.setPWM(2,0,FULL_ON)
     pwm.setPWM(7,0,FULL_ON)
     print("ON")


