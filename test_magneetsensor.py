import time
from RPi import GPIO

btn = 26


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(btn, GPIO.IN, GPIO.PUD_UP)


setup()
try:
    while True:
        knop_status = GPIO.input(btn)
        print("De status van de knop is: {0}".format(knop_status))
        time.sleep(1)
except KeyboardInterrupt as ex:
    print(ex)
finally:
    print('Stopped...')
    GPIO.cleanup()
