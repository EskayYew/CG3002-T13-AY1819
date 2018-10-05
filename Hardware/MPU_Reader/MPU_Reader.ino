#include<Wire.h>
extern "C" { 
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}

const int MPU=0x68; 
#define TCAADDR 0x70
int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;
 
void tcaselect(uint8_t i) {
  if (i > 7) return;
 
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}

void setup(){
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
  tcaselect(0);
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,12,true);  
  AcX=Wire.read()<<8|Wire.read();    
  AcY=Wire.read()<<8|Wire.read();  
  AcZ=Wire.read()<<8|Wire.read();  
  GyX=Wire.read()<<8|Wire.read();  
  GyY=Wire.read()<<8|Wire.read();  
  GyZ=Wire.read()<<8|Wire.read();  
  
  Serial.print("Accelerometer: ");
  Serial.print("X0 = "); Serial.print(AcX/8192);
  Serial.print(" | Y0 = "); Serial.print(AcY/8192);
  Serial.print(" | Z0 = "); Serial.println(AcZ/8192); 
  
  Serial.print("Gyroscope: ");
  Serial.print("X0 = "); Serial.print(GyX/131);
  Serial.print(" | Y0 = "); Serial.print(GyY/131);
  Serial.print(" | Z0 = "); Serial.println(GyZ/131);
  Serial.println(" ");

  //Wire.endTransmission();
  //delay(333);

  tcaselect(1);
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,12,true);  
  AcX=Wire.read()<<8|Wire.read();    
  AcY=Wire.read()<<8|Wire.read();  
  AcZ=Wire.read()<<8|Wire.read();  
  GyX=Wire.read()<<8|Wire.read();  
  GyY=Wire.read()<<8|Wire.read();  
  GyZ=Wire.read()<<8|Wire.read();  
  
  Serial.print("Accelerometer: ");
  Serial.print("X1 = "); Serial.print(AcX/8192);
  Serial.print(" | Y1 = "); Serial.print(AcY/8192);
  Serial.print(" | Z1 = "); Serial.println(AcZ/8192); 
  
  Serial.print("Gyroscope: ");
  Serial.print("X1 = "); Serial.print(GyX/131);
  Serial.print(" | Y1 = "); Serial.print(GyY/131);
  Serial.print(" | Z1 = "); Serial.println(GyZ/131);
  Serial.println(" ");

  //Wire.endTransmission();
  //delay(333);

  tcaselect(1);
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,12,true);  
  AcX=Wire.read()<<8|Wire.read();    
  AcY=Wire.read()<<8|Wire.read();  
  AcZ=Wire.read()<<8|Wire.read();  
  GyX=Wire.read()<<8|Wire.read();  
  GyY=Wire.read()<<8|Wire.read();  
  GyZ=Wire.read()<<8|Wire.read();  
  
  Serial.print("Accelerometer: ");
  Serial.print("X1 = "); Serial.print(AcX/8192);
  Serial.print(" | Y1 = "); Serial.print(AcY/8192);
  Serial.print(" | Z1 = "); Serial.println(AcZ/8192); 
  
  Serial.print("Gyroscope: ");
  Serial.print("X1 = "); Serial.print(GyX/131);
  Serial.print(" | Y1 = "); Serial.print(GyY/131);
  Serial.print(" | Z1 = "); Serial.println(GyZ/131);
  Serial.println(" ");
}
