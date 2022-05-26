import time
from RPi import GPIO
from smbus import SMBus
import datetime


class LCD_Module:

    # I2C obj aanmaken
    global i2c
    i2c = SMBus()
    i2c.open(1)

    def __init__(self, e_pin, rs_pin) -> None:
        self.e_pin = e_pin
        self.rs_pin = rs_pin
        self.__setup()
        self.__init_LCD()

    # --- GETTERS / SETTERS ---

    # ********** property e_pin - (setter/getter) ***********

    @property
    def e_pin(self):
        """ The e_pin property. """
        return self.__e_pin

    @e_pin.setter
    def e_pin(self, value):
        self.__e_pin = value

    # ********** property rs_pin - (setter/getter) ***********

    @property
    def rs_pin(self):
        """ The rs_pin property. """
        return self.__rs_pin

    @rs_pin.setter
    def rs_pin(self, value):
        self.__rs_pin = value

    # --- SETUP ---
    def __setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.e_pin, GPIO.OUT)
        GPIO.setup(self.rs_pin, GPIO.OUT)
        GPIO.output(self.e_pin, GPIO.HIGH)

    def __init_LCD(self):
        self.send_instruction(0b00111000)  # function set of 0x38
        self.send_instruction(0b00001111)  # display on of 0xf
        self.send_instruction(0b00000001)

    # --- PUBLIC FUNCTIONS ---
    def send_instruction(self, value):
        GPIO.output(self.rs_pin, GPIO.LOW)
        i2c.write_byte(0x38, value)
        GPIO.output(self.e_pin, GPIO.LOW)
        GPIO.output(self.e_pin, GPIO.HIGH)
        time.sleep(0.01)

    # Characters sturen

    def send_character(self, value):
        value = ord(value)
        GPIO.output(self.rs_pin, GPIO.HIGH)
        GPIO.output(self.e_pin, GPIO.HIGH)
        i2c.write_byte(0x38, value)
        GPIO.output(self.e_pin, GPIO.LOW)
        GPIO.output(self.e_pin, GPIO.HIGH)
        time.sleep(0.01)

    # Functie voor bericht te schrijven

    def write_message(self, message):
        self.send_instruction(0b00000001)
        count = 0
        for i in message:
            count += 1
            self.send_character(i)
            if count == 16:
                # VOOR NIEUWE REGEL: 0x40 is de 40tigste hexadecimale waarde van de gewenste blok
                self.send_instruction(0b10000000 | 0x40)

    # Instructies om LCD op te zetten

    def init_LCD(self):
        self.send_instruction(0b00111000)  # function set of 0x38
        self.send_instruction(0b00001111)  # display on of 0xf
        self.send_instruction(0b00000001)  # clear display/cursor home of 0x01

    def write_scrolling(self, message):
        self.send_instruction(0b00000001)
        len_string = len(message)
        message += f" {message}"
        j = 0
        k = 16
        while True:
            self.send_instruction(0x2)
            for i in message[j:k]:
                self.send_character(i)
            j += 1
            k += 1
            if k > len_string + 15:
                j = 0
                k = 16
            time.sleep(0.5)

    @staticmethod
    def close_lcd():
        GPIO.cleanup()
