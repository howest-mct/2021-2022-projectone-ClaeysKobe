from selenium import webdriver
from mfrc522 import SimpleMFRC522
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, send
from flask_cors import CORS
import netifaces as ni
import threading
import os
from datetime import datetime
from classes.spi_class import SpiClass
from classes.lcd_class import LCD_Module
from helpers.klasseknop import Button
import time
from RPi import GPIO
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity


# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options


buzzerPin = 23
magnetPin = 17
transistorPin = 27
btnPin = Button(21)
shutdownBtnPin = Button(5)

# Default variables
magnet_status = 0
prev_magnet_status = 0
laatst_geledigd = datetime.now()
lock_opened = False
register_rfid = False
login_rfid = False
led_strip_ldr = False
led_strip_lock = False
led_waarde = False
prev_led_waarde = False
brieven_vandaag = f""
try:
    ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
except Exception:
    ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
# Code voor Hardware


def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(buzzerPin, GPIO.OUT)
    GPIO.setup(transistorPin, GPIO.OUT)
    GPIO.setup(magnetPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # magnet pin
    global magnet_status
    global prev_magnet_status
    magnet_status = GPIO.input(magnetPin)
    prev_magnet_status = GPIO.input(magnetPin)
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
    # lock status
    global lock_opened
    answer = DataRepository.read_latest_lock()
    if answer is not None:
        answer = answer['waarde']
        if answer == 1:
            lock_opened = True
        else:
            lock_opened = False
    else:
        lock_opened = False


def lees_shutdown_knop(pin):
    if shutdownBtnPin.pressed:
        print("**** button pressed: shutting down PI ****")
        time.sleep(5)
        os.system("sudo shutdown -h now")


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
app.config['JWT_SECRET_KEY'] = 'Secret!12345698790! loijsfmlqkjs'
jwt = JWTManager(app)

CORS(app)


@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(e)


# API ENDPOINTS
endpoint = '/api/v1'


@app.route('/')
def hallo():
    return "Server is running."


@app.route(endpoint + '/login/', methods=['POST'])
def login():
    gegevens = DataRepository.json_or_formdata(request)

    print(gegevens)
    username = gegevens['username']
    password = gegevens['password']

    if not username:
        return jsonify(message="missing parameter!"), 400
    if not password:
        return jsonify(message="missing parameter!"), 400

    answer = DataRepository.check_gebruiker(username, password)
    if answer is not None:
        print("succesvol ingelogd")
        # expires = datetime.timedelta(seconds=10)  expires_delta=expires
        access_token = create_access_token(
            identity=username)

        print(access_token)
        return jsonify(message="This is a public endpoint to generate a token", access_token=access_token), 200
    else:
        return jsonify(message="Username and/or password are incorrect"), 401


@app.route(endpoint + '/protected/', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(message="This is a protected endpoint: ", logged_in_as=current_user), 200


@app.route(endpoint + '/events/today/', methods=['GET'])
def sens_today():
    if request.method == 'GET':
        data = DataRepository.read_sensor_gesch_today()
        if data is not None:
            return jsonify(sensors=data), 200
        else:
            return jsonify(data="ERROR"), 404


@app.route(endpoint + '/events/', methods=['GET', 'DELETE'])
def sensors():
    if request.method == 'GET':
        data = DataRepository.read_sensor_gesch()
        if data is not None:
            return jsonify(sensors=data), 200
        else:
            return jsonify(data="ERROR"), 404
    if request.method == 'DELETE':
        data = DataRepository.truncate_events()
        if data is not None:
            return jsonify(answer="succes"), 202
        else:
            return jsonify(answer="ERROR"), 400


@app.route(endpoint + '/events/lid/', methods=['GET'])
def sensors_lid():
    if request.method == 'GET':
        data = DataRepository.read_latest_lid()
        if data is not None:
            return jsonify(status=data), 200
        else:
            return jsonify(data="ERROR"), 404


@app.route(endpoint + '/events/letters/', methods=['GET'])
def sensors_letters():
    if request.method == 'GET':
        data = DataRepository.read_brieven_today()
        if data is not None:
            return jsonify(letters=data), 200
        else:
            return jsonify(data="ERROR"), 404


@app.route(endpoint + '/events/letters/count/', methods=['GET'])
def get_latest_letter_count():
    if request.method == 'GET':
        data = DataRepository.get_latest_letters(laatst_geledigd)
        if data is not None:
            return jsonify(letters=data), 200
        else:
            return jsonify(data="geen"), 200


@app.route(endpoint + '/events/letters/latest/', methods=['GET'])
def latest_letters():
    if request.method == 'GET':
        data = DataRepository.read_latest_letter()
        if data is not None:
            return jsonify(data=data), 200
        else:
            return jsonify(data="--"), 200


@app.route(endpoint + '/events/lock/latest/', methods=['GET'])
def latest_lock():
    if request.method == 'GET':
        data = DataRepository.read_latest_lock()
        if data is not None:
            return jsonify(data=data), 200
        else:
            return jsonify(data="--"), 200


@app.route(endpoint + '/users/', methods=['GET', 'POST'])
def gebruikers():
    if request.method == 'GET':
        data = DataRepository.read_users()
        for gebruiker in data:
            wachtwoord = gebruiker['wachtwoord']
            if wachtwoord is not None:
                wachtwoord = str(wachtwoord, 'utf-8')
                gebruiker['wachtwoord'] = wachtwoord
            else:
                gebruiker['wachtwoord'] = 'onbekend'
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
        wachtwoord = data['wachtwoord']
        if wachtwoord is not None:
            wachtwoord = str(wachtwoord, 'utf-8')
            data['wachtwoord'] = wachtwoord
        else:
            data['wachtwoord'] = 'onbekend'
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
    time.sleep(0.1)


@socketio.on('F2B_openBox')
def open_box():
    global lock_opened
    global led_strip_lock
    print('Box opened via PC')
    # Add change to database
    answer = DataRepository.insert_rfid_value(0, "Lock geopend")
    answer = DataRepository.insert_box_site(1, "Lock geopend")
    print(answer)
    # Send to the client!
    lock_opened = True
    led_strip_lock = True
    socketio.emit('B2F_refresh_history', broadcast=True)
    socketio.emit('B2F_emptyd_letters', broadcast=True)
    time.sleep(0.1)


@socketio.on('F2B_closeBox')
def open_box():
    global lock_opened
    global led_strip_lock
    print('Box closed via PC')
    # Add change to database
    answer = DataRepository.insert_rfid_value(1, "Lock gesloten")
    answer = DataRepository.insert_box_site(1, "Lock gesloten")
    print(answer)
    # Send to the client!
    lock_opened = False
    led_strip_lock = False
    socketio.emit('B2F_refresh_history', broadcast=True)
    time.sleep(0.1)


@socketio.on('F2B_waitingForLogin')
def login_via_rfid():
    global login_rfid
    login_rfid = True


@socketio.on('F2B_waitingForRegister')
def register_rfid_set():
    global register_rfid
    register_rfid = True

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
                led_strip_lock == True
            else:
                beschrijving = "brievenbusklep geopend"
                led_strip_lock == False
            answer = DataRepository.insert_magnet_value(
                magnet_status, beschrijving)
            answer = DataRepository.insert_lid(magnet_status, beschrijving)
            print(f"New magnet value: {answer}")
            socketio.emit('B2F_change_magnet', broadcast=True)
            socketio.emit('B2F_refresh_history', broadcast=True)
        prev_magnet_status = magnet_status
        time.sleep(0.5)


def read_rfid():
    global lock_opened
    global register_rfid
    global login_rfid
    global laatst_geledigd
    while True:
        id, text = reader.read()
        if id != "":
            print("ID: %s\nText: %s" % (id, text))
            rfid_id = id
            print(register_rfid)
            if register_rfid == False:
                gebruiker = DataRepository.check_rfid(rfid_id)
                if gebruiker is not None:
                    gebruiker = gebruiker['naam']
                    lock_opened = not lock_opened
                    print(login_rfid)
                    if login_rfid == True:
                        socketio.emit('B2F_loginPermitted')
                        login_rfid = False
                    else:
                        if lock_opened == True:
                            beschrijving = f"{gebruiker} Unlocked your mailbox"
                            print(beschrijving)
                            laatst_geledigd = datetime.now()
                            socketio.emit('B2F_emptyd_letters', broadcast=True)
                        else:
                            beschrijving = f"{gebruiker} Locked your mailbox"
                            print(beschrijving)
                        answer = DataRepository.insert_rfid_value(
                            id, beschrijving)
                        answer = DataRepository.insert_box_scanner(
                            id, beschrijving, lock_opened)
                        socketio.emit('B2F_changed_lock', {
                            "lock_status": lock_opened}, broadcast=True)
                        socketio.emit('B2F_refresh_history', broadcast=True)
                else:
                    print("Ongeregistreede gebruiker probeerde in te loggen")
                time.sleep(0.5)
            else:
                socketio.emit('B2F_rfidwritten', {'rfid': rfid_id})
                register_rfid = False
            time.sleep(1)
            id = ""


def wait_for_button():
    btnPin.on_press(lees_knop)
    shutdownBtnPin.on_press(lees_shutdown_knop)
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
            show_brieven_vandaag()
            socketio.emit('B2F_new_letter', broadcast=True)
        ldr6 = spiObj.read_channel(32)
        if ldr6 > 850:
            led_strip_ldr = True
        else:
            led_strip_ldr = False
        time.sleep(0.5)


def change_led():
    global prev_led_waarde
    if led_strip_ldr == True and led_strip_lock == True:
        led_waarde = True
        GPIO.output(transistorPin, GPIO.HIGH)
        DataRepository.insert_led(1)
    else:
        led_waarde = False
        GPIO.output(transistorPin, GPIO.LOW)
        if prev_led_waarde != led_waarde:
            DataRepository.insert_led(0)
    prev_led_waarde = led_waarde
    time.sleep(1)


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


def start_thread_led():
    thread5 = threading.Thread(target=change_led, args=(), daemon=True)
    thread5.start()


def start_threads():
    print("**** Starting THREADS ****")
    start_thread_magnet()
    start_thread_rfid()
    start_thread_button()
    # start_thread_read_ldr()
    start_thread_led()


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
