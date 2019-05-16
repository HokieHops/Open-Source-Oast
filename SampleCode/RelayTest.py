#!/usr/bin/env python

import time

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)
GPIO.output(5, GPIO.HIGH)

time.sleep(2)

GPIO.output(5, GPIO.LOW)
GPIO.cleanup()