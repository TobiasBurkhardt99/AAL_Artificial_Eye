import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# The selected pins
trigger = 24
echo    = 23

# Pause between the individual measurements in seconds
sleeptime = 3

GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.output(trigger, False)

try:
    while True:
        # Distance measurement by using the 10us long trigger signal
        GPIO.output(trigger, True)
        time.sleep(0.00001)
        GPIO.output(trigger, False)
        # The stopwatch is started here
        onTime = time.time()
        while GPIO.input(echo) == 0:
            onTime = time.time() 
        while GPIO.input(echo) == 1:
            offTime = time.time() 
        # The difference between the two times gives the duration we are looking for
        duration = offTime - onTime
        # Calculate distance based on speed of sound
        distance = (duration * 34300) / 2
        # Checking whether measured value is within the permissible distance
        if distance < 2 or (round(distance) > 450):
            # If not, an error message is output
            print("Distance outside the measuring range")
            print("------------------------------")
        else:
            # The distance is formatted to two decimal places
            distance = format(distance, '.2f')
            # The calculated distance is output to the console
            print("Distance: "+ str(distance))
            print("------------------------------")
        # Pause between the individual measurements
        time.sleep(sleeptime)

# Clean up after the program is finished
except KeyboardInterrupt:
    GPIO.cleanup()
