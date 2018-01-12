#!/usr/bin/env python

from setuptools import setup
import numpy

setup(
    name='pibass',
    version='0.1',
    description='Big Mouth Billy Bass Raspberry Pi controller with Adafruit MotorHAT and AWS Polly TTS',
    author='ElementAI',
    author_email='hello@elementai.com',
    packages=['pibass'],
    install_requires=[
      'Adafruit_MotorHAT',
      'aubio',
      'boto3',
      'googletrans',
      'pydub',
      'rtmbot',
    ],
)
