from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import os
import websocket
import thread
import time
import wiringpi as wiringpi
import numpy as np
from keras.layers.core import Layer, Dense, Dropout, Activation, Flatten, Reshape, Permute
from keras.layers.convolutional import Convolution2D, MaxPooling2D, UpSampling2D, ZeroPadding2D, Conv2D, UpSampling2D
from keras.models import Model
from keras.layers import Input, Dense
from keras import backend as K

FRAME_H =  90
FRAME_W = 180

NET_H =  70
NET_W = 180

RECORD = True

STEER_MIDPT = 150.
STEER_UPPER = 200.
STEER_LOWER = 100.

def normalize(image):
    image = image.astype('float32')
    image -= np.mean(image, axis=(0,1))
    image /= np.std( image, axis=(0,1))

    return image
 
"""
Construct the network and load the weight
"""
image_inp = Input(shape=(NET_H, NET_W, 3))

x = Conv2D(filters=8,  kernel_size=(5, 5), activation='relu')(image_inp)
x = MaxPooling2D((2, 2))(x)

x = Conv2D(filters=16, kernel_size=(5, 5), activation='relu')(x)
x = MaxPooling2D((2, 2))(x)

x = Conv2D(filters=32, kernel_size=(5, 5), activation='relu')(x)
x = MaxPooling2D((2, 2))(x)

x = Flatten()(x)
x = Dropout(.5)(x)
x = Dense(128, activation = 'relu')(x)
x = Dropout(.5)(x)
x = Dense(1, activation='tanh')(x)

angle_out = x

model = Model(inputs=[image_inp], outputs=[angle_out])
model.load_weights('weights.hdf5')

"""
Setup pins for steering
"""
wiringpi.wiringPiSetupGpio()

wiringpi.pinMode(18,2)
wiringpi.pwmSetMode(0)
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(551)
wiringpi.pwmWrite(18, 0)

""" 
Capture frames from the camera
"""
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (FRAME_W, FRAME_H)
camera.framerate = 50
rawCapture = PiRGBArray(camera, size=(FRAME_W, FRAME_H))
time.sleep(0.1)

os.system('rm -r demo')
os.system('mkdir demo')
os.system('mkdir demo/image')
os.system('mkdir demo/steer')
counter = 0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# Grab the raw NumPy array representing the image
	image = cv2.flip(frame.array, 0)
	#cv2.imshow("Frame", image)

	# Make angle prediction
	net_inp = np.expand_dims(normalize(image[20:]), 0)
	net_out = model.predict(net_inp)[0][0]

	# Send PWM signal to servo
	steer = int(net_out * (STEER_UPPER - STEER_MIDPT) + STEER_MIDPT)
	wiringpi.pwmWrite(18, steer)
	#print 'Predicted Angle:', steer

	if RECORD: 
		cv2.imwrite('demo/image/' + str(counter).zfill(6) + '.png', image)
		with open('demo/steer/' + str(counter).zfill(6) + '.txt', 'w') as steer_file:
			steer_file.write(str(steer*10))
		counter += 1

	# Clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	key = cv2.waitKey(1) & 0xFF
 
	# If the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
