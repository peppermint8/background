#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import requests
import sys
import json

class Weather():
    zipcode = ""
    api_key = "" 
    temp = 0.0
    weather = "unknown"
    area = "unknown"
    temp_unit = "'F" # or 'C or 'K
    temp_format = "{:.1f}"
    # to do - celcius option

    def __init__(self, zipcode, api_key):
        self.zipcode = zipcode
        self.api_key = api_key


    def update(self):
        
        if len(self.api_key) > 30:

            # v 3.0 - might cost money
            #https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}
        
            url = "https://api.openweathermap.org/data/2.5/weather?zip={z}&APPID={a}".format(z=self.zipcode, a=self.api_key)
            r = requests.get(url, timeout=10)

            weather_json = json.loads(r.text)
            self.area = weather_json.get("name", "unknown")
            #self.weather = weather_json['weather'][0]['main']
            self.weather = weather_json['weather'][0]['description']
            
            self.icon = weather_json['weather'][0]['icon']

            if self.temp_unit == "'F":
                self.temp = self.temp_format.format(self.k2f(weather_json['main']['temp']))
            elif self.temp_unit == "'C": 
                self.temp = self.temp_format.format(self.k2c(weather_json['main']['temp']))
            else:
                # Kevlin
                self.temp = self.temp_format.format(weather_json['main']['temp'])

        # icon meanings
        #https://openweathermap.org/weather-conditions
        # 01d = sun
        # 02d = sun & cloud
        # 03d = cloud
        # 04d = dk cloud
        # 09d = dk rain
        # 10d = rain + sun = light rain
        # 11d = lightning/thunderstorm
        # 13d = snow
        # 50d = hazy


        # pressure, humidity, temp_min, temp_max, wind.speed, degree
        #print(json.dumps(weather_json, indent=2))

    def k2f(self, kelvin_temp):
        """k2felvin to fahrenheit"""
        return (kelvin_temp - 273.15) * 9 / 5 + 32
    
    def k2c(self, kelvin_temp):
        """k2felvin to celcius"""
        return kelvin_temp - 273.15

    def __str__(self):

        weather_str = "{}: {}, {}{}".format(self.area, self.weather, self.temp, self.temp_unit)
        return weather_str
        


if __name__ == '__main__':

    zip_list = ["94598,us", "85016,us", "98602,us"]
    w_list = []
    for z in zip_list:
        w = Weather(z)
        w_list.append(w)

    for w in w_list:
        w.update()
        print("- {}".format(w))
              
    sys.exit(0)
