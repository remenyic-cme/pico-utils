import machine
import utime


class Motor:
    def __init__(self, enable=None, in1=None, in2=None):
        assert isinstance(enable, int), "Expected ENABLE to be of type integer but received {} of type {}".format(
            "'" + str(enable) + "'", str(type(enable)))
        assert isinstance(in1, int), "Expected IN1 to be of type integer but received {} of type {}".format(
            "'" + str(in1) + "'", str(type(in1)))
        assert isinstance(in2, int), "Expected IN2 to be of type integer but received {} of type {}".format(
            "'" + str(in2) + "'", str(type(in2)))

        pin_pwm = machine.Pin(enable, machine.Pin.OUT)
        self.pwm = machine.PWM(pin_pwm)
        self.pin_fwd = machine.Pin(in1, machine.Pin.OUT)
        self.pin_bck = machine.Pin(in2, machine.Pin.OUT)
        self.pwm.freq(50)
        self._duty = 0
        self.pwm.duty_u16(self._duty)

    def forward(self):
        self.pin_fwd.high()
        self.pin_bck.low()

    def backward(self):
        self.pin_fwd.low()
        self.pin_bck.high()

    def __update_duty(self):
        self.pwm.duty_u16(self._duty)

    @property
    def duty(self):
        return self._duty

    @duty.setter
    def duty(self, value):
        self._duty = value
        if self._duty < 0:
            self._duty = 0
        self.__update_duty()


class SonicSensor:
    def __init__(self, pin_trigger=None, pin_echo=None):
        assert isinstance(pin_trigger, int), "Expected pin_trigger to be int but received {}".format(
            str(type(pin_trigger)))
        assert isinstance(pin_echo, int), "Expected pin_echo to be int but received {}".format(str(type(pin_echo)))
        self.trigger = machine.Pin(pin_trigger, machine.Pin.OUT)
        self.echo = machine.Pin(pin_echo, machine.Pin.IN)

    def __call__(self):
        self.trigger.low()
        utime.sleep_us(5)
        self.trigger.high()
        utime.sleep_us(10)
        self.trigger.low()
        signal_off = 0
        signal_on = 0
        while self.echo.value() == 0:
            signal_off = utime.ticks_us()
        while self.echo.value() == 1:
            signal_on = utime.ticks_us()
        time_passed = signal_on - signal_off
        distance = (time_passed * 0.0343) / 2
        return distance


def time_it(func):
    def wrapper(*args, **kwargs):
        time_start = utime.ticks_ms()
        result = func(*args, **kwargs)
        time_stop = utime.ticks_ms()
        time_took = round((time_stop - time_start) / 1000, 3)
        print(func.__name__, "executed in {} seconds.".format(time_took))
        return result

    return wrapper


import machine
import utime


class SonicSensor2:
    def __init__(self, trigger=None, echo=None):
        """
        SonicSensor class is used to quickly instantiate a sonic sensor
        and have access to multiple built-in functionalities

        :param trigger: integer, must be positive, this is the pin.OUT on your pico
        :param echo: integer, must be positive, this is the pin.IN on your pico
        """

        assert isinstance(trigger, int), "Expected trigger to be int but received {}".format(str(type(trigger)))
        assert isinstance(echo, int), "Expected echo to be int but received {}".format(str(type(echo)))
        self._trigger = machine.Pin(trigger, machine.Pin.OUT)
        self._trigger.value(0)
        self._echo = machine.Pin(echo, machine.Pin.IN)

    def _send_pulse(self):
        """
        Send a pulse and and find out how many microseconds
        it took to travel the distance 1 way
        """
        self._trigger.low()
        utime.sleep_us(2)
        self._trigger.high()
        utime.sleep_us(5)
        self._trigger.low()
        signal_off = 0
        signal_on = 0
        while self._echo.value() == 0:
            signal_off = utime.ticks_us()
        while self._echo.value() == 1:
            signal_on = utime.ticks_us()
        time_passed = signal_on - signal_off
        distance = (time_passed * 0.0343) / 2
        return distance

    @property
    def dist_cm(self):
        """
        This attr sends a pulsse, gets its readings
        and converts them to cm/s using the bellow formula

        distance = pulse duration / 29.1

        Explanation:
            the sound speed on air (343.2 m/s), that It's equivalent to
            0.034320 cm/us that is 1cm each 29.1us


        return distance
        """
        return round(self._send_pulse(), 2)


