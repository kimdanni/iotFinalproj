from flask import Flask, Response, jsonify, make_response, render_template, request
from flask_cors import CORS
from flask.helpers import send_file

import cv2
import time, io
import base64
import numpy as np

from threading import Thread , Lock

from numpy.lib.arraysetops import isin

import datetime

from gtts import gTTS
import os

#from get_camera_settings import CamSettings
from crawl import Weather
from grovepi import *

greenled = 4
redled = 3
button = 2
pinMode(button, "INPUT")
pinMode(greenled, "OUTPUT")
pinMode(redled, "OUTPUT")


class database:
    def __init__(self):
        self.__width  = 500
        self.__height = 500
        self.__brightness = -7
        self.__lightcount = 4
        self.__light = True
        
        wt = Weather()
        self.__weather = wt.run()
        
        self.__cap = None
        
    @property
    def weather(self):
        return self.__weather

    @weather.setter
    def weather(self, val):
        if isinstance(val, int):
            pass
        elif isinstance(val, str):
            try:         val = int(val)
            except:      pass
        else:
            return
        self.__weather = val
        
    @property
    def light(self):
        return self.__light

    @light.setter
    def light(self, val):
        if isinstance(val, bool):
            pass
        elif isinstance(val, str):
            try:         val = bool(val)
            except:      pass
        else:
            return
        self.__light = val
    
    @property
    def lightcount(self):
        return self.__lightcount

    @lightcount.setter
    def lightcount(self, val):
        if isinstance(val, int):
            pass
        elif isinstance(val, str):
            try:         val = int(val)
            except:      pass
        else:
            return
        self.__lightcount = val
        
    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, val):
        if isinstance(val, int):
            pass
        elif isinstance(val, str):
            try:         val = int(val)
            except:      pass
        else:
            return
        self.__width = val

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, val):
        if isinstance(val, int):
            pass
        elif isinstance(val, str):
            try:         val = int(val)
            except:      pass
        else:
            return
        self.__height = val
        
    @property
    def brightness(self):
        return self.__brightness

    @brightness.setter
    def brightness(self, val):
        if isinstance(val, int):
            pass
        elif isinstance(val, str):
            try:         val = int(val)
            except:      pass
        else:
            return
        self.__brightness = val
    @property
    def quality(self):
        return self.__quality

    @quality.setter
    def quality(self, val):
        if isinstance(val, int):
            pass
        elif isinstance(val, str):
            try:         val = int(val)
            except:      pass
        else:
            return
        self.__quality = val
    @property
    def cap(self):
        return self.__cap

    @cap.setter
    def cap(self, val):
        self.__cap = val
    def init(self):
        self.__cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)
        self.__cap.set(cv2.CAP_PROP_FRAME_WIDTH,500)
        self.__cap.set(cv2.CAP_PROP_BRIGHTNESS,40)

    def initialize(self):
        if(self.__cap == None):
            return
        self.__cap.set(cv2.CAP_PROP_BRIGHTNESS, self.__brightness)
    

def cam_get():
    global db
    global img
    try:
        db.cap = cv2.VideoCapture(0)
        while True:
            lock.acquire()
            ret, img = db.cap.read()
            lock.release()
            
            time.sleep(0.03)
    except (KeyboardInterrupt, SystemExit):
        print('\n! Received keyboard interrupt, quitting threads.\n')
    finally:
        db.cap.release()

def traffic_light():
    global db
    count = 0
    flag = False
    while True:
        count += 1
        button_status = digitalRead(button)
        delay = 2
        if(button_status):
            flag = True
        if(count > db.lightcount):
            if(flag):
                delay = 4
            if(count > db.lightcount*delay):
                count = 0
            digitalWrite(greenled, 1)
            digitalWrite(redled, 0)
            db.light = not db.light
        else:
            if(flag):
                flag = False
                delay = 2
            digitalWrite(redled, 1)
            digitalWrite(greenled, 0)
        time.sleep(1)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(SECRET_KEY='dev')
    app.config.from_pyfile('config.py', silent=True)
    
    @app.route('/')
    def index():
        return render_template('a.html')
    
    
    @app.route('/video_feed')
    def video_feed():
        global db
        lock.acquire()
        encoded = base64.b64encode(cv2.imencode('.jpeg', img)[1].tobytes())
        lock.release()
            
        response = make_response(encoded)
        response.headers.set('Content-Type', 'image/jpg')
        response.headers.set('Content-Disposition', 'attachment', filename='test.jpg')
        return response
    
    @app.route('/cam_release')
    def cam_release():
        global db
        db.init()
        if(db.cap == None):
            response = make_response()
            return response;
        db.cap.release()
        response = make_response()
        return response;
    
    @app.route('/set_api', methods=['POST'])
    def set_api():
        global db
        global img
        data = request.get_json()
        db.brightness, db.quality = data['brightness'], data['quality']
        db.initialize()
        now = datetime.datetime.now()
        response = make_response()
        db.init()
        return response
    
    @app.route('/get_settings/<setting>')
    def get_settings(setting):
        global db
        if(setting == "brightness"):
            return str(db.brightness)
        if(setting == "quality"):
            return str(db.quality)
        if(setting == "weather"):
            return str(db.weather)
        if(setting == "light"):
            info = ""
            if(db.light):
                info = "RED"
            else:
                info = "GREEN"
            return str(info)
        response = make_response()
        return response
    return app

if __name__ == "__main__":
    global db
    db = database()
    th = Thread(target=cam_get)
    th.daemon = True
    th.start()
    
    th1 = Thread(target=traffic_light)
    th1.daemon = True
    th1.start()
    
    lock = Lock()
    try:
        app = create_app()
        CORS(app)
        app.run("0.0.0.0", port=8000)
        
    except (KeyboardInterrupt, SystemExit):
        print('\n! Received keyboard interrupt, quitting threads.\n')