import time
import network
import machine
from machine import (
    DEEPSLEEP,
    RTC,
    ADC,
    Pin
)
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

    def notify(self):
        # TODO:
        print("Sender: %s\nMessage: %s" % (self.sender, self.message))


class Service(object):
    """
    Web service to manage the device
    """
    def __init__(self, *args, **kwargs):
        self.pin = Pin(2, Pin.OUT)
        super(Service, self).__init__(*args, **kwargs)

    def _toggle(pin):
        pin.value(not pin.value())

    def get_sensor_data():
        """
        returns Report
        """
        adc = ADC(0)
        data = {
            "message": adc.read(),
            # "sender": Report.SENSOR
            "sender": "sensor",
        }
        return Report(**data)

    def get_battery_status():
        """
        returns: Report
        """
        return Report()

    def connect_ap(sta_if):
        """
        Connects to the AP
        Returns boolean of the connection attempt.
        """
        sta_if.connect(
            CONFIG['wifi']['essid'],
            CONFIG['wifi']['password'])

    def led_status(self):
        """
        Report status using the built-in led from the NodeMCU
            - 250ms Connecting
            - 1000ms high /5000ms low Connected
        """
        connected = sta_if.is_connected()
        time.sleep_ms(CONFIG['wifi']['status'][connected])
        self._toggle(self.pin)

    def deepsleep(self, rtc, milliseconds):
        # configure RTC.ALARM0 to be able to wake the device
        rtc.irq(trigger=rtc.ALARM0, wake=DEEPSLEEP)

        # set RTC.ALARM0 to fire after the given seconds (waking the device)
        rtc.alarm(rtc.ALARM0, milliseconds)

        # put the device to sleep
        machine.deepsleep()

    def sleep(self, milliseconds):
        # put the device to sleep but keeping wlan working.
        machine.deepsleep(milliseconds)


if __name__ == '__main__':
    rtc = RTC()

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    debug = CONFIG['debug']
    service = Service()

    connected = False
    while not connected:
        service.connect_ap(sta_if)
        connected = sta_if.is_connected()

        service.led_status()
        service.sleep(CONFIG['sleep']['not_connected'])

    while connected:
        report = service.get_sensor_data()
        report.notify()
    else:
        while True:
            if debug:
                print("Connected!")

            # report = service.get_sensor_data()
            # report.notify()

            print('getting status')
            service.status()
            time.sleep_ms(CONFIG['sleep']['connected'])
