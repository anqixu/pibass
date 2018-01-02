#!/usr/bin/env python

import atexit
import heapq
import random
import threading
import time

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor


class PiBassMotors(object):
  def __init__(self):
    self.hat = Adafruit_MotorHAT(addr=0x60)
    self.hat_mutex = threading.Lock()
    with self.hat_mutex:
      self.head  = self.hat.getMotor(1)
      self.mouth = self.hat.getMotor(2)
      self.tail  = self.hat.getMotor(3)

    atexit.register(self.terminate)


  def __enter__(self):
    return self


  def __exit__(self, type, value, traceback):
    self.terminate()


  def terminate(self):
    self.turn_off_all_motors()


  def turn_off_all_motors(self):
    with self.hat_mutex:
      for i in range(1, 5):
        self.hat.getMotor(i).run(Adafruit_MotorHAT.RELEASE)


  def test_motor(self, motor, delay=0.3, speed=255, loop=3, reverse_first=False, t=None):
    with self.hat_mutex:
      for i in range(loop):
        move_dir = Adafruit_MotorHAT.BACKWARD if reverse_first else Adafruit_MotorHAT.FORWARD
        motor.setSpeed(speed)
        motor.run(move_dir)
        time.sleep(delay)
        motor.setSpeed(0)

        time.sleep(delay)

        move_dir = Adafruit_MotorHAT.FORWARD if reverse_first else Adafruit_MotorHAT.BACKWARD
        motor.setSpeed(speed)
        motor.run(move_dir)
        time.sleep(delay)
        motor.setSpeed(0)

        time.sleep(delay)

      motor.run(Adafruit_MotorHAT.RELEASE)


  def move_head(self, speed=255, delay_move=0.3, open=True, release=True, t=None):
    with self.hat_mutex:
      motor = self.head
      motor.setSpeed(speed)
      motor.run(Adafruit_MotorHAT.BACKWARD if open else Adafruit_MotorHAT.FORWARD)
      time.sleep(delay_move)
      motor.setSpeed(0)
      if release:
        motor.run(Adafruit_MotorHAT.RELEASE)


  def move_mouth(self, speed=255, delay_move=0.12, delay_open=0.15, release=True, t=None):
    with self.hat_mutex:
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


  def move_tail(self, speed=255, delay_move=0.12, delay_open=0.1, release=True, t=None):
    with self.hat_mutex:
      motor = self.tail
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


class MotorEvent:
  def __init__(self, motor, run_arg=None, speed=None):
    self.motor = motor
    self.run_arg = run_arg
    self.speed = speed


class PiBassAsyncMotors(PiBassMotors):
  def __init__(self):
    self.events = []
    self.events_mutex = threading.Lock()
    self.event_loop_active = False
    self.event_thread = threading.Thread(target=self.event_loop)
    super(PiBassAsyncMotors, self).__init__()
    self.event_thread.start()


  def terminate(self):
    self.event_loop_active = False
    if self.event_thread is not None:
      self.event_thread.join()
      self.event_thread = None
    super(PiBassAsyncMotors, self).terminate()


  def add_event(self, event, t=time.time()):
    with self.events_mutex:
      heapq.heappush(self.events, (t, event))


  def event_loop(self):
    self.event_loop_active = True

    while self.event_loop_active:
      now = time.time()
      if len(self.events) > 0 and self.events[0][0] <= now: # if has time-expired event
        with self.events_mutex:
          event_t, event = heapq.heappop(self.events)
        with self.hat_mutex:
          if event.speed is not None:
            event.motor.setSpeed(event.speed)
          if event.run_arg is not None:
            event.motor.run(event.run_arg)
        continue

      else: # did not process any events
        time.sleep(0.001)

    self.event_loop_active = False


  def test_motor(self, motor, delay=0.3, speed=255, loop=3, reverse_first=False, t=None):
    if t is None:
      t = time.time()
      
    for i in range(loop):
      move_dir = Adafruit_MotorHAT.BACKWARD if reverse_first else Adafruit_MotorHAT.FORWARD
      self.add_event(MotorEvent(motor, move_dir, speed), t)
      t += delay
      self.add_event(MotorEvent(motor, None, 0), t)

      t += delay

      move_dir = Adafruit_MotorHAT.FORWARD if reverse_first else Adafruit_MotorHAT.BACKWARD
      self.add_event(MotorEvent(motor, move_dir, speed), t)
      t += delay
      self.add_event(MotorEvent(motor, None, 0), t)

      t += delay

      self.add_event(MotorEvent(motor, Adafruit_MotorHAT.RELEASE, None), t)

      return t


  def move_head(self, speed=255, delay_move=0.3, open=True, release=True, t=None):
    if t is None:
      t = time.time()
    motor = self.head
    direction = Adafruit_MotorHAT.BACKWARD if open else Adafruit_MotorHAT.FORWARD
    self.add_event(MotorEvent(motor, direction, speed), t)
    t += delay_move
    self.add_event(MotorEvent(motor, None, 0), t)
    if release:
      self.add_event(MotorEvent(motor, Adafruit_MotorHAT.RELEASE, None), t)
    return t


  def move_mouth(self, speed=255, delay_move=0.12, delay_open=0.15, release=True, t=None):
    if t is None:
      t = time.time()
    motor = self.mouth
    self.add_event(MotorEvent(motor, Adafruit_MotorHAT.FORWARD, speed), t)
    t += delay_move
    self.add_event(MotorEvent(motor, None, 0), t)
    t += delay_open
    self.add_event(MotorEvent(motor, Adafruit_MotorHAT.BACKWARD, speed), t)
    t += delay_move
    self.add_event(MotorEvent(motor, None, 0), t)
    if release:
      self.add_event(MotorEvent(motor, Adafruit_MotorHAT.RELEASE, None), t)
    return t


  def move_tail(self, speed=255, delay_move=0.12, delay_open=0.1, release=True, t=None):
    if t is None:
      t = time.time()
    motor = self.tail
    self.add_event(MotorEvent(motor, Adafruit_MotorHAT.FORWARD, speed), t)
    t += delay_move
    self.add_event(MotorEvent(motor, None, 0), t)
    t += delay_open
    self.add_event(MotorEvent(motor, Adafruit_MotorHAT.BACKWARD, speed), t)
    t += delay_move
    self.add_event(MotorEvent(motor, None, 0), t)
    if release:
      self.add_event(MotorEvent(motor, Adafruit_MotorHAT.RELEASE, None), t)
    return t


def test_pibass_motors(async=True):
  bass = PiBassAsyncMotors() if async else PiBassMotors()
  test_head = True
  test_mouth = False
  test_tail = False

  if test_head:
    t = bass.move_head(open=True, release=False)
    if async:
      time.sleep(t-time.time())
    time.sleep(0.5)
    t = bass.move_head(open=False, release=False)
    if async:
      time.sleep(t-time.time())
    time.sleep(1)

  if test_mouth:
    for i in range(5):
      t = bass.move_mouth(delay_open=random.uniform(0.05, 0.15), release=False)
      if async:
        time.sleep(t-time.time())
      time.sleep(random.uniform(0.025, 0.15))
    time.sleep(1)

  if test_tail:
    for i in range(5):
      t = bass.move_tail(delay_open=random.uniform(0.05, 0.2), release=False)
      if async:
        time.sleep(t-time.time())
      time.sleep(random.uniform(0.025, 0.15))
    time.sleep(1)

  #bass.test_motor(bass.mouth, reverse_first=False)
  #bass.test_motor(bass.tail,  reverse_first=False)
  #bass.test_motor(bass.head,  reverse_first=False)

  bass.terminate()


if __name__ == '__main__':
  test_pibass_motors()
