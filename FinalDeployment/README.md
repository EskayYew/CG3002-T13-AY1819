# Final Deployment Folder

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
