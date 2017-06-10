import time
import network
import urequests
from machine import (
    DEEPSLEEP,
    RTC,
    ADC,
    Pin
)
import machine
from config import CONFIG


class Report(object):
    """
    Report to be given to another service
    """
    sender = ''
    message = ''

    def __init__(self, sender=None, message=None, *args, **kwargs):
        self.sender = sender
        self.message = message
        super(Report, self).__init__(*args, **kwargs)

    def notify(self, is_connected):
        print("Sender: %s\nMessage: %s" % (self.sender, self.message))
        if self.sender == 'sensor' and is_connected:
            url = '%s%s' % (CONFIG['thingspeak_url'], self.message)
            result = urequests.get(url)
            print(result.text)


class Service(object):
    """
    Web service to manage the device
    """
    PINOUT = {
        'D0': 16,
        'D1': 5,
        'D2': 4,
        'D3': 0,
        'D4': 2,
        'D5': 14,
        'D6': 12,
        'D7': 13,
        'D8': 15,
        'D9': 3,
        'D10': 1,
    }

    def __init__(self, *args, **kwargs):
        self.pin = Pin(self.PINOUT['D4'], Pin.OUT)
        self.adc = ADC(0)
        self.sta_if = network.WLAN(network.STA_IF)
        self.sta_if.active(True)
        super(Service, self).__init__(*args, **kwargs)

    def _toggle(self):
        self.pin.value(not self.pin.value())

    def is_connected(self):
        return self.sta_if.isconnected()

    def get_sensor_data(self):
        """
        returns Report
        """
        data = {
            "message": self.adc.read(),
            "sender": "sensor",
        }
        return Report(**data)

    def get_battery_status(self):
        """
        returns: Report
        """
        return Report()

    def connect(self):
        """
        Connects to the AP
        Returns boolean of the connection attempt.
        """
        self.sta_if.connect(
            CONFIG['wifi']['essid'],
            CONFIG['wifi']['password'])

        return self.is_connected()

    def is_connected(self):
        return self.sta_if.isconnected()

    def status(self):
        """
        Report status using the built-in led from the NodeMCU
            - Fast blink: Connecting
            - Slow blink: Connected
        """
        connected = self.is_connected()
        self._toggle()
        time.sleep_ms(CONFIG['wifi']['status'][connected])

    def get_information(self):
        return {
            'is_connected': self.is_connected(),
            'ifconfig': self.sta_if.ifconfig()
        }

    def deepsleep(self, rtc, milliseconds):
        # configure RTC.ALARM0 to be able to wake the device
        rtc.irq(trigger=rtc.ALARM0, wake=DEEPSLEEP)

        # set RTC.ALARM0 to fire after the given seconds (waking the device)
        rtc.alarm(rtc.ALARM0, milliseconds)

        # put the device to sleep
        machine.deepsleep()


if __name__ == '__main__':
    rtc = RTC()
    debug = CONFIG['debug']
    service = Service()
    connected = service.connect()

    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        print('woke from a deep sleep')
    else:
        print('power on or hard reset')

    while service.is_connected is False:
        print("NOT Connected!")
        service.led_status()
        connected = service.connect()
        if not connected:
            time.sleep_ms(CONFIG['sleep']['not_connected'])

    else:
        while True:
            if debug:
                print("Connected!")

            report = service.get_sensor_data()
            report.notify(service.is_connected())

            print('getting status')
            service.status()
            time.sleep_ms(CONFIG['sleep']['connected'])

            print('going to deepsleep')
            service.deepsleep(rtc, CONFIG['sleep']['connected'])
