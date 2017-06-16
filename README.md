
## Objective

To make a lane follower based on a standard RC car like this https://www.youtube.com/watch?v=-v6q2dNZTU8.

## Design

The basic idea is to use a Raspberry Pi to control the RC car. The Raspberry Pi makes steering action based on camera image.

<img width="500" src="images/hardware.jpg"/>

** Hardware **

For the uninitiated, the receiver of a standard RC car receives throttle and steering signals from the transmitter. The signals are converted to PWM pulses by the receiver to directly control the speed of the motor and the steering angle of the servo. The following figure pictures the wiring of a standard RC car:

<img width="500" src="images/rc_car.png"/>

During data collection, we will simply hook the steering PWM of the car to pin GPIO17. The script **raspberry_pi/collect_data.py** will record the values of steering PWM and the associated images. The data of each trial are collectively stored in driving\_trial_*. The trial folders are automatically numbered.

** Software **

In autonomous mode, the servo of the car is connected to pin GPIO18 of Raspberry Pi instead of the receiver. The Raspberry Pi will use the camera to capture the image and use the trained neural network to predict the steering angle. The steering angle is then translated to PWM signal to control the servo. This whole processing pipeline is implemented in the script **raspberry_pi/drive_me.py**.

<img width="500" src="images/design.png"/>

## Data Collection

Copy files in folder raspberry_pi to Raspberry Pi.

sudo pigpiod

sudo python collect_data.py

The script will capture the images and the steering angles to folder drive\_trial_*. The trial folders are automatically numbered.

## Train the Network

Copy the collected data in drive\_trial_* from Raspberry Pi to the machine used to train the CNN.

Follow the instructions in the "Learn to Drive.ipynb".

The trained CNN will be saved to file weights.hdf5.

## Let the Car Drive Autonomously

Copy the trained weights (file weights.hdf5) from the training machine to Raspberry Pi.

sudo python drive_me.py
