#include<Wire.h>
extern "C" { 
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}

const int switchPin = 12; //the switch connect to pin 12
int switchState = 0;         // variable for reading the pushbutton status
const int MPU=0x68; 
#define TCAADDR 0x70
const int flexPin = 11;
int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ, Flex;
 
void tcaselect(uint8_t i) {
  if (i > 7) return;
 
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}

void setup(){
  pinMode(switchPin, INPUT); //initialize thebuttonPin as input

  pinMode(flexPin, INPUT);
  
  Wire.begin();
  tcaselect(0);
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); 
  Wire.write(0);    
  Wire.endTransmission(true);
  tcaselect(1);
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); 
  Wire.write(0);    
  Wire.endTransmission(true);
  tcaselect(2);
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); 
  Wire.write(0);    
  Wire.endTransmission(true);
  Serial.begin(115200);
}

void loop(){
  switchState = digitalRead(switchPin);
  
  if (switchState == HIGH ) {

  Flex = digitalRead(flexPin);
  
  tcaselect(0);
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,12,true);  
  AcX=Wire.read()<<8|Wire.read();    
  AcY=Wire.read()<<8|Wire.read();  
  AcZ=Wire.read()<<8|Wire.read();  
  Tmp=Wire.read()<<8|Wire.read();  
  GyX=Wire.read()<<8|Wire.read();  
  GyY=Wire.read()<<8|Wire.read();  
  GyZ=Wire.read()<<8|Wire.read();  
  
  Serial.print("Accelerometer: ");
  Serial.print("X0 = "); Serial.print(AcX/16384);
  Serial.print(" | Y0 = "); Serial.print(AcY/16384);
  Serial.print(" | Z0 = "); Serial.println(AcZ/16384); 
  
  Serial.print("Gyroscope: ");
  Serial.print("X0 = "); Serial.print(GyX/131);
  Serial.print(" | Y0 = "); Serial.print(GyY/131);
  Serial.print(" | Z0 = "); Serial.println(GyZ/131);
  Serial.println(" ");

  tcaselect(1);
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,12,true);  
  AcX=Wire.read()<<8|Wire.read();    
  AcY=Wire.read()<<8|Wire.read();  
  AcZ=Wire.read()<<8|Wire.read();  
  Tmp=Wire.read()<<8|Wire.read();  
  GyX=Wire.read()<<8|Wire.read();  
  GyY=Wire.read()<<8|Wire.read();  
  GyZ=Wire.read()<<8|Wire.read();  
  
  Serial.print("Accelerometer: ");
  Serial.print("X0 = "); Serial.print(AcX/16384);
  Serial.print(" | Y0 = "); Serial.print(AcY/16384);
  Serial.print(" | Z0 = "); Serial.println(AcZ/16384); 
  
  Serial.print("Gyroscope: ");
  Serial.print("X0 = "); Serial.print(GyX/131);
  Serial.print(" | Y0 = "); Serial.print(GyY/131);
  Serial.print(" | Z0 = "); Serial.println(GyZ/131);
  Serial.println(" ");

  tcaselect(2);
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,12,true);  
  AcX=Wire.read()<<8|Wire.read();    
  AcY=Wire.read()<<8|Wire.read();  
  AcZ=Wire.read()<<8|Wire.read();  
  Tmp=Wire.read()<<8|Wire.read();  
  GyX=Wire.read()<<8|Wire.read();  
  GyY=Wire.read()<<8|Wire.read();  
  GyZ=Wire.read()<<8|Wire.read();  
  
  Serial.print("Accelerometer: ");
  Serial.print("X0 = "); Serial.print(AcX/16384);
  Serial.print(" | Y0 = "); Serial.print(AcY/16384);
  Serial.print(" | Z0 = "); Serial.println(AcZ/16384); 
  
  Serial.print("Gyroscope: ");
  Serial.print("X0 = "); Serial.print(GyX/131);
  Serial.print(" | Y0 = "); Serial.print(GyY/131);
  Serial.print(" | Z0 = "); Serial.println(GyZ/131);
  Serial.println(" ");

  tcaselect(3);
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,12,true);  
  AcX=Wire.read()<<8|Wire.read();    
  AcY=Wire.read()<<8|Wire.read();  
  AcZ=Wire.read()<<8|Wire.read();  
  Tmp=Wire.read()<<8|Wire.read();  
  GyX=Wire.read()<<8|Wire.read();  
  GyY=Wire.read()<<8|Wire.read();  
  GyZ=Wire.read()<<8|Wire.read();  
  
  Serial.print("Accelerometer: ");
  Serial.print("X0 = "); Serial.print(AcX/16384);
  Serial.print(" | Y0 = "); Serial.print(AcY/16384);
  Serial.print(" | Z0 = "); Serial.println(AcZ/16384); 
  
  Serial.print("Gyroscope: ");
  Serial.print("X0 = "); Serial.print(GyX/131);
  Serial.print(" | Y0 = "); Serial.print(GyY/131);
  Serial.print(" | Z0 = "); Serial.println(GyZ/131);
  Serial.println(" ");
  
  //Wire.endTransmission();
  delay(333);

  }
}
