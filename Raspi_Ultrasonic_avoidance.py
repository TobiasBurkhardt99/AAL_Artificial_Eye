# connection of 3 sensors to RasPi https://i.imgur.com/GcZRI8S.jpg
import RPi.GPIO as GPIO
import time
#import gpiozero
# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Set pins for the left sensor
TRIG_LEFT = 24  # Update with your GPIO pin number
ECHO_LEFT = 23  # Update with your GPIO pin number

# Set pins for the right sensor
TRIG_RIGHT = 27  # Update with your GPIO pin number
ECHO_RIGHT = 22  # Update with your GPIO pin number

# Set up GPIO direction (IN / OUT)
GPIO.setup(TRIG_LEFT, GPIO.OUT)
GPIO.setup(ECHO_LEFT, GPIO.IN)
GPIO.setup(TRIG_RIGHT, GPIO.OUT)
GPIO.setup(ECHO_RIGHT, GPIO.IN)

def get_distance(trig, echo):
    # Set the trigger to High
    GPIO.output(trig, True)

    # Set the trigger after 0.01ms to Low
    time.sleep(0.00001)
    GPIO.output(trig, False)

    StartTime = time.time()
    StopTime = time.time()

    # Save StartTime
    while GPIO.input(echo) == 0:
        StartTime = time.time()

    # Save time of arrival
    while GPIO.input(echo) == 1:
        StopTime = time.time()

    # Time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # Multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance

try:
    while True:
        distance_left = get_distance(TRIG_LEFT, ECHO_LEFT)
        print("Distance left:"+str(distance_left))
        distance_right = get_distance(TRIG_RIGHT, ECHO_RIGHT)
        print("Distance right:"+str(distance_right))

        if distance_left < 50.0:
            print("Go right")
        elif distance_right < 50.0:
            print("Go left")

        # Delay for a bit before the next check
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()

## other method

# from gpiozero import DistanceSensor
# ultrasonic = DistanceSensor(echo=17, trigger=4)
# while True:
#     print(ultrasonic.distance)