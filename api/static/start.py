# encoding=utf8
import atexit
import Image
import ImageDraw
import ImageFont
import time
import signal
import logging
import json
import psutil
import subprocess
import threading
import os
import sys
from base import base
from weather import weather
from customtext import customtext
from logo import logo
from ad import ad
from train import train
from systemlogs import systemlogs
import constants
import logs

b = base()
swap = b.matrix.CreateFrameCanvas()
customTextScreen = customtext(b)
logoScreen = logo(b)
adScreen = ad(b)
trainScreen = train(b)
weatherScreen = weather(b)
systemlogger = systemlogs(b)

fontXoffset = 0
topOffset   = 3
image     = Image.new('RGB', (constants.width, constants.height))
draw      = ImageDraw.Draw(image)

def signal_handler(signal, frame):
    b.matrix.Clear()
    sys.exit(0)

def clearOnExit():
    b.matrix.Clear()

def drawClear():
    draw.rectangle((0, 0, constants.width, constants.height), fill=constants.black)
    b.matrix.SetImage(image, 0, 0)

def displayError(e):
    drawClear()
    draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), e, font=constants.font, fill=constants.orange)
    b.matrix.SetImage(image, 0, 0)
    time.sleep(1)
    drawClear()

atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

while True:
    try:
        swap.Clear()
        if b.config["customtext"]["enabled"] == True:
            customTextScreen.draw()

        swap.Clear()
        if b.config["weather"]["enabled"] == True:
            weatherScreen.draw()

        swap.Clear()
        if b.config["subway"]["enabled"] == True:
            trainScreen.draw('S')
            swap.Clear()
            trainScreen.draw('N')

        swap.Clear()
        if b.config["logo"]["enabled"] == True:
            logoScreen.draw()

    except Exception as e:
        logging.exception("message")
        pass
