from statistics import mean
#import RPi.GPIO as GPIO
import time
from pydub import AudioSegment
from pydub.generators import Sine
import pygame

# # Set GPIO mode
# GPIO.setmode(GPIO.BCM)

# # Set pins for the sensors
# TRIG_LEFT = 24
# ECHO_LEFT = 23
# TRIG_RIGHT = 27
# ECHO_RIGHT = 22
# #TRIG_MID = 5
# #ECHO_MID = 6
distance_start_beeping = 1200
distance_stop = 300

# Set up GPIO direction (IN / OUT)
# GPIO.setup(TRIG_LEFT, GPIO.OUT)
# GPIO.setup(ECHO_LEFT, GPIO.IN)
# GPIO.setup(TRIG_RIGHT, GPIO.OUT)
# GPIO.setup(ECHO_RIGHT, GPIO.IN)
# #GPIO.setup(TRIG_MID, GPIO.OUT)
# #GPIO.setup(ECHO_MID, GPIO.IN)

# def get_distance(trig, echo):
#     # Set the trigger to High
#     GPIO.output(trig, True)

#     # Set the trigger after 0.01ms to Low
#     time.sleep(0.00001)
#     GPIO.output(trig, False)

#     StartTime = time.time()
#     StopTime = time.time()

#     # Save StartTime
#     while GPIO.input(echo) == 0:
#         StartTime = time.time()

#     # Save time of arrival
#     while GPIO.input(echo) == 1:
#         StopTime = time.time()

#     # Time difference between start and arrival
#     TimeElapsed = StopTime - StartTime
#     # Multiply with the sonic speed (34300 cm/s)
#     # and divide by 2, because there and back
#     distance = (TimeElapsed * 34300) / 2

#     return distance




def play_beep(balance, volume):
    # Validate balance and volume
    if not -1.0 <= balance <= 1.0:
        raise ValueError("Balance must be between -1.0 (full left) and 1.0 (full right).")
    if not 0.0 <= volume <= 1.0:
        raise ValueError("Volume must be between 0.0 (mute) and 1.0 (max).")

    try:
        # Initialize Pygame mixer
        pygame.mixer.init()

        # Load beep sound
        beep_sound = pygame.mixer.Sound("beep.mp3")

        # Adjust volume (considering Pygame uses 0.0 to 1.0 scale)
        beep_sound.set_volume(volume)

        # Calculate left and right volumes for balance
        left_volume = min(1.0, max(0.0, 1.0 - balance))
        right_volume = min(1.0, max(0.0, 1.0 + balance))

        # Play the beep sound with the specified balance
        channel = beep_sound.play()
        channel.set_volume(left_volume, right_volume)

        # Wait for the beep to finish playing
        while channel.get_busy():
            pygame.time.delay(10)

    except Exception as e:
        print(f"An error occurred: {e}")




# start of Main
#initialise variables
c_l = 400#(TRIG_LEFT, ECHO_LEFT)
b_l = c_l
a_l =c_l

c_r = 400#(TRIG_RIGHT, ECHO_RIGHT)
b_r = c_r
a_r =c_r

c_m = 400#(TRIG_RIGHT, ECHO_RIGHT)
b_m = c_m
a_m =c_m

level = 0


try:
    while True:
        distance_left = 1000#get_distance(TRIG_LEFT, ECHO_LEFT)
        distance_right = 1000#get_distance(TRIG_RIGHT, ECHO_RIGHT)
        distance_mid = 200#get_distance(TRIG_MID, ECHO_MID)

        # average distance left
        c_l = b_l
        b_l = a_l
        a_l = distance_left

        averaged_distance_left = mean([a_l, b_l, c_l])

        # average distance right
        c_r = b_r
        b_r = a_r
        a_r = distance_right

        averaged_distance_right = mean([a_r, b_r, c_r])  

        # average distance Middle
        c_m = b_m
        b_m = a_m
        a_m = distance_mid

        averaged_distance_mid = mean([a_m, b_m, c_m])

        # adjust for level, Peeping starts at distance_start_beeping, Warning at distance_stop 
        min_dist = min(distance_left,distance_right, distance_mid)
        if min_dist < distance_stop:
            level = 1
        elif min_dist < distance_start_beeping:
            level = (distance_start_beeping - min_dist)/distance_start_beeping
        else:
            level = 0

        # calculate balance
        if min_dist < distance_start_beeping:
            #map balance from -1 (most left) to 1 (most right)
            balance = 2 * (distance_left / (distance_left + distance_right)) - 1

        # play beep
        play_obj = play_beep(balance, level)

        # Delay for a bit before the next check
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    #GPIO.cleanup()
