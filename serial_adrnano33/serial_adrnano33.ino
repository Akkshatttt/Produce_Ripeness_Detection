//#include <WiFiNINA.h>
#include "DFRobot_AS7341.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

DFRobot_AS7341 as7341;
DFRobot_AS7341::sModeOneData_t data1;
DFRobot_AS7341::sModeTwoData_t data2;

#define pot A0
#define class_1 2
#define class_2 3
#define class_3 4
#define class_4 5
#define class_5 6
#define OLED_RESET -1
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define I2C_ADDRESS 0x3C
#define buzzer 7
#define LED_OUT 9
#define LED_IN 8

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

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

  Wire.begin();
  display.begin(SSD1306_SWITCHCAPVCC, I2C_ADDRESS);
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(0,0);
  display.println("Produce Ripeness Detector");
  display.display();
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
    loading();
    }
  if (digitalRead(class_2)==LOW){
    run("1");
    loading();
    }
  if (digitalRead(class_3)==LOW){
    run("2");
    loading();
    }
  if (digitalRead(class_4)==LOW){
    run("3");
    loading();
    }
  if (digitalRead(class_5)==LOW){
    run("4");
    loading();
    }
  delay(250);
  display.display();

  if (Serial.available() > 0) {
    int user_input = Serial.read();
    display.setCursor(0, 0);
    digitalWrite(LED_IN, HIGH);
    delay(1000);
    digitalWrite(LED_IN, LOW);
    switch(user_input) {
      case '0':
        display.clearDisplay();
        display.print(F("Prediction: "));
        display.println(F("Unripe"));
        tone(buzzer, 445, 200);
        delay(250);
        tone(buzzer, 445, 200);
        break;
      case '1':
        display.clearDisplay();
        display.print(F("Prediction: "));
        display.println(F("Partially Ripe"));
        tone(buzzer, 445, 200);
        break;
      case '2':
        display.clearDisplay();
        display.print(F("Prediction: "));
        display.println(F("Ripe"));
        tone(buzzer, 445, 200);
        break;
      case '3':
        display.clearDisplay();
        display.print(F("Prediction: "));
        display.println(F("Decaying"));
        tone(buzzer, 1000, 200);
        delay(250);
        tone(buzzer, 1000, 200);
        break;
      default:
        display.clearDisplay();
        display.println(F("Invalid input"));
    }
    display.display();
  }
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
  Serial.println(class_id);
  digitalWrite(LED_OUT, HIGH);
  delay(1000);
  digitalWrite(LED_OUT, LOW);
}

void read_controls() {
  pot_val = analogRead(pot);
}

void adjust_brightness() {
  int brightness = map(pot_val, 0, 1023, 1, 21);
  //Serial.print("\nBrightness: "); Serial.println(brightness);
  as7341.controlLed(brightness);
}

void loading(){
  display.setCursor(0, 0);
  display.clearDisplay();
  display.println("Waiting    for model output...");
}