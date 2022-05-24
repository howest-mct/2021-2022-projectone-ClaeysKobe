from spi_klasse import SpiClass
import time

spiObj = SpiClass(0, 0)

brief_gevallen = False


def check_waarde():
    global brief_gevallen
    ldr = spiObj.read_channel(0)
    print(f"LDR: {ldr}")
    if ldr > 100:
        brief_gevallen = True
        ldr = spiObj.read_channel(0)
    else:
        brief_gevallen = False


try:
    while True:
        check_waarde()
        print(brief_gevallen)
        time.sleep(1)
except KeyboardInterrupt as ex:
    print(ex)
finally:
    spiObj.closespi()
    print('Stopped...')
