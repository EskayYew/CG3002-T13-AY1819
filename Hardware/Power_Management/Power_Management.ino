#include "Time.h"
#define NUM_SAMPLES 10

// Constants
const int SENSOR_PIN_A0 = A0;   // Input pin for measuring Vout from INA169
const int SENSOR_PIN_A1 = A1;   // Input pin for measuring Vout from voltage divider
const float RS = 0.1;           // Shunt resistor value (in ohms) for INA169
const float VOLTAGE_REF = 5.0;  // Reference voltage for analog read, //5.126 <-- voltage regulator
const float R1 = 22000.0;       // Resistor 22k ohms (10% tolerance)
const float R2 = 22000.0;       // Resistor 22k ohms with 20% tolerance from R1 26888.889/25545.455/20431 with 5v

// Global Variables
unsigned char sample_count = 0;       // current sample number
float sensorValueA0 = 0.0;            // Variable to store value from analog read
float sensorValueA1 = 0.0;            // Variable to store value from analog read/sum of samples taken
float voltageOut = 0.0;               // Calculated Voltage Out value, Vout = Vin * R2/(R1+R2)
float voltageIn = 0.0;                // Calculated Voltage In Source value
float current = 0.0;                  // Calculated current value
float totalCurrent = 0.0;             // Calculated Total current value
float avgAmp = 0.0;                   // Calculated avgAmp
float ampHr = 0.0;                    // Calculated amp-hour
float power = 0.0;                    // Calculated power value
float lastPower = 0.0;                // Previous power value
float energy = 0.0;                   // Calculated energy value
float elapsedTime = 0.0;
unsigned long prevTime = 0;
unsigned long currTime = 0;

void printDigits(int digits) {
  // utility function for digital clock display: prints preceding colon and leading 0
  Serial.print(":");
  if (digits < 10)
  Serial.print('0');
  Serial.print(digits);
}

void setup() {
  // Initialize serial monitor
  Serial.begin(9600);
}

void loop() {
  // Read analog value
  // take a number of analog samples and add them up
  while (sample_count < NUM_SAMPLES) {
      sensorValueA0 += analogRead(SENSOR_PIN_A0);
      sensorValueA1 += analogRead(SENSOR_PIN_A1);
      sample_count++;
      delay(10);
  }

  // Actual voltage calibration: 
  // 2.73v 5.47v analogRead: 560
  // 1 is equivalent to 2.73/560=4.875mv
  // Vout = (4.875*sample)/1000
  // Actual battery voltage = (2*Vout)
  // Remap the ADC value into a voltage number
  sensorValueA0 = (sensorValueA0 / (float)NUM_SAMPLES * 5.2) / 1024.0;
  voltageOut = (sensorValueA1 / (float)NUM_SAMPLES * 4.975) / 1024.0;

  // Calculate Vin from Vout and two resistor
  // Battery V = 5.224, Voltage across resistor = 2.608
  // division factor = 2.001533742331288343558282208589
  voltageIn = voltageOut * 2;

  // Current value
  // Following the equation given by the INA169 datasheet to
  // determine the current flowing through RS. Assume RL = 10k
  // Is = (Vout x 1k) / (RS x RL)
  current = (sensorValueA0 / (RS * 10.0));
  totalCurrent = (totalCurrent + current * 1000) ;
  avgAmp = totalCurrent / elapsedTime;
  ampHr = (avgAmp * elapsedTime) / 3600; //mAh
  
  // Power value
  power = current * voltageIn;
  
  // Energy value
  if (power != 0) {
  currTime = millis();
  elapsedTime = (currTime - prevTime) / 3600000.0;
  prevTime = currTime;
  energy = energy + (power * elapsedTime) * 1000;
  }
  
  // Output value (in amps/watts/voltage/joules) to the serial monitor to 2 decimal
  // places
  Serial.print(current, 2);
  Serial.print(" A | ");
  Serial.print(ampHr, 2);
  Serial.print(" mAh | ");
  Serial.print(power, 2);
  Serial.print(" W | ");
  Serial.print(energy, 2);
  Serial.print(" Wh | ");
  Serial.print(voltageOut, 2);
  Serial.print(" Vout | ");
  Serial.print(voltageIn,2 );
  Serial.print(" Vin | ");
  Serial.print("Uptime: ");
  Serial.print(hour());
  printDigits(minute());
  printDigits(second());
  Serial.println();

  sample_count = 0;
  sensorValueA0 = 0;
  sensorValueA1 = 0;
  // Delay program for a few milliseconds
  delay(800);

}

