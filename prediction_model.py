import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, BatchNormalization, Dropout
import serial
import csv

serial_port = 'COM35'
baud_rate = 9600

huhu = serial.Serial(serial_port, baud_rate)
ripeness_index = {
    0: 'Unripe',
    1: 'Partially Ripe',
    2: 'Ripe',
    3: 'Decaying',
    4: 'Undefined Error',
}

try:
    model = load_model(r"C:\Users\Akshatt\Desktop\V&F Rip\Serial\my_model.keras")
    print("Model loaded successfully.")
except (OSError, IOError):
    print("Model not found. Training a new one.")
    model = Sequential()
    model.add(Dense(128, activation='relu', input_dim=X_train.shape[1]))
    model.add(BatchNormalization())
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(32, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dense(5, activation='softmax'))

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)

    model.save(r"C:\Users\Akshatt\Desktop\V&F Rip\my_model.keras")
    print("Model trained and saved.")

def run():
    data = pd.read_csv(r"C:\Users\Akshatt\Desktop\V&F Rip\Serial\produce_color_database.csv")
    features = data.iloc[:, :10].values
    labels = data.iloc[:, 10].values
    
    label_encoder = LabelEncoder()
    labels = label_encoder.fit_transform(labels)
    
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    accuracy = model.evaluate(X_test, y_test)[1]
    most_recent_entry = data.iloc[-1, :10].values.reshape(1, -1)
    most_recent_entry = scaler.transform(most_recent_entry)
    prediction = model.predict(most_recent_entry)
    predicted_ripeness = label_encoder.inverse_transform([np.argmax(prediction)])
    if data.iloc[-1, 11] == 4:
        data.at[data.index[-1], 'class'] = predicted_ripeness[0]
        
    print(f'Model Accuracy: {accuracy * 100:.2f}%')
    print(f'Predicted Ripeness Level for the Most Recent Entry: {predicted_ripeness[0]}')
    
    if data.iloc[-1, 11] == 4:
        data.at[data.index[-1], 'class'] = predicted_ripeness[0]
    
    data.at[data.index[-1], 'prediction'] = predicted_ripeness[0]    
    print("\n RIPENESS LABEL: ",ripeness_index[data.at[data.index[-1], 'prediction']])
    data.to_csv(r"C:\Users\Akshatt\Desktop\V&F Rip\Serial\produce_color_database.csv", index=False)

try:
    while True:
        data = huhu.readline().decode('utf-8').strip()
        print(f'Received data: {data}')
        with open(r"C:\Users\Akshatt\Desktop\V&F Rip\Serial\produce_color_database.csv", 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([(x) for x in data.split(',')])
        run()
        
except KeyboardInterrupt:
    huhu.close()