import time
from RPi import GPIO

btn = 19
btn2 = 13
btn3 = 6


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(btn, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(btn2, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(btn3, GPIO.IN, GPIO.PUD_UP)


setup()
try:
    while True:
        knop_status = GPIO.input(btn)
        knop_status2 = GPIO.input(btn2)
        knop_status3 = GPIO.input(btn3)
        print("De status van de knop is: {0}".format(knop_status))
        print("De status van de knop 2 is: {0}".format(knop_status2))
        print("De status van de knop 3 is: {0}".format(knop_status3))
        time.sleep(1)
except KeyboardInterrupt as ex:
    print(ex)
finally:
    print('Stopped...')
    GPIO.cleanup()
