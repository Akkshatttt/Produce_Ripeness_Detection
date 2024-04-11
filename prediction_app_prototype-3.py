import serial
import threading
import subprocess
import csv
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")
appWidth, appHeight = 480, 560

latest_entry =[]
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
        global F1data
        global F2data
        global F3data
        global F4data
        global F5data
        global F6data
        global F7data
        global F8data
        F1data=df["F1"].values[0]
        F2data=df["F2"].values[0]
        F3data=df["F3"].values[0]
        F4data=df["F4"].values[0]
        F5data=df["F5"].values[0]
        F6data=df["F6"].values[0]
        F7data=df["F7"].values[0]
        F8data=df["F8"].values[0]
        NIR1data=df["NIR_1"].values[0]
        NIR2data=df["NIR_2"].values[0]
        return [F1data/1000,F2data/1000,F3data/1000,F4data/1000,F5data/1000,F6data/1000,F7data/1000,F8data/1000,NIR1data/1000,NIR2data/1000]

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

try:
    saved_model = keras.models.load_model(r"sigmoidmodel.keras")
    print("Model loaded successfully.")
except (OSError, IOError):
    df = pd.read_csv(traindata)
    build_class = Ripeness_Detection(df)
    build_class.Neural_Network(True)

def open_output_logs(app):
    file_path = r"outputdatabase.csv"
    try:
        subprocess.Popen(['notepad.exe', file_path], shell=True)
    except FileNotFoundError:
        print("Notepad not found. Please make sure it's installed on your system.")

def serialdata():
    while True:
        try:
            global rawdata
            rawdata = access_serial.readline().decode('utf-8').strip()
            processedata = list(map(int, rawdata.split(',')))
            print(f'\nReceived data: {rawdata}')
            
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
            global ripeness_output
            global ripeness_value
            ripeness_output=ripeness_labels[np.argmax(predictions[0])]
            ripeness_value=np.argmax(predictions[0])
            
            update_gui(app)
            print("\nModel Predictions:")
            print("Prediction => ", ripeness_labels[np.argmax(predictions[0])])
        
        except KeyboardInterrupt:
            access_serial.close()

def update_gui(app):
    def update_frame_width(frame, data):
        return int((data-1)/999*(430-50)+50)
    def update_label_text(label, data):
        return f"{label} Data:{data}"
    for i in range(1, 9):
        frame_name = f"F{i}Frame"
        label_name = f"F{i}Label"
        frame_width = update_frame_width(getattr(app, frame_name), eval(f"F{i}data"))
        getattr(app, frame_name).configure(width=frame_width)
        getattr(app, label_name).configure(width=frame_width, text=update_label_text(f"F{i} Data", eval(f"F{i}data")))

    app.ripenessLevelVar.set(ripeness_output)
    app.ripenessValueVar.set(ripeness_value)
    app.dataVar.set(str(f"{rawdata}"))


serial_thread = threading.Thread(target=serialdata, daemon=True)
serial_thread.start()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GUI Application")
        self.geometry(f"{appWidth}x{appHeight}")
        
        #F1
        self.F1Frame = ctk.CTkFrame(self, fg_color="purple", width=2, height=20)
        self.F1Frame.grid(row=0, column=0, padx=20, pady=(20,2),sticky="w")
        self.F1Label = ctk.CTkLabel(self.F1Frame, text=f"F1 Data:")
        self.F1Label.grid(row=0, column=0,padx=5)
        #F2
        self.F2Frame = ctk.CTkFrame(self, fg_color="indigo", width=2, height=20)
        self.F2Frame.grid(row=1, column=0, padx=20, pady=2,sticky="w")
        self.F2Label = ctk.CTkLabel(self.F2Frame, text=f"F2 Data:")
        self.F2Label.grid(row=1, column=0,padx=5,columnspan=2)
        #F3
        self.F3Frame = ctk.CTkFrame(self, fg_color="blue", width=2, height=20)
        self.F3Frame.grid(row=2, column=0, padx=20, pady=2,sticky="w")
        self.F3Label = ctk.CTkLabel(self.F3Frame, text=f"F3 Data:", text_color="black")
        self.F3Label.grid(row=2, column=0,padx=5,columnspan=2)
        #F4
        self.F4Frame = ctk.CTkFrame(self, fg_color="cyan", width=2, height=20)
        self.F4Frame.grid(row=3, column=0, padx=20, pady=2,sticky="w")
        self.F4Label = ctk.CTkLabel(self.F4Frame, text=f"F4 Data:",text_color="black")
        self.F4Label.grid(row=3, column=0,padx=5,columnspan=2)
        #F5
        self.F5Frame = ctk.CTkFrame(self, fg_color="green", width=2, height=20)
        self.F5Frame.grid(row=4, column=0, padx=20, pady=2,sticky="w")
        self.F5Label = ctk.CTkLabel(self.F5Frame, text=f"F5 Data:")
        self.F5Label.grid(row=4, column=0,padx=5,columnspan=2)
        #F6
        self.F6Frame = ctk.CTkFrame(self, fg_color="yellow", width=2, height=20)
        self.F6Frame.grid(row=5, column=0, padx=20, pady=2,sticky="w")
        self.F6Label = ctk.CTkLabel(self.F6Frame, text=f"F6 Data:", text_color="gray")
        self.F6Label.grid(row=5, column=0,padx=5,columnspan=2)
        #F7
        self.F7Frame = ctk.CTkFrame(self, fg_color="orange", width=2, height=20)
        self.F7Frame.grid(row=6, column=0, padx=20, pady=2,sticky="w")
        self.F7Label = ctk.CTkLabel(self.F7Frame, text=f"F7 Data:", text_color="gray")
        self.F7Label.grid(row=6, column=0,padx=5,columnspan=2)
        #F8
        self.F8Frame = ctk.CTkFrame(self, fg_color="red", width=2, height=20)
        self.F8Frame.grid(row=7, column=0, padx=20, pady=2,sticky="w")
        self.F8Label = ctk.CTkLabel(self.F8Frame, text=f"F8 Data:")
        self.F8Label.grid(row=7, column=0,padx=5,columnspan=2)
        #data
        self.dataFrame = ctk.CTkFrame(self, bg_color="green", width=460)
        self.dataFrame.grid(row=9, column=0, padx=20, pady=10,sticky="w")
        self.dataLabel = ctk.CTkLabel(self.dataFrame, text="Data received from sensor",width=360)
        self.dataLabel.grid(row=9, column=0, columnspan=2, sticky="ew")
        self.dataVar = ctk.StringVar()
        self.dataEntry = ctk.CTkEntry(self.dataFrame, textvariable=self.dataVar, width=420)
        self.dataEntry.grid(row=10, column=0, columnspan=2, padx=10)
        #accuracy
        self.dateLabel = ctk.CTkLabel(self.dataFrame, text=f"Date: {datetime.now().strftime('%d/%m')}")
        self.dateLabel.grid(row=11, column=0, pady=2, sticky="w", padx=5)  
        #prediction
        self.ripenessFrame = ctk.CTkFrame(self, bg_color="green", width=460)
        self.ripenessFrame.grid(row=10, column=0, padx=20, pady=10,sticky="w")
        self.ripenessLabel = ctk.CTkLabel(self.ripenessFrame, text="Predicted Ripeness")
        self.ripenessLabel.grid(row=10, column=1,padx=(0,20), columnspan=2,pady=(10,2.5), sticky="w")
        #level
        self.ripenessLevelVar = ctk.StringVar()
        self.ripenessLevelEntry = ctk.CTkEntry(self.ripenessFrame, textvariable=self.ripenessLevelVar, width=290)
        self.ripenessLevelEntry.grid(row=10, column=0, pady=(10,2.5), sticky="w", padx=10)
        self.levelLabel = ctk.CTkLabel(self.ripenessFrame, text="Ripness Level")
        self.levelLabel.grid(row=12, column=1, padx=(0,20), pady=(2.5,10), sticky="w")
        self.ripenessValueVar = ctk.StringVar()
        self.ripenessValueEntry = ctk.CTkEntry(self.ripenessFrame, textvariable=self.ripenessValueVar, width=290)
        self.ripenessValueEntry.grid(row=12, column=0, columnspan=2, sticky="w", padx=10, pady=(2.5,10))
        #buttons
        self.outputButton = ctk.CTkButton(self, text="Open Output Logs", command=lambda: open_output_logs(self), width=128)
        self.outputButton.grid(row=13, column=0, padx=20, pady=20, sticky="w")
        self.quitButton = ctk.CTkButton(self, text="Quit", command=self.destroy, width=60)
        self.quitButton.grid(row=13, column=0, padx=160, pady=20, sticky="w")
        

if __name__ == "__main__":
    app = App()
    app.mainloop()