#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import time
import atexit

hat = Adafruit_MotorHAT(addr=0x60)

def turn_off_all_motors():
  for i in range(1, 5):
    hat.getMotor(i).run(Adafruit_MotorHAT.RELEASE)
atexit.register(turn_off_all_motors)

mouth = hat.getMotor(1)
head  = hat.getMotor(2)
tail  = hat.getMotor(3)

motor = head

delay = 0.4
speed = 100
loop = 3

for i in range(loop):
    motor.setSpeed(speed)
    motor.run(Adafruit_MotorHAT.BACKWARD)
    time.sleep(delay)
    motor.setSpeed(0)
    motor.run(Adafruit_MotorHAT.RELEASE)
    time.sleep(delay)

    motor.setSpeed(speed)
    motor.run(Adafruit_MotorHAT.FORWARD)
    time.sleep(delay)
    motor.setSpeed(0)
    motor.run(Adafruit_MotorHAT.RELEASE)
    time.sleep(delay)
