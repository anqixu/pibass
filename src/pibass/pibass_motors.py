#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import time
import atexit
import random


class PiBass(object):
  def __init__(self):
    self.hat = Adafruit_MotorHAT(addr=0x60)
    atexit.register(self.turn_off_all_motors)

    self.mouth = self.hat.getMotor(1)
    self.head  = self.hat.getMotor(2)
    self.tail  = self.hat.getMotor(3)


  def turn_off_all_motors(self):
    for i in range(1, 5):
      self.hat.getMotor(i).run(Adafruit_MotorHAT.RELEASE)


  def test_motor(self, motor, delay=0.3, speed=255, loop=3, pre_unlatch_delay=0.0, reverse_first=False):
    for i in range(loop):
      move_dir = Adafruit_MotorHAT.BACKWARD if reverse_first else Adafruit_MotorHAT.FORWARD
      unlatch_dir = Adafruit_MotorHAT.FORWARD if reverse_first else Adafruit_MotorHAT.BACKWARD
      if pre_unlatch_delay > 0:
        motor.setSpeed(255)
        motor.run(unlatch_dir)
        time.sleep(pre_unlatch_delay)
      motor.setSpeed(speed)
      motor.run(move_dir)
      time.sleep(delay)
      motor.setSpeed(0)

      time.sleep(delay)

      move_dir, unlatch_dir = unlatch_dir, move_dir
      if pre_unlatch_delay > 0:
        motor.setSpeed(255)
        motor.run(unlatch_dir)
        time.sleep(pre_unlatch_delay)
      motor.setSpeed(speed)
      motor.run(move_dir)
      time.sleep(delay)
      motor.setSpeed(0)

      time.sleep(delay)

    motor.run(Adafruit_MotorHAT.RELEASE)


  def move_mouth(self, speed=255, delay_move=0.12, delay_open=0.15, release=False):
    motor = self.mouth
    motor.setSpeed(speed)
    motor.run(Adafruit_MotorHAT.FORWARD)
    time.sleep(delay_move)
    motor.setSpeed(0)
    time.sleep(delay_open)
    motor.setSpeed(speed)
    motor.run(Adafruit_MotorHAT.BACKWARD)
    time.sleep(delay_move)
    motor.setSpeed(0)
    if release:
      motor.run(Adafruit_MotorHAT.RELEASE)


  def move_tail(self, speed=255, delay_move=0.15, delay_open=0.2):
    motor = self.tail
    motor.setSpeed(speed)
    motor.run(Adafruit_MotorHAT.FORWARD)
    time.sleep(delay_move)
    motor.setSpeed(0)
    time.sleep(delay_open)
    motor.run(Adafruit_MotorHAT.RELEASE)


def main():
  # TODO: implement spin loop to asynchronously submit motor changes
  # TODO: start thread with spin loop enabled; on die release all motors
  # TODO: find some python audio library to compute amplitude signal given audio file
  #       binarize (with hysterisis?), and trigger mouth movements

  bass = PiBass()
  test_mouth = False
  test_tail = True

  if test_mouth:
    for i in range(10):
      bass.move_mouth(delay_open=random.uniform(0.05, 0.15))
      time.sleep(random.uniform(0.025, 0.15))
    time.sleep(1)
    bass.mouth.run(Adafruit_MotorHAT.RELEASE)

  if test_tail:
    for i in range(10):
      bass.move_tail(delay_open=random.uniform(0.1, 0.3))
      time.sleep(random.uniform(0.025, 0.15))

  #bass.test_motor(bass.mouth, reverse_first=False)
  #bass.test_motor(bass.tail,  reverse_first=False)
  #bass.test_motor(bass.head,  reverse_first=True, pre_unlatch_delay=0.1)


if __name__ == '__main__':
  main()