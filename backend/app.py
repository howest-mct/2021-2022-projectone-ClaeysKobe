import time
from RPi import GPIO
from helpers.klasseknop import Button
from classes.lcd_class import LCD_Module
from classes.spi_class import SpiClass
import threading
import netifaces as ni

from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify, request
from repositories.DataRepository import DataRepository
from mfrc522 import SimpleMFRC522

from selenium import webdriver

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options


buzzerPin = 23
magnetPin = 17
btnPin = Button(21)

# Default variables
magnet_status = 0
prev_magnet_status = 0
lock_opened = False
register_rfid = False
brieven_vandaag = f""
ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
# Code voor Hardware


def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(buzzerPin, GPIO.OUT)
    GPIO.setup(magnetPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # rfid-reader
    global reader
    reader = SimpleMFRC522()
    # lcd
    global lcd_module
    lcd_module = LCD_Module(16, 20)
    # spi
    global spiObj
    spiObj = SpiClass(0, 1)
    # aantal brieven vandaag setten
    global brieven_vandaag
    brieven_vandaag = DataRepository.read_brieven_today()
    brieven_vandaag = brieven_vandaag[0]
    brieven_vandaag = brieven_vandaag['Aantal']
    show_brieven_vandaag()


def lees_knop(pin):
    if btnPin.pressed:
        print("**** button pressed: showing IP ****")
        lcd_module.write_message(ip)
        time.sleep(5)
        show_brieven_vandaag()


def show_brieven_vandaag():
    if brieven_vandaag > 0:
        lcd_module.write_message(f"Brieven vandaag:{brieven_vandaag}")
    else:
        lcd_module.write_message(f"Nog geen brievenontvangen")


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


@app.route(endpoint + '/events/today/', methods=['GET'])
def sens_today():
    if request.method == 'GET':
        data = DataRepository.read_sensor_gesch_today()
        if data is not None:
            return jsonify(sensors=data), 200
        else:
            return jsonify(data="ERROR"), 404


@app.route(endpoint + '/events/', methods=['GET'])
def sensors():
    if request.method == 'GET':
        data = DataRepository.read_sensor_gesch()
        if data is not None:
            return jsonify(sensors=data), 200
        else:
            return jsonify(data="ERROR"), 404


@app.route(endpoint + '/events/lid/', methods=['GET'])
def sensors_lid():
    if request.method == 'GET':
        data = DataRepository.read_latest_lid()
        if data is not None:
            return jsonify(sensors=data), 200
        else:
            return jsonify(data="ERROR"), 404


@app.route(endpoint + '/events/letters/', methods=['GET'])
def sensors_letters():
    if request.method == 'GET':
        data = DataRepository.read_brieven_today()
        if data is not None:
            return jsonify(sensors=data), 200
        else:
            return jsonify(data="ERROR"), 404


@app.route(endpoint + '/users/', methods=['GET', 'POST'])
def gebruikers():
    if request.method == 'GET':
        data = DataRepository.read_users()
        if data is not None:
            return jsonify(gebruikers=data), 200
        else:
            return jsonify(data="ERROR"), 404
    elif request.method == 'POST':
        te_verzenden = DataRepository.json_or_formdata(request)
        rfid = te_verzenden['rfid']
        naam = te_verzenden['naam']
        wachtwoord = te_verzenden['wachtwoord']
        answer = DataRepository.insert_user(rfid, naam, wachtwoord)
        if answer is not None:
            return jsonify(data=answer), 201
        else:
            return jsonify(data="ERROR"), 400


@app.route(endpoint + '/user/<UserID>/', methods=['GET', 'PUT', 'DELETE'])
def gebruiker(UserID):
    if request.method == 'GET':
        data = DataRepository.read_user(UserID)
        if data is not None:
            return jsonify(gebruikers=data), 200
        else:
            return jsonify(data="ERROR"), 404
    elif request.method == 'PUT':
        te_verzenden = DataRepository.json_or_formdata(request)
        rfid = te_verzenden['rfid']
        naam = te_verzenden['naam']
        wachtwoord = te_verzenden['wachtwoord']
        answer = DataRepository.update_user(rfid, naam, wachtwoord, UserID)
        if answer is not None:
            return jsonify(data=answer), 201
        else:
            return jsonify(data="ERROR"), 400
    elif request.method == 'DELETE':
        data = DataRepository.remove_user(UserID)
        if data is not None:
            return jsonify(gebruikers=data), 200
        else:
            return jsonify(data="ERROR"), 404


@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # Send to the client!
    socketio.emit('B2F_change_magnet', {
        'status': magnet_status}, broadcast=True)
    time.sleep(0.1)


@socketio.on('F2B_openBox')
def open_box():
    print('Box opened via PC')
    # Add change to database
    answer = DataRepository.insert_rfid_value(0, "Lock geopend")
    answer = DataRepository.insert_box_site(1, "Lock geopend")
    print(answer)
    # Send to the client!
    socketio.emit('B2F_change_magnet', {'status': answer}, broadcast=True)
    socketio.emit('B2F_refresh_history', broadcast=True)
    time.sleep(0.1)


@socketio.on('F2B_closeBox')
def open_box():
    print('Box closed via PC')
    # Add change to database
    answer = DataRepository.insert_rfid_value(1, "Lock gesloten")
    answer = DataRepository.insert_box_site(1, "Lock gesloten")
    print(answer)
    # Send to the client!
    socketio.emit('B2F_change_magnet', {'status': answer}, broadcast=True)
    socketio.emit('B2F_refresh_history', broadcast=True)
    time.sleep(0.1)


@socketio.on('F2B_name4rfid')
def write_to_rfid():
    global register_rfid
    try:
        time.sleep(0.1)
        register_rfid = True
    finally:
        play()
        time.sleep(0.1)

# START een thread op. Belangrijk!!! Debugging moet UIT staan op start van de server, anders start de thread dubbel op
# werk enkel met de packages gevent en gevent-websocket.


def buzz(noteFreq, duration):
    halveWaveTime = 1 / (noteFreq * 2)
    waves = int(duration * noteFreq)
    for i in range(waves):
        GPIO.output(buzzerPin, True)
        time.sleep(halveWaveTime)
        GPIO.output(buzzerPin, False)
        time.sleep(halveWaveTime)


def play():
    t = 0
    notes = [262]
    duration = [2]
    for n in notes:
        buzz(n, duration[t])
        time.sleep(duration[t] * 0.1)
        t += 1
#buzz(262, 0.5)


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
            answer = DataRepository.insert_lid(magnet_status, beschrijving)
            print(f"New magnet value: {answer}")
            socketio.emit('B2F_change_magnet', {
                          'status': magnet_status}, broadcast=True)
            socketio.emit('B2F_refresh_history', broadcast=True)
        prev_magnet_status = magnet_status
        time.sleep(0.5)


def read_rfid():
    global lock_opened
    global register_rfid
    while True:
        id, text = reader.read()
        if id != "":
            print("ID: %s\nText: %s" % (id, text))
            rfid_id = id
            if register_rfid == False:
                lock_opened = not lock_opened
                if lock_opened == True:
                    beschrijving = f"{text} Unlocked your mailbox"
                else:
                    beschrijving = f"{text} Locked your mailbox"
                answer = DataRepository.insert_rfid_value(id, beschrijving)
                answer = DataRepository.insert_box_scanner(id, beschrijving)
                socketio.emit('B2F_refresh_history', broadcast=True)
                time.sleep(0.5)
            else:
                socketio.emit('B2F_rfidwritten', {'rfid': rfid_id})
                register_rfid = False
            time.sleep(1)
            id = ""


def wait_for_button():
    btnPin.on_press(lees_knop)
    time.sleep(0.1)


def read_ldr():
    global led_strip_ldr
    while True:
        ldr1 = spiObj.read_channel(0b1)
        ldr2 = spiObj.read_channel(2)
        ldr3 = spiObj.read_channel(4)
        ldr4 = spiObj.read_channel(8)
        ldr5 = spiObj.read_channel(16)
        if ldr1 > 75 or ldr2 > 75 or ldr3 > 75 or ldr4 > 75 or ldr5 > 75:
            print("Brief ontvangen")
            answer = DataRepository.insert_ldr_values(
                ldr1, ldr2, ldr3, ldr4, ldr5)
            answer = DataRepository.add_letter()
        ldr6 = spiObj.read_channel(32)
        if ldr6 > 850:
            led_strip_ldr = True
        else:
            led_strip_ldr = False
        time.sleep(0.5)


def start_thread_magnet():
    thread = threading.Thread(target=read_sensor_magnet, args=(), daemon=True)
    thread.start()


def start_thread_rfid():
    thread2 = threading.Thread(target=read_rfid, args=(), daemon=True)
    thread2.start()


def start_thread_button():
    thread3 = threading.Thread(target=wait_for_button, args=(), daemon=True)
    thread3.start()


def start_thread_read_ldr():
    thread4 = threading.Thread(target=read_ldr, args=(), daemon=True)
    thread4.start()


def start_threads():
    print("**** Starting THREADS ****")
    start_thread_magnet()
    start_thread_rfid()
    start_thread_button()
    # start_thread_read_ldr()


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
        time.sleep(0.1)


def start_chrome_thread():
    print("**** Starting CHROME ****")
    chromeThread = threading.Thread(
        target=start_chrome_kiosk, args=(), daemon=True)
    chromeThread.start()


# ANDERE FUNCTIES

if __name__ == '__main__':
    try:
        setup_gpio()
        start_threads()
        start_chrome_thread()
        print("**** Starting APP ****")
        socketio.run(app, debug=False, host='0.0.0.0')
    except KeyboardInterrupt:
        print('KeyboardInterrupt exception is caught')
    finally:
        GPIO.cleanup()
