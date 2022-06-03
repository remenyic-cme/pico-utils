from utils import SonicSensor, Motor, time_it, SonicSensor2
import utime


class Robot:
    MAX_PWM = 65025

    def __init__(self):
        self.motor_left = Motor(enable=2, in1=3, in2=4)
        self.motor_right = Motor(enable=7, in1=5, in2=6)
        self._max_pwm = 65025

        # setting up pwm to 0 for both motor sides
        self.motor_left.duty = 0
        self.motor_right.duty = 0
        self._speed = 0

        # setting up the sensors
        self.sens_right = SonicSensor(pin_echo=13, pin_trigger=12)
        self.sens_front = SonicSensor(pin_echo=11, pin_trigger=10)
        self.sens_left = SonicSensor(pin_echo=9, pin_trigger=8)

        self.GEAR_5 = self._max_pwm
        self.GEAR_4 = self._max_pwm * .8
        self.GEAR_3 = self._max_pwm * .6
        self.GEAR_2 = self._max_pwm * .4
        self.GEAR_1 = self._max_pwm * .3

        self.last_stuck = False

    def min_duty(self):
        return min([self.motor_left.duty, self.motor_right.duty])

    def max_duty(self):
        return max([self.motor_left.duty, self.motor_right.duty])

    @property
    def current_speed(self):
        return self._speed

    @current_speed.setter
    def current_speed(self, value):
        value = int(value)
        self._speed = value
        self.motor_left.duty = value
        self.motor_right.duty = value

    @property
    def sensor_left(self):
        return self.sens_left()

    @property
    def sensor_right(self):
        return self.sens_right()

    @property
    def sensor_front(self):
        return self.sens_front()

    def shift_gear_forward(self):
        if self.current_speed == self.GEAR_5:
            # daca suntem in treapta 5 nu mai incrementam viteza
            return
        if self.current_speed == self.GEAR_1:
            # daca robotul e oprit, creste viteza la GEAR_1
            self.current_speed = self.GEAR_1
            return
        self.current_speed = self.current_speed + self._max_pwm * .2

    def shift_gear_backward(self):
        if self.current_speed == 0:
            # daca suntem in treapta 5 nu mai incrementam viteza
            return
        if self.current_speed == self.GEAR_1:
            # daca robotul e oprit, creste viteza la GEAR_1
            self.current_speed = 0
            return
        self.current_speed = self.current_speed - self._max_pwm * .2

    def forward(self):
        self.motor_left.forward()
        self.motor_right.forward()

    def backward(self):
        self.motor_left.backward()
        self.motor_right.backward()

    def stop(self):
        speed = self.min_duty()
        if self.current_speed == 0:
            return
        while self.max_duty() > 0:
            self.motor_left.duty -= 75
            self.motor_right.duty -= 75
            utime.sleep_us(3)

    def rotate_left(self):
        self.motor_left.backward()
        self.motor_right.forward()

    def rotate_right(self):
        self.motor_left.forward()
        self.motor_right.backward()

    def get_best_direction(self):
        # get best max distance of 5 error-free readings
        left, front, right = [], [], []
        for _ in range(5):
            left.append(self.sensor_left)
            front.append(self.sensor_front)
            right.append(self.sensor_right)
            utime.sleep_ms(2)
        left, front, right = min(left), min(front), min(right)
        if front > 50:
            # priotise front direction as long is over 50cm free space ahead
            return "front", front
        directions = {"left": left, "front": front, "right": right}
        direction = min(directions, key=directions.get)
        return direction, directions[direction]

    def check_all_sensors(self):
        if self.sensor_front > 2200 and self.sensor_left > 2200 and self.sensor_right > 2200:
            return True

    def check_stuck(self):
        stuck = self.check_all_sensors()
        if stuck and self.last_stuck:
            self.backward()
            self.duty = self.GEAR_1
            utime.sleep_ms(150)
            self.last_stuck = False
        else:
            self.last_stuck = True


def self_drive(seconds=0):
    robot = Robot()
    start_time = utime.time()
    end_time = 0
    max_readings = []

    while (end_time - start_time) < seconds:
        direction, distance = robot.get_best_direction()
        if distance > 30:
            print(direction, distance)
            if direction == "front":
                robot.forward()
            elif direction == "left":
                # slow down to GEAR_1 to rotate slowly
                while robot.current_speed > robot.GEAR_1:
                    robot.shift_gear_backward()
                    utime.sleep_ms(1)
                robot.rotate_left()
                utime.sleep_ms(15)
            elif direction == "right":
                # slow down to GEAR_1 to rotate slowly
                while robot.current_speed > robot.GEAR_1:
                    robot.shift_gear_backward()
                    utime.sleep_ms(1)
                robot.rotate_right()
                utime.sleep_ms(15)
            robot.shift_gear_forward()
        else:
            print("no space to go forward")
            robot.rotate_right()
            robot.current_speed = robot.GEAR_1
            utime.sleep_ms(50)
        end_time = utime.time()
    robot.stop()


@time_it
def main():
    robot = Robot()
    robot.forward()
    robot.current_speed = robot.GEAR_1
    utime.sleep(2)
    robot.current_speed = robot.GEAR_3
    utime.sleep(2)
    robot.rotate_left()
    utime.sleep(2)
    robot.stop()

