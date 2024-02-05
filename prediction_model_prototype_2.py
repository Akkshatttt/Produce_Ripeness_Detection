import serial
import threading
import subprocess
import csv
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PySimpleGUI as sg
from datetime import datetime
latest_entry = []
predictions =None
ripeness_labels =[]
class Ripeness_Detection:
    def __init__(self, data):
        self.df = data
        self.inputs = []
        self.labels = []
        self.ripeness_class_names = ["Early Ripe", "Partially Ripe", "Ripe", "Decay", "Undefined"]
        global ripeness_labels
        ripeness_labels=self.ripeness_class_names
    def define_and_assign_labels(self):
        self.labels = self.df.pop("Ripeness")
    def scale_data_and_define_inputs(self):
        self.df["scaled_F1"] = self.df.pop("F1") / 1000
        self.df["scaled_F2"] = self.df.pop("F2") / 1000
        self.df["scaled_F3"] = self.df.pop("F3") / 1000
        self.df["scaled_F4"] = self.df.pop("F4") / 1000
        self.df["scaled_F5"] = self.df.pop("F5") / 1000
        self.df["scaled_F6"] = self.df.pop("F6") / 1000
        self.df["scaled_F7"] = self.df.pop("F7") / 1000
        self.df["scaled_F8"] = self.df.pop("F8") / 1000
        self.df["scaled_NIR_1"] = self.df.pop("NIR_1") / 1000
        self.df["scaled_NIR_2"] = self.df.pop("NIR_2") / 1000
        for i in range(len(self.df)):
            self.inputs.append(np.array([self.df["scaled_F1"][i], self.df["scaled_F2"][i], self.df["scaled_F3"][i], self.df["scaled_F4"][i], self.df["scaled_F5"][i], self.df["scaled_F6"][i], self.df["scaled_F7"][i], self.df["scaled_F8"][i], self.df["scaled_NIR_1"][i], self.df["scaled_NIR_2"][i]]))
        self.inputs = np.asarray(self.inputs)
    def split_data(self):
        l = len(self.df)
        self.train_inputs = self.inputs[0:int(l*0.95)]
        self.test_inputs = self.inputs[int(l*0.95):]
        self.train_labels = self.labels[0:int(l*0.95)]
        self.test_labels = self.labels[int(l*0.95):]
    def build_and_train_model(self):
        self.model = keras.Sequential([
            keras.Input(shape=(10,)),
            keras.layers.Dense(16),
            keras.layers.Dense(32),
            keras.layers.Dense(64),
            keras.layers.Dense(128),
            keras.layers.Dense(256),
            keras.layers.Dense(512),
            keras.layers.Dense(4, activation='softmax')
        ])
        self.model.compile(optimizer='adam', loss="sparse_categorical_crossentropy", metrics=['accuracy'])
        self.model.fit(self.train_inputs, self.train_labels, epochs=19)
        print("\n\nModel Evaluation:")
        global test_acc
        test_loss, test_acc = self.model.evaluate(self.test_inputs, self.test_labels)
        print("Evaluated Accuracy: ",test_acc*100,"%")

         
    def save_model(self):
        self.model.save(r"C:\Users\Akshatt\Desktop\V&F Rip\Test Backups\testmodel2.keras")
    def Neural_Network(self, save):
        self.define_and_assign_labels()
        self.scale_data_and_define_inputs()
        self.split_data()
        self.build_and_train_model()
        if save:
            self.save_model()
            
    def get_latest_entry(self):
        df = self.df.tail(1)
        return [df["F1"].values[0]/1000, df["F2"].values[0]/1000, df["F3"].values[0]/1000, df["F4"].values[0]/1000, df["F5"].values[0]/1000, df["F6"].values[0]/1000, df["F7"].values[0]/1000, df["F8"].values[0]/1000, df["NIR_1"].values[0]/1000, df["NIR_2"].values[0]/1000]

    def make_predictions(self):
        global latest_entry
        latest_entry = self.get_latest_entry()
        prediction_array = np.array([latest_entry])
        global predictions
        predictions = saved_model.predict(prediction_array)
        send_prediction=str(np.argmax(predictions[0]))
        access_serial.write(send_prediction.encode())
        
traindata = r"trainingdatabase.csv"
outdata = r"outputdatabase.csv"
serial_port = 'COM35'
baud_rate = 9600
access_serial = serial.Serial(serial_port, baud_rate)
sg.theme('Black')

layout = [[sg.Text('Data received from sensor:', font=('Arial', 14), background_color='#222222')],
          [sg.Text('', key='currentserialdata', font=('Arial', 14),pad=15)],
          [sg.Text('Predicted Ripeness:', font=('Arial', 14),background_color='#222222'), sg.Text('', key='ripenesslevel', font=('Arial', 14)),sg.Text('Label:', font=('Arial', 14),background_color='#222222'), sg.Text('', key='ripenesslabel', font=('Arial', 14))],
          [sg.Text('Current Model Accuracy:', font=('Arial', 14),background_color='#222222'), sg.Text('', key='modelaccuracy', font=('Arial', 14))],
          [sg.Button('Open Output Logs', font=('Arial', 14),pad=20),sg.Exit('Quit', font=('Arial', 14),pad=20,)]]

try:
    saved_model = keras.models.load_model(r"sigmoidmodel.keras")
    print("Model loaded successfully.")
except (OSError, IOError):
    df = pd.read_csv(traindata)
    build_class = Ripeness_Detection(df)
    build_class.Neural_Network(True)

window = sg.Window('Sensor Data', layout, finalize=True)
def open_output_log():
    file_path = r"outputdatabase.csv"
    try:
        subprocess.Popen(['notepad.exe', file_path], shell=True)
    except FileNotFoundError:
        print("Notepad not found. Please make sure it's installed on your system.")
def serialdata():
    while True:
        try:
            rawdata = access_serial.readline().decode('utf-8').strip()
            processedata = list(map(int, rawdata.split(',')))
            print(f'Received data: {rawdata}')
            
            finaldata = processedata + [datetime.now().strftime('%d/%m')]
            with open(outdata, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(finaldata)
                
            df = pd.read_csv(outdata)
            input_class = Ripeness_Detection(df)
            input_class.make_predictions()
            
            latest_index = df.index[-1]
            df.at[latest_index, 'Prediction'] = np.argmax(predictions[0])
            df.to_csv(outdata, index=False)
            
            print(latest_entry)
            print("\nModel Predictions:")
            print("Prediction => ", ripeness_labels[np.argmax(predictions[0])])
        
        except KeyboardInterrupt:
            access_serial.close()

def update_gui():
    while True:
        event, values = window.read(timeout=1000)
        if event == 'Open Output Logs':
            open_output_log()
        elif event == 'Quit' or event is None:
            window.close()
            break
        else:
            if predictions is not None:
                window['currentserialdata'].update(latest_entry)
                window['ripenesslabel'].update(ripeness_labels[np.argmax(predictions[0])])
                window['ripenesslevel'].update(np.argmax(predictions[0]))
                window['modelaccuracy'].update("94.2%")
            else:
                window['currentserialdata'].update("No data available")
                window['ripenesslabel'].update("No data available")
                window['ripenesslevel'].update("No data available")
                window['modelaccuracy'].update("No data available")

serial_thread = threading.Thread(target=serialdata, daemon=True)
serial_thread.start()

update_gui()