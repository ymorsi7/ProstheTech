#include "BluetoothSerial.h"
const int readPin = A1;
const int readPin1 = A4;
BluetoothSerial SerialBT;
void setup() {
  Serial.begin(115200);
  SerialBT.begin();
  Serial.println("The device started, now you can pair it with bluetooth!");
}

void loop() {
  float totalVoltage1 = 0.0;
  float totalVoltage2 = 0.0;
  for(int i = 0; i< 100; i++) {
    int sensorValue1 = analogRead(readPin);
    int sensorValue2 = analogRead(readPin1);
    float voltage1 = (sensorValue1) * (3.3 / 4095.0);
    totalVoltage1 += voltage1;
    float voltage2 = (sensorValue2) * (3.3 / 4095.0);
    totalVoltage2 += voltage2;
    delay(1);
  }

  float avgVoltage1 = totalVoltage1 / 100;
  float avgVoltage2 = totalVoltage2 / 100;

  Serial.print(avgVoltage1, 6);
  Serial.print(" ");
  Serial.println(avgVoltage2, 6);
  SerialBT.print(avgVoltage1, 6);
  SerialBT.print(" ");
  SerialBT.println(avgVoltage2, 6);
  delay(50);
}
