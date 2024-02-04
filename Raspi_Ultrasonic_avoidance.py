import RPi.GPIO as GPIO
import time
import pygame

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Set pins for the sensors
TRIG_LEFT = 24
ECHO_LEFT = 23
TRIG_RIGHT = 27
ECHO_RIGHT = 22
TRIG_MID = 5
ECHO_MID = 6
distance_start_beeping = 1200
distance_stop = 300

#Set up GPIO direction (IN / OUT)
GPIO.setup(TRIG_LEFT, GPIO.OUT)
GPIO.setup(ECHO_LEFT, GPIO.IN)
GPIO.setup(TRIG_RIGHT, GPIO.OUT)
GPIO.setup(ECHO_RIGHT, GPIO.IN)
GPIO.setup(TRIG_MID, GPIO.OUT)
GPIO.setup(ECHO_MID, GPIO.IN)

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




def play_beep(balance, volume, sound_file):
    # Validate balance and volume
    if not -1.0 <= balance <= 1.0:
        raise ValueError("Balance must be between -1.0 (full left) and 1.0 (full right).")
    if not 0.0 <= volume <= 1.0:
        raise ValueError("Volume must be between 0.0 (mute) and 1.0 (max).")

    try:
        # Initialize Pygame mixer
        pygame.mixer.init()

        # Load beep sound
        beep_sound = pygame.mixer.Sound(sound_file)

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


def calculate_level_balance(data_sensor_left, data_sensor_mid, data_sensor_right, dist_start, dist_stop):
    balance = 0
    level = 0
    # adjust for level, Peeping starts at distance_start_beeping, Warning at distance_stop 
    min_dist = min(data_sensor_left,data_sensor_mid, data_sensor_right)
    #print(f"min_dist: {min_dist}, dist_start: {dist_start}, dist_stop: {dist_stop}")  # Debugging line
    if min_dist < dist_stop:
        level = 1
    elif min_dist < dist_start:
        level = (dist_start - min_dist)/dist_start
    else:
        level = 0
    # calculate balance
    if min_dist < dist_start:
        #map balance from -1 (most left) to 1 (most right)
        balance = 2 * (data_sensor_left / (data_sensor_left + data_sensor_right)) - 1

    return [level, balance]


# start of Main
#initialise variables
c_l = (TRIG_LEFT, ECHO_LEFT)
b_l = c_l
a_l =c_l

c_r = (TRIG_RIGHT, ECHO_RIGHT)
b_r = c_r
a_r =c_r

c_m = (TRIG_RIGHT, ECHO_RIGHT)
b_m = c_m
a_m =c_m

level = 0
balance = 0

try:
    while True:
        #read sensor values and calculate floating average

        distance_left = get_distance(TRIG_LEFT, ECHO_LEFT)
        distance_right = get_distance(TRIG_RIGHT, ECHO_RIGHT)
        distance_mid = get_distance(TRIG_MID, ECHO_MID)
        # average distance left
        c_l = b_l
        b_l = a_l
        a_l = distance_left
        averaged_distance_left = (3 * a_l + 2 * b_l + c_l)/6
        # average distance right
        c_r = b_r
        b_r = a_r
        a_r = distance_right
        averaged_distance_right = (3 * a_r + 2 * b_r + c_r)/6  
        # average distance Middle
        c_m = b_m
        b_m = a_m
        a_m = distance_mid
        averaged_distance_mid = (3 * a_m + 2 * b_m + c_m)/6

        # adjust for level, Peeping starts at distance_start_beeping, Warning at distance_stop 
        [level, balance] = calculate_level_balance(averaged_distance_left, averaged_distance_mid, averaged_distance_right, distance_start_beeping, distance_stop)

        # play beep
        if level < 1:
            play_obj = play_beep(balance, level, "beep.mp3")
            print("beep")
            print(("level:{} \nbalance:{}".format(level, balance)))
        else:
            play_obj = play_beep(balance, level, "beep_stop.mp3")
            print("stop")
            print(("level:{} \nbalance:{}".format(level, balance)))

        # Delay for a bit before the next check
        time.sleep(1.1-level)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()
