#include <WiFiNINA.h>
#include "DFRobot_AS7341.h"

DFRobot_AS7341 as7341;
DFRobot_AS7341::sModeOneData_t data1;
DFRobot_AS7341::sModeTwoData_t data2;

#define pot A0
#define class_1 7
#define class_2 3
#define class_3 6
#define class_4 5
#define class_5 4

int pot_val;

void setup() {
  Serial.begin(9600);

  pinMode(class_1, INPUT_PULLUP);
  pinMode(class_2, INPUT_PULLUP);
  pinMode(class_3, INPUT_PULLUP);
  pinMode(class_4, INPUT_PULLUP);
  pinMode(class_5, INPUT_PULLUP);

  while (as7341.begin() != 0) {
    Serial.println("I2C init failed, please check if the wire connection is correct");
    delay(1000);
  }
  as7341.enableLed(true);
}

void loop() {
  read_controls();
  adjust_brightness();
  as7341.startMeasure(as7341.eF1F4ClearNIR);
  data1 = as7341.readSpectralDataOne();
  as7341.startMeasure(as7341.eF5F8ClearNIR);
  data2 = as7341.readSpectralDataTwo();

  if (digitalRead(class_1)==LOW){
    run("0");
    }
  if (digitalRead(class_2)==LOW){
    run("1");
    }
  if (digitalRead(class_3)==LOW){
    run("2");
    }
  if (digitalRead(class_4)==LOW){
    run("3");
    }
  if (digitalRead(class_5)==LOW){
    run("4");
    }
  delay(250);
}

void run(String class_id) {
  Serial.print(data1.ADF1); Serial.print(",");
  Serial.print(data1.ADF2); Serial.print(",");
  Serial.print(data1.ADF3); Serial.print(",");
  Serial.print(data1.ADF4); Serial.print(",");
  Serial.print(data2.ADF5); Serial.print(",");
  Serial.print(data2.ADF6); Serial.print(",");
  Serial.print(data2.ADF7); Serial.print(",");
  Serial.print(data2.ADF8); Serial.print(",");
  Serial.print(data1.ADNIR); Serial.print(",");
  Serial.print(data2.ADNIR); Serial.print(",");
  Serial.print(class_id); Serial.print(",");
  Serial.print("d/m"); Serial.print(","); Serial.println();
}

void read_controls() {
  pot_val = analogRead(pot);
}

void adjust_brightness() {
  int brightness = map(pot_val, 0, 1023, 1, 21);
  //Serial.print("\nBrightness: "); Serial.println(brightness);
  as7341.controlLed(brightness);
}
