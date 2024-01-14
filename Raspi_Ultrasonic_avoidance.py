from statistics import mean
import RPi.GPIO as GPIO
import time
from pydub import AudioSegment
from pydub.generators import Sine
import simpleaudio as sa

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Set pins for the sensors
TRIG_LEFT = 24
ECHO_LEFT = 23
TRIG_RIGHT = 27
ECHO_RIGHT = 22

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



def play_beep(frequency, balance):
    # Generate a sine wave tone
    tone = Sine(frequency).to_audio_segment(duration=100)

    # Adjust balance
    # Balance -1.0 is full left, 1.0 is full right
    pan = balance
    tone = tone.pan(pan)

    # Play the tone
    play_obj = sa.play_buffer(tone.raw_data, num_channels=2, bytes_per_sample=tone.sample_width, sample_rate=tone.frame_rate)

    return play_obj

# start of Main
# initialise variables
c_l = (TRIG_LEFT, ECHO_LEFT)
b_l = c_l
a_l =c_l

c_r = (TRIG_RIGHT, ECHO_RIGHT)
b_r = c_r
a_r =c_r

try:
    while True:
        distance_left = get_distance(TRIG_LEFT, ECHO_LEFT)
        distance_right = get_distance(TRIG_RIGHT, ECHO_RIGHT)

        # average distance
        c_l = b_l
        b_l = a_l
        a_l = distance_left

        averaged_distance_left = mean(a_l, b_l, c_l)

         # average distance
        c_r = b_r
        b_r = a_r
        a_r = distance_right

        averaged_distance_right = mean(a_r, b_r, c_r)       

        # Determine which side to beep and set balance
        if averaged_distance_left < 50.0:
            play_obj = play_beep(1000, -1.0)  # Beep on the left
        elif averaged_distance_right < 50.0:
            play_obj = play_beep(1000, 1.0)   # Beep on the right

        # Delay for a bit before the next check
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()
