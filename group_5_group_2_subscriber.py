# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 20:27:49 2023

Group Members: (Section 01 & Section 03)
    1. Jungyu Lee (Section 01 group 5)
    2. Minyoung Seol (Section 01 group 5)
    3. Sunehildeep Singh (Section 03 group 2)
    4. Garv Chhokra (Section 03 group 2)
"""

import sys
import base64
import json
import paho.mqtt.client as mqtt
import datetime
import threading
import time
import numpy as np
import tkinter as tk
from group_5_group2_data_generator import print_data
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# global variable to keep track of the last received time
last_received_time = time.time()

# custom Text widget that behaves like stdout
class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    # method to redirect stdout to the text widget
    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # scroll to the end to show the latest message

    def flush(self):
        pass

# the callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("temperature/data")

received_temperatures = []  # global list to keep track of received temperatures
time_list = []  # global list to keep track of timestamps

# the callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global last_received_time
    global received_temperatures
    global time_list

    last_received_time = time.time()  # update the time of the last received message

    # decode the message
    data = json.loads(msg.payload.decode())

    # check if data is missing
    if data.get('Temperature') is None:
        print_data({"Status": "Data transmission was skipped"})
        # format the "Data transmission skipped" message
        formatted_data = print_data({"Status": "Data transmission was skipped"})
        # display the message in the GUI text box
        sys.stdout.write(formatted_data)
        return

    # append the current temperature to the list of received temperatures
    received_temperatures.append(data['Temperature'])

    # convert timestamp from Unix format to hour:minute:second
    formatted_timestamp = datetime.datetime.fromtimestamp(data['timestamp']).strftime('%H:%M:%S')
    data['timestamp'] = formatted_timestamp  # update the timestamp to the formatted version
    time_list.append(formatted_timestamp)  # store the formatted timestamp

    # ensure the lists only retain the last 10 elements
    received_temperatures = received_temperatures[-10:]
    time_list = time_list[-10:]

    # calculate the first and third quartiles
    q1 = np.percentile(received_temperatures, 25)
    q3 = np.percentile(received_temperatures, 75)

    # calculate the IQR
    iqr = q3 - q1

    # define bounds for outliers
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    was_wild = False

    # detect and handle wild data
    if data['Temperature'] < lower_bound or data['Temperature'] > upper_bound:
        print("Wild data detected and corrected!")  # diagnostic print
        data['Temperature'] = data['Temperature'] / 10
        was_wild = True

        # update the last element of received_temperatures with the corrected value (divided by 10)
        received_temperatures[-1] = data['Temperature']

    # limit the temperature to two decimal places
    data['Temperature'] = round(data['Temperature'], 2)

    # decode packet_id from base64 back to integer
    packet_id_bytes = base64.b64decode(data['packet_id'])
    data['packet_id'] = int.from_bytes(packet_id_bytes, 'big')

    # if data was 'wild'
    if was_wild:
        data['Status'] = "Received and corrected 'wild' data"
    else:
        data['Status'] = "Received data"

    # format the received data as a string using the print_data function
    formatted_data = print_data(data)

    # display the received data in the GUI text box
    sys.stdout.write(formatted_data)

    # update the chart in the GUI
    update_chart()


# background thread function to check if data hasn't been received in a while
def check_last_received():
    global last_received_time
    while True:
        time_since_last_received = time.time() - last_received_time
        if time_since_last_received > 4:  # 3 seconds + 1 second buffer
            data = {"Status": "Data transmission was likely skipped or connection lost"}
            # format the "Data transmission skipped" message
            formatted_data = print_data(data)
            # display the message in the GUI text box
            sys.stdout.write(formatted_data)
            last_received_time = time.time()  # reset the last received time to prevent repeated messages
        time.sleep(1)  # check every second

# start the background thread
threading.Thread(target=check_last_received, daemon=True).start()

# create the main Tkinter window
root = tk.Tk()
root.title("MQTT Data Receiver")

# create a text box widget
text_box = tk.Text(root, wrap=tk.WORD)
text_box.pack(fill=tk.BOTH, expand=True)

# redirect stdout to the Tkinter text box
sys.stdout = StdoutRedirector(text_box)

# create the figure and axis for the chart
fig, ax = plt.subplots(figsize=(8, 4))
ax.set_title("Temperature over Time")
ax.set_xlabel("Time")
ax.set_ylabel("Temperature (°C)")

# function to update the chart
def update_chart():
    ax.clear()
    ax.plot(time_list[-6:], received_temperatures[-6:], label='Temperature', color='blue', marker='o')
    ax.bar(time_list[-6:], received_temperatures[-6:], label='Temperature', color='lightblue', alpha=0.5)
    ax.legend()
    ax.set_title("Temperature over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature (°C)")
    fig.autofmt_xdate()
    fig.tight_layout()

    # update the chart in the GUI
    canvas.draw()

# create a canvas to display the chart in the GUI
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 1883, 60)

# start the MQTT client loop in a separate thread
mqtt_thread = threading.Thread(target=client.loop_forever, daemon=True)
mqtt_thread.start()

# handle the closing of the Tkinter window
def on_close():
    client.loop_stop()  # Stop the MQTT client loop
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# start the Tkinter main loop
root.mainloop()
