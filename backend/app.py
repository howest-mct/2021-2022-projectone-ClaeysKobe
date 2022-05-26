import time
from RPi import GPIO
from helpers.klasseknop import Button
import threading

from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify, request
from repositories.DataRepository import DataRepository
from mfrc522 import SimpleMFRC522

from selenium import webdriver

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options


magnetPin = 17

# Default variables
magnet_status = 0
prev_magnet_status = 0

# Code voor Hardware


def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(magnetPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # rfid-reader
    global reader
    reader = SimpleMFRC522()
    # GPIO.setup(ledPin, GPIO.OUT)
    # GPIO.output(ledPin, GPIO.LOW)


# def lees_knop(pin):
#     if btnPin.pressed:
#         print("**** button pressed ****")
#         if GPIO.input(ledPin) == 1:
#             switch_light({'lamp_id': '3', 'new_status': 0})
#         else:
#             switch_light({'lamp_id': '3', 'new_status': 1})


# Code voor Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app)


@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(e)


# API ENDPOINTS
endpoint = '/api/v1'


@app.route('/')
def hallo():
    return "Server is running."


@app.route(endpoint + '/sensors/today/', methods=['GET'])
def sens_today():
    if request.method == 'GET':
        data = DataRepository.read_sensor_gesch_today()
        if data is not None:
            return jsonify(sensors=data), 200
        else:
            return jsonify(data="ERROR"), 404


@app.route(endpoint + '/sensors/', methods=['GET'])
def sensors():
    if request.method == 'GET':
        data = DataRepository.read_sensor_gesch()
        if data is not None:
            return jsonify(sensors=data), 200
        else:
            return jsonify(data="ERROR"), 404


@app.route(endpoint + '/sensors/lid/', methods=['GET'])
def sensors_lid():
    if request.method == 'GET':
        data = DataRepository.read_latest_lid()
        if data is not None:
            return jsonify(sensors=data), 200
        else:
            return jsonify(data="ERROR"), 404


@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # Send to the client!
    emit('B2F_change_magnet', {'status': magnet_status}, broadcast=True)


@socketio.on('F2B_openBox')
def open_box():
    print('Box opened via PC')
    # Add change to database
    answer = DataRepository.insert_box_value(0, "Lock geopend")
    print(answer)
    # Send to the client!
    socketio.emit('B2F_change_magnet', {'status': answer}, broadcast=True)
    socketio.emit('B2F_refresh_history', broadcast=True)


@socketio.on('F2B_closeBox')
def open_box():
    print('Box closed via PC')
    # Add change to database
    answer = DataRepository.insert_box_value(1, "Lock gesloten")
    print(answer)
    # Send to the client!
    socketio.emit('B2F_change_magnet', {'status': answer}, broadcast=True)
    socketio.emit('B2F_refresh_history', broadcast=True)

# START een thread op. Belangrijk!!! Debugging moet UIT staan op start van de server, anders start de thread dubbel op
# werk enkel met de packages gevent en gevent-websocket.


def read_sensor_magnet():
    while True:
        global magnet_status
        global prev_magnet_status
        magnet_status = GPIO.input(magnetPin)
        if magnet_status != prev_magnet_status:
            beschrijving = ''
            if magnet_status == 0:
                beschrijving = "Brievenbusklep gesloten"
            else:
                beschrijving = "brievenbusklep geopend"
            answer = DataRepository.insert_magnet_value(
                magnet_status, beschrijving)
            print(f"New magnet value: {answer}")
            socketio.emit('B2F_change_magnet', {
                          'status': magnet_status}, broadcast=True)
            socketio.emit('B2F_refresh_history', broadcast=True)
        prev_magnet_status = magnet_status


def read_rfid():
    while True:
        id, text = reader.read()
        print("ID: %s\nText: %s" % (id, text))


def start_thread():
    print("**** Starting THREADS ****")
    thread = threading.Thread(target=read_sensor_magnet, args=(), daemon=True)
    thread.start()


def start_thread2():
    thread2 = threading.Thread(target=read_rfid, args=(), daemon=True)
    thread2.start()


def start_chrome_kiosk():
    import os

    os.environ['DISPLAY'] = ':0.0'
    options = webdriver.ChromeOptions()
    # options.headless = True
    # options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    # options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    # options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--kiosk')
    # chrome_options.add_argument('--no-sandbox')
    # options.add_argument("disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.get("http://localhost")
    while True:
        pass


def start_chrome_thread():
    print("**** Starting CHROME ****")
    chromeThread = threading.Thread(
        target=start_chrome_kiosk, args=(), daemon=True)
    chromeThread.start()


# ANDERE FUNCTIES

if __name__ == '__main__':
    try:
        setup_gpio()
        start_thread()
        start_thread2()
        start_chrome_thread()
        print("**** Starting APP ****")
        socketio.run(app, debug=False, host='0.0.0.0')
    except KeyboardInterrupt:
        print('KeyboardInterrupt exception is caught')
    finally:
        GPIO.cleanup()
