import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 1)
spi.max_speed_hz = 10 ** 5

ldr = 0b1


def to_volt(waarde):
    voltage = round((waarde / 1023) * 3.3, 2)
    return voltage


def to_percent(waarde):
    waarde = 1023 - waarde
    percentage = round((waarde / 1023) * 100, 1)
    return percentage


try:
    while True:
        bytes_out = [0b1, (8 | ldr) << 4, 0b0]
        bytes_in = spi.xfer(bytes_out)
        # Mijn methode: Omslachtig
        # waarde_byte1 = bytes_in[2]
        # waarde_byte2 = bytes_in[1]
        # waarde_byte2 = waarde_byte2 & 0b11
        # waarde_byte2 = waarde_byte2 << 8
        # waarde_pot = waarde_byte1 | waarde_byte2

        # methode geert:
        # LDR BEREKENEN
        data_ldr = ((bytes_in[1] & 3) << 8) | bytes_in[2]
        print(data_ldr)

        # POT BEREKENEN
        bytes_out = [0b1, (0b1 << 7), 0b0]
        bytes_in = spi.xfer(bytes_out)
        data_pot = ((bytes_in[1] & 3) << 8) | bytes_in[2]
        print(data_pot)
        time.sleep(1)
except KeyboardInterrupt as ex:
    print(ex)
finally:
    spi.close()
    print('Stopped...')
