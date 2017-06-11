from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import read_PWM
import pigpio
import os
import time

FRAME_H =  90
FRAME_W = 180

STEER_GPIO = 17
FRAME_RATE = 50
TRIAL_NUM  = 0

for file in os.listdir('.'):
    if 'drive_trial_' in file:
        TRIAL_NUM += 1

# Setup the camera
camera = PiCamera()
camera.resolution = (FRAME_W, FRAME_H)
camera.framerate = FRAME_RATE
rawCapture = PiRGBArray(camera, size=(FRAME_W, FRAME_H))
time.sleep(0.1)

# Setup PWM reader
pi = pigpio.pi()
steer_pwm = read_PWM.reader(pi, STEER_GPIO)

# Start recording
trial = 'drive_trial_' + str(TRIAL_NUM)
print trial
os.system('mkdir ' + trial)
os.system('mkdir ' + trial + '/image')
os.system('mkdir ' + trial + '/steer')
counter = 0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # Grab the raw NumPy array representing the image
    image = cv2.flip(frame.array, 0)
    #cv2.imshow("Frame", image)

    cv2.imwrite(trial + '/image/' + str(counter).zfill(6) + '.png', image)

    with open(trial + '/steer/' + str(counter).zfill(6) + '.txt', 'w') as steer_file:
        steer_pw = steer_pwm.pulse_width()
        steer_file.write(str(steer_pw))

    print counter, '\t', steer_pw
    counter += 1

    # Clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    key = cv2.waitKey(1) & 0xFF
 
    # If the `q` key was pressed, break from the loop
    if key == ord("q"):
        break