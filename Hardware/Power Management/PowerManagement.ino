#define NUM_SAMPLES 20

// Constants
const int SENSOR_PIN_A0 = A0;   // Input pin for measuring Vout from INA169
const int SENSOR_PIN_A1 = A1;   // Input pin for measuring Vout from voltage divider
const float RS = 0.1;           // Shunt resistor value (in ohms) for INA169
const float VOLTAGE_REF = 5.0;  // Reference voltage for analog read, //5.126 <-- voltage regulator
const float R1 = 22000.0;       // Resistor 22k ohms (10% tolerance)
const float R2 = 22000.0;       // Resistor 22k ohms with 20% tolerance from R1 26888.889/25545.455/20431 with 5v

// Global Variables
unsigned char sample_count = 0; // current sample number
float sensorValueA0;            // Variable to store value from analog read
float sensorValueA1;            // Variable to store value from analog read/sum of samples taken
float voltage;                  // Calculated Voltage Out value, Vout = Vin * R2/(R1+R2)
float voltageIn;                // Calculated Voltage Source value
float current;                  // Calculated current value
float power;                    // Calculated power value
float lastPower = 0.0;          // Previous power value
float energy;                   // Calculated energy value

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

  // Remap the ADC value into a voltage number (5.23V reference)
  sensorValueA0 = (sensorValueA0 / (float)NUM_SAMPLES * VOLTAGE_REF) / 1024;
  voltage = (sensorValueA1 / (float)NUM_SAMPLES * VOLTAGE_REF) / 1024.0;

  // Calculate VoltageIn from Vout and two resistor
  // Battery V = 5.224, Voltage across resistor = 2.608
  // division factor = 2.001533742331288343558282208589
  voltageIn = voltage * 2;
//  voltageIn = (voltage * (R1+R2)) / R2;
//  voltageIn = voltage * 2.001533742331288343558282208589;
  
  // Follow the equation given by the INA169 datasheet to
  // determine the current flowing through RS. Assume RL = 10k
  // Is = (Vout x 1k) / (RS x RL)
  current = (sensorValueA0 / (RS * 10.0)) * 1000;

  // Power value
  power = current * voltage;

  // Energy value
  energy = ((power + lastPower) / 2) * 500 / 3600000;
  lastPower = lastPower + power;
  
  // Output value (in amps/watts/voltage/joules) to the serial monitor to 2 decimal
  // places
  Serial.print(current, 2);
  Serial.print(" mA | ");
  Serial.print(power, 2);
  Serial.print(" mW | ");
  Serial.print(voltage, 2);
  Serial.print(" V | ");
  Serial.print(voltageIn,2 );
  Serial.print(" Vin | ");
  Serial.print(energy, 2);
  Serial.println(" J");

  sample_count = 0;
  sensorValueA0 = 0;
  sensorValueA1 = 0;
  // Delay program for a few milliseconds
  delay(500);

}

