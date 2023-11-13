# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 21:14:55 2023

Group Members: (Section 01 & Section 03)
    1. Jungyu Lee (Section 01 group 5)
    2. Minyoung Seol (Section 01 group 5)
    3. Sunehildeep Singh (Section 03 group 2)
    4. Garv Chhokra (Section 03 group 2)
"""
import base64
import json
import time
import tkinter as tk
from random import randint
import paho.mqtt.client as mqtt
from threading import Thread
from group_5_group2_data_generator import create_data, TemperatureSensor

# The PublisherGUI class represents the graphical user interface for publishing data to an MQTT broker
class PublisherGUI:
    def __init__(self, root):
        # initializing the GUI
        self.root = root
        self.root.title("PublisherGUI")
        self.is_publishing = False

        # creating GUI elements for user input
        self.min_label = tk.Label(root, text="Min Temperature:")
        self.min_label.pack()
        self.min_value = tk.StringVar()
        self.min_entry = tk.Entry(root, textvariable=self.min_value)
        self.min_entry.pack()

        self.max_label = tk.Label(root, text="Max Temperature:")
        self.max_label.pack()
        self.max_value = tk.StringVar()
        self.max_entry = tk.Entry(root, textvariable=self.max_value)
        self.max_entry.pack()

        self.start_button = tk.Button(root, text="Start Publishing", command=self.start_publishing)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Publishing", command=self.stop_publishing, state=tk.DISABLED)
        self.stop_button.pack()

        self.status_label = tk.Label(root, text="Not Publishing")
        self.status_label.pack()

        self.data_text = tk.Text(root, height=20, width=50)
        self.data_text.pack()

        self.scrollbar = tk.Scrollbar(root, command=self.data_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.data_text.configure(yscrollcommand=self.scrollbar.set)

    # method to display data on the GUI
    def display_data(self, data_str):
        self.data_text.insert(tk.END, data_str + '\n')
        self.data_text.see(tk.END)

    # method to start the data publishing process
    def start_publishing(self):
        self.is_publishing = True
        self.start_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.NORMAL
        self.status_label['text'] = "Publishing..."
        try:
            x_min = float(self.min_value.get())
            x_max = float(self.max_value.get())
            self.sensor = TemperatureSensor(x_min, x_max)
            self.publish_interval = 3  # Set the interval to 3 seconds by default
        except ValueError:
            self.status_label['text'] = "Error: Invalid input. Please enter numeric values."
            self.stop_publishing()
            return
        Thread(target=self.publish_data_loop).start()

    # method to stop the data publishing process
    def stop_publishing(self):
        self.is_publishing = False
        self.start_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.DISABLED
        self.status_label['text'] = "Not Publishing"

    # method for the data publishing loop
    def publish_data_loop(self):
        client = mqtt.Client() # creating an MQTT client
        client.connect("broker.hivemq.com", 1883, 60) # connecting to the MQTT broker

        while self.is_publishing:
            self.publish_data(client) # publish data using the MQTT client
            time.sleep(self.publish_interval) # wait for the specified interval

        client.disconnect() # disconnect from the MQTT broker when publishing stops

    # method to publish data using the MQTT client
    def publish_data(self, client):
        data = create_data(self.sensor) # get data from the TemperatureSensor

        # occasionally skip transmission
        if randint(1, 100) == 50:
            self.display_data("Data transmission skipped")
            return

        # occasionally transmit wild data
        if randint(1, 100) == 20:
            data['Temperature'] = data['Temperature'] * 10

        # add a time stamp in Unix format to the data
        data['timestamp'] = time.time() 
        
        # generate a packet_id as bytes and convert it to a base64 string
        packet_id = randint(1, 1000)
        packet_id_bytes = packet_id.to_bytes((packet_id.bit_length() + 7) // 8, 'big')
        data['packet_id'] = base64.b64encode(packet_id_bytes).decode()  # base64 string

        data_str = '\n '.join([f'{key}: {value}' for key, value in data.items()]) # format data as a string
        self.display_data(data_str) # display the data on the GUI

        # publishing the data to the "temperature/data" topic on the MQTT broker
        client.publish("temperature/data", json.dumps(data))

if __name__ == '__main__':
    root = tk.Tk() # create the root Tkinter window
    app = PublisherGUI(root) # create an instance of the PublisherGUI class
    root.mainloop() # start the main event loop of the GUI application

