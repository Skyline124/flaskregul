#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import math

buttonPin = 26                      # define the buttonPin
motorPins = (18, 23, 24, 25)        # define pins connected to four phase ABCD of stepper motor
CCWStep = (0x01, 0x02, 0x04, 0x08)  # define power supply order for coil for rotating anticlockwise
CWStep = (0x08, 0x04, 0x02, 0x01)   # define power supply order for coil for rotating clockwise

# define the range of steps for the motor to realize
# maximum command to the boiler
NB_STEPS_RANGE = 360

# min delay between demanded steps on the motor (milliseconds)
MIN_DELAY = 20

# ## ------------------------ ## #
# ## --       LIBRARY      -- ## #
# ## ------------------------ ## #


def setup():
    ''' Setup function '''
    print('Motor program starting...')
    GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
    for pin in motorPins:
        GPIO.setup(pin, GPIO.OUT)


def moveOnePeriod(direction, ms):
    ''' As for four phase stepping motor,
        four steps is a cycle. the function is used to drive
        the stepping motor clockwise or anticlockwise to take four steps
    '''
    for j in range(0, 4, 1):      # cycle for power supply order
        for i in range(0, 4, 1):  # assign to each pin, a total of 4 pins
            if (direction == 1):  # power supply order clockwise
                GPIO.output(motorPins[i], ((CCWStep[j] == 1 << i) and GPIO.HIGH or GPIO.LOW))
            else:                # power supply order anticlockwise
                GPIO.output(motorPins[i], ((CWStep[j] == 1 << i) and GPIO.HIGH or GPIO.LOW))
        if(ms < MIN_DELAY):       # the delay can not be less than 3ms, otherwise it will exceed speed limit of the motor
            ms = MIN_DELAY
        time.sleep(ms * 0.001)


def moveSteps(direction, ms, steps):
    ''' Continuous rotation function, the parameter steps specifies
        the rotation cycles, every four steps is a cycle
    '''
    for i in range(steps):
        moveOnePeriod(direction, ms)


def motorStop():
    ''' function used to stop rotating '''
    for i in range(0, 4, 1):
        GPIO.output(motorPins[i], GPIO.LOW)


# ## ------------------------ ## #
# ## --        PERSO       -- ## #
# ## ------------------------ ## #

def initPosition():
    ''' Initialisation function to get the position 0 of the boiler
    '''
    # Motor setup
    setup()

    # Button of zero position setup
    # Set buttonPin's mode is input, and pull up to high level(3.3V)
    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    print('looking for the zero position...')
    steps = 0
    # 512 steps is a total circle rotation
    while steps < 512:
        moveSteps(1, MIN_DELAY, 1)
        steps = steps + 1
        if GPIO.input(buttonPin) == GPIO.LOW:
            print("found the init point ! (step = " + str(steps) + ")")
            motorStop()
            return "OK"

    motorStop()
    print("couldn't find init position")
    return "NOK: couldn't find zero position of the motor"


def setPercentage(currentPercentage, percentage):
    """ function to realize the percentage of the maximum possible
        value of the boiler power
    """
    StepsToRealize = math.floor((percentage - currentPercentage) / 100 * NB_STEPS_RANGE)
    if StepsToRealize > 0:
        moveSteps(0, MIN_DELAY, StepsToRealize)
        motorStop()
        return percentage
    elif StepsToRealize < 0:
        moveSteps(1, MIN_DELAY, -StepsToRealize)
        motorStop()
        return percentage
    else:
        return percentage


def clean():
    GPIO.cleanup()
    print("cleanedup!")


if __name__ == '__main__':
    # Initialization of the zero position
    initPosition()
    currentPercentage = 0

    while True:
        strPercentage = input('Give me a percentage to realize:')
        try:
            percentage = int(strPercentage)
            if percentage < 0:
                percentage = 0
            if percentage > 100:
                percentage = 100
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            continue

        currentPercentage = setPercentage(currentPercentage, percentage)
        print("currentPercentage = " + str(currentPercentage))


