# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 21:14:55 2023

Group Members: (Section 01 & Section 03)
    1. Jungyu Lee (Section 01 group 5)
    2. Minyoung Seol (Section 01 group 5)
    3. Sunehildeep Singh (Section 03 group 2)
    4. Garv Chhokra (Section 03 group 2)
"""

import pandas as pd
import random

# list of average temperatures
temperatures = [
    22.2, 19.35, 19.1, 19.7, 21.35, 23.15, 23.05, 21.85, 20.39, 21.45, 21.85, 19.55, 19.25,
    18.45, 18.1, 16.2, 15.9, 15.3, 15.3, 19.1, 19.39, 16.35, 16.2, 16.6, 18.55, 19.2, 16, 18.64,
    26.2, 24.54
]

# creating a DataFrame from the list of temperatures
df = pd.DataFrame(temperatures, columns=['Average Temperature'])
# Property to get the random temperature value between x_min and x_max

# TemperatureSensor class for generating random temperature values between x_min and x_max
class TemperatureSensor:
    def __init__(self, x_min, x_max):
        self.x_min = x_min # minimum temperature value
        self.x_max = x_max # maximum temperature value

    # generates a random normalized value between 0 and 1 
    def _generate_normalized_value(self):
        return random.random()

    # property to get the random temperature value between x_min and x_max
    @property
    def temperature(self):
        normalized_value = self._generate_normalized_value()
        m = self.x_max - self.x_min
        temperature = m * normalized_value + self.x_min
        return temperature

# finding the minimum and maximum temperature values from the DataFrame
x_min = df['Average Temperature'].min()
x_max = df['Average Temperature'].max()

# creating an instance of the TemperatureSensor class with the temperature range from the DataFrame
sensor = TemperatureSensor(x_min, x_max)

# function to create data using the TemperatureSensor and return a dictionary
def create_data(sensor):
    temperature_value = sensor.temperature
    data = {'Temperature': temperature_value}
    return data

# function to format and print the data dictionary
def print_data(data_dict):
    formatted_data = "\nData Received:\n" + "-" * 40 + "\n"
    for key, value in data_dict.items():
        formatted_data += f"{key}: {str(value).rjust(30)}\n"
    formatted_data += "-" * 40 + "\n"
    return formatted_data

