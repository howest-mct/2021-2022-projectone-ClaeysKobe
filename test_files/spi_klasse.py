import spidev


class SpiClass:

    def __init__(self, bus=0, device=0) -> None:
        self.__bus = bus
        self.__device = device

    def read_channel(self, channel):
        # Open Device
        spi = spidev.SpiDev()
        spi.open(self.__bus, self.__device)
        spi.max_speed_hz = 10 ** 5
        # Lees uit
        bytes_out = [0b1, (8 | channel) << 4, 0b0]
        bytes_in = spi.xfer(bytes_out)
        data = ((bytes_in[1] & 3) << 8) | bytes_in[2]
        return data

    @staticmethod
    def closespi():
        spi = spidev.SpiDev()
        spi.close()
        print("Spi Closed")
