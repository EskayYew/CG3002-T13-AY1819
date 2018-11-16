# Final Deployment Folder

CG3002-T13-AY1819

This folder contains the files needed for the overall deployment of the dance detection system. Each folder contains instructions to install the relevant packages and run the files needed for the different components of the system.

Intructions for installation of Operating System on Raspberry Pi can be found at the bottom of this README.

## Folders needed for dance detection system execution:

PiDeployment

ArduinoDeployment

ServerDeployment

## Folders needed for data collection on Pi:

DataCollection

ArduinoDeployment

## Pi Deployment Folder

Contains installation instructions and all software files
that needs to be on the Pi, in order for the software
component of the Dance Detection System to work.

Main Processes on Pi:

Receiving data from Arduino

Processing of data and prediction of move

Sending of predicted move to server 


## Arduino Deployment Folder

Contains all software files that needs to be uploaded on to the Arduino, in order for
the Arduino to receive data from sensors and send data from Arduino to Pi. 

Main Processes on Arduino:

Collect data from hardware sensors

Calculation of power values

Sending of data from Arduino to Pi

## Data Collection Folder

Contains all software files that is needed to be uploaded onto the Pi so as to collect data from sensors and arduino.
The data collected can then be used to train the ML model.

## Server Deployment Folder

Contains all software files that is needed to be uploaded onto a computer so as to host an evaluation server for the dance detection system.

## Installation Instructions for Raspberry Pi

### Setting up of Raspberry Pi (installation of Raspbian OS GNU/LINUX 9 via NOOBS)
Reference from:

https://learn.adafruit.com/setting-up-a-raspberry-pi-with-noobs/overview

https://www.youtube.com/watch?v=4z9trGhCbfk

1. Download NOOBS version 282 from: http://www.raspberrypi.org/downloads.

2. Download SD CARD formatter from: https://www.sdcard.org/downloads/formatter_4/.
Format SD CARD via Full Overwrite and Quick Erase through the software application.

3. Drag files from extracted zip folder of NOOBS 282 into SD CARD.

4. Insert SD CARD into SD CARD reader of Pi. Connect keyboard, laptop, desktop screen and power adapter to Raspberry Pi. Power up Raspberry Pi.

5. There will be a process of partitioning & setting up during boot up.

6. Once completed, select and install Raspbian OS. 

7. Once Raspbian OS is installed, a Raspberry Pi Configuration Interface will be displayed, configure the current time and location and also the wireless connection of your raspberry pi. If Raspberry Pi Config does not show up on screen, press `Ctrl + Alt + T`, to open raspberry terminal, and type `sudo raspi-config`.

8. Type `sudo apt-get update` followed by `sudo apt-get upgrade`. The process takes very long so ensure that there is a stable and fast internet connection on the Pi.

### Setting up SSH for raspberry pi
Reference from:

https://learn.adafruit.com/adafruits-raspberry-pi-lesson-6-using-ssh

1. Open raspberry terminal, and type `sudo raspi-config`.

2. Navigate to Interfacing Options of the Configuration Interface, then enable SSH.

3. Reboot Raspberry Pi to make SSH enable configuration permanent. Type `sudo reboot` in raspberry terminal.

4. For Windows Users, we need to install PuTTY and run the program.

5. Once program is running, enter the ip address (can be found via command `ifconfig` on raspberry pi terminal, usually the ip address of the wireless lan connection)

### Setting up VNC viewer for raspberry pi
Reference from: 

https://learn.adafruit.com/adafruit-raspberry-pi-lesson-7-remote-control-with-vnc/overview

1. Open raspberry terminal, type `sudo apt-get update` then `sudo apt-get install tightvncserver`.

2. To run vnc server on raspberry pi 3, type `vncserver :1` into the terminal.

3. User will be prompted to type in a password and asked to create a separate read-only password(user should type n for no). VNC server 
should now be running on raspberry pi.

4. Install VNC Viewer on computer from: https://www.realvnc.com/en/connect/download/viewer/.

5. Run VNC Viewer and set up connection with raspberry pi. Enter ip address of raspberry pi (found from `ifconfig`) and append `:1` when setting up connection using VNC Viewer.

6. In addition, to make VNC server run at startup, it is suggested that you follow this guide: https://learn.adafruit.com/adafruit-raspberry-pi-lesson-7-remote-control-with-vnc/running-vncserver-at-startup
