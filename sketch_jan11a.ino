#include <WiFiNINA.h>
#include "DFRobot_AS7341.h"
#include <SD.h>

// ... (other code remains unchanged)

const char filename[] = "C:\\Users\\Akshatt\Desktop\\V&F Rip\\produce_color_databse.csv";  // Name of your CSV file

char ssid[] = "PHN Technology";
char pass[] = "S%&QAVz8z)";
int keyIndex = 0;
const char server[] = "http://192.168.1.7/Vegetables_and_Fruits_Data_Logger/index.php";
int status = WL_IDLE_STATUS;

WiFiClient client;

DFRobot_AS7341 as7341;
DFRobot_AS7341::sModeOneData_t data1;
DFRobot_AS7341::sModeTwoData_t data2;

#define pot A0
#define class_1 2
#define class_2 3
#define class_3 4
#define class_4 5
#define class_5 8
#define green 6
#define red 7

int pot_val, class_1_val, class_2_val, class_3_val, class_4_val, class_5_val;

void setup(){
  Serial.begin(9600);

  pinMode(class_1, INPUT_PULLUP);
  pinMode(class_2, INPUT_PULLUP);
  pinMode(class_3, INPUT_PULLUP);
  pinMode(class_4, INPUT_PULLUP);
  pinMode(class_5, INPUT_PULLUP);
  pinMode(green, OUTPUT);
  pinMode(red, OUTPUT);
  
  while (as7341.begin() != 0) {
    Serial.println("I2C init failed, please check if the wire connection is correct");
    delay(1000);
  }

  as7341.enableLed(true);

  if (WiFi.status() == WL_NO_MODULE) { Serial.println("Connection Failed!"); while (true); }
  while (status != WL_CONNECTED) {
    Serial.println("Attempting to connect to WiFi !!!");
    status = WiFi.begin(ssid, pass);
    delay(10000);
  }

}
void loop(){
  read_controls();
  adjust_brightness();
  as7341.startMeasure(as7341.eF1F4ClearNIR);
  data1 = as7341.readSpectralDataOne();
  as7341.startMeasure(as7341.eF5F8ClearNIR);
  data2 = as7341.readSpectralDataTwo();
  Serial.print("F1(405-425nm): "); Serial.println(data1.ADF1);
  Serial.print("F2(435-455nm): "); Serial.println(data1.ADF2);
  Serial.print("F3(470-490nm): "); Serial.println(data1.ADF3);
  Serial.print("F4(505-525nm): "); Serial.println(data1.ADF4);
  Serial.print("F5(545-565nm): "); Serial.println(data2.ADF5);
  Serial.print("F6(580-600nm): "); Serial.println(data2.ADF6);
  Serial.print("F7(620-640nm): "); Serial.println(data2.ADF7);
  Serial.print("F8(670-690nm): "); Serial.println(data2.ADF8);
  Serial.print("Clear_1: "); Serial.println(data1.ADCLEAR);
  Serial.print("NIR_1: "); Serial.println(data1.ADNIR);
  Serial.print("Clear_2: "); Serial.println(data2.ADCLEAR);
  Serial.print("NIR_2: "); Serial.println(data2.ADNIR);
  Serial.print("\n------------------------------\n");
  delay(1000);

  make_a_get_request("4");

  if(!class_1_val){
    make_a_get_request("0");}
  if(!class_2_val){
    make_a_get_request("1");}
  if(!class_3_val){
    make_a_get_request("2");}
  if(!class_4_val){
    make_a_get_request("3");}
  if(!class_5_val){
    make_a_get_request("4");}
}

void read_controls(){
  pot_val = analogRead(pot);
  class_1_val = digitalRead(class_1);
  class_2_val = digitalRead(class_2);
  class_3_val = digitalRead(class_3);
  class_4_val = digitalRead(class_4);
  class_5_val = digitalRead(class_5);
}

void adjust_brightness(){
  int brightness = map(pot_val, 0, 1023, 1, 21);
  Serial.print("\nBrightness: "); Serial.println(brightness);
  as7341.controlLed(brightness);
}

void make_a_get_request(String _class) {
  // Open the file in write mode
  File dataFile = SD.open(filename, FILE_WRITE);

  // If the file is open, write the data to it
  if (dataFile) {
    dataFile.print(data1.ADF1);
    dataFile.print(",");
    dataFile.print(data1.ADF2);
    dataFile.print(",");
    dataFile.print(data1.ADF3);
    dataFile.print(",");
    dataFile.print(data1.ADF4);
    dataFile.print(",");
    dataFile.print(data2.ADF5);
    dataFile.print(",");
    dataFile.print(data2.ADF6);
    dataFile.print(",");
    dataFile.print(data2.ADF7);
    dataFile.print(",");
    dataFile.print(data2.ADF8);
    dataFile.print(",");
    dataFile.print(data1.ADCLEAR);
    dataFile.print(",");
    dataFile.print(data1.ADNIR);
    dataFile.print(",");
    dataFile.print(data2.ADCLEAR);
    dataFile.print(",");
    dataFile.print(data2.ADNIR);
    dataFile.print(",");
    dataFile.print(_class);
    dataFile.println();

    // Close the file
    dataFile.close();

    Serial.println("Data written to file.");

    // Additional actions or feedback can be added here
  } else {
    Serial.println("Error opening file.");
  }

  delay(2000);  // Adjust the delay as needed
}