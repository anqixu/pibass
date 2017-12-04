#!/usr/bin/python

import atexit
import heapq
import random
import threading
import time

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor


class MotorEvent:
  def __init__(self, motor, run_arg=Adafruit_MotorHAT.RELEASE, speed=-1):
    self.motor = motor
    self.run_arg = run_arg
    self.speed = speed


class PiBass(object):
  def __init__(self):
    self.hat = Adafruit_MotorHAT(addr=0x60)
    self.hat_mutex = threading.Lock()

    self.mouth = self.hat.getMotor(1)
    self.head  = self.hat.getMotor(2)
    self.tail  = self.hat.getMotor(3)

    self.events = []
    self.events_mutex = threading.Lock()
    self.event_loop_active = False
    self.event_thread = threading.Thread(target=self.event_loop)
    atexit.register(self.terminate)


  def __enter__(self):
    return self


  def __exit__(self, type, value, traceback):
    self.terminate()


  def terminate(self):
    self.turn_off_all_motors()
    self.event_loop_active = False
    if self.event_thread is not None:
      self.event_thread.join()
      self.event_thread = None


  def add_event(self, event, t=time.time()):
    with self.events_mutex:
      heapq.heappush(self.events, (t, event))


  def event_loop(self):
    self.event_loop_active = True

    while self.event_loop_active:
      now = time.time()
      if len(self.events) > 0 and self.events[0][0] >= now: # if has time-expired event
        with self.events_mutex:
          _, event = heapq.heappop(self.events)
        with self.hat_mutex:
          if event.speed >= 0:
            event.motor.setSpeed(event.speed)
          event.motor.run(event.run_arg)
        continue

      else: # did not process any events
        time.sleep(0.01)

    self.event_loop_active = False


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