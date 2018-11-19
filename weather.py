#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io

import requests
import datetime

CONFIG_INI = "config.ini"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))


class Weather(object):
    """Class used to wrap action code with mqtt connection

        Please change the name refering to your application
    """

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except:
            self.config = None

        # start listening to MQTT
        self.start_blocking()

    # --> Sub callback function, one per intent
    def weather_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")

         # action code goes here...
        print("[Received] intent: {}".format(intent_message.intent.intent_name))

        #if intent_message.slots.days:
        #    day = intent_message.slots.days.first().value
        #    print(day)
            
        #_weather = GetWeather()
        #description = _weather.getTodaysWeather()

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, "Wetter")

    # More callback function goes here...
    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == 'maxwiese:weatherforecast':
            self.weather_callback(hermes, intent_message)
        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

class GetWeather(object):

    today =  datetime.datetime.now()

    def __init__(self):
        self.weather_forecast = requests.get("http://api.openweathermap.org/data/2.5/forecast?id=2878270&lang=de&APPID=25fdaf98e2bfd3173a4d7048b59b1aae").json()
        self.weather_forecast_list = self.weather_forecast.get("list")
         
    def getTodaysWeather(self):
        return_data = ""

        for main_weather in self.weather_forecast_list:
            date = self.parse_date(str(main_weather.get("dt_txt")))
            
            if self.today.strftime("%d%m%y") == date.strftime("%d%m%y"):                

                #get the Weather
                weather = main_weather.get("weather")[0]
                first_weather = weather
                weather_description = first_weather.get("description")

                #get the Temperatur 
                temp_kelsius = float(str(main_weather.get("main").get("temp")))
                temp = temp_kelsius - 273.15

                if date.strftime("%H") == "09":
                    return_data += "Heute Morgen {} bei einer Temperatur von {:.2f} °C\n".format(weather_description, temp)
                
                if date.strftime("%H") == "12":
                    pass
                
                if date.strftime("%H") == "15":
                    return_data += "Am Nachmittag {} bei einer Temperatur von {:.2f} °C\n".format(weather_description, temp)
                
                if date.strftime("%H") == "21":
                    return_data += "In der Nacht {} bei einer Temperatur von {:.2f} °C\n".format(weather_description, temp)

        return return_data

    def getTomorrowsWeather(self):
        return_data = ""
        tomorrow = datetime.datetime(int(self.today.strftime("%Y")), int(self.today.strftime("%m")), int(self.today.strftime("%d"))+1)

        for main_weather in self.weather_forecast_list:
            date = self.parse_date(str(main_weather.get("dt_txt")))

            if tomorrow.strftime("%d%m%y") == date.strftime("%d%m%y"):
                #get the Weather
                weather = main_weather.get("weather")[0]
                first_weather = weather
                weather_description = first_weather.get("description")

                #get the Temperatur 
                temp_kelsius = float(str(main_weather.get("main").get("temp")))
                temp = temp_kelsius - 273.15

                if date.strftime("%H") == "09":
                    return_data += "Morgen in der Früh {} bei einer Temperatur von {:.2f} °C\n".format(weather_description, temp)
                
                if date.strftime("%H") == "12":
                    pass
                
                if date.strftime("%H") == "15":
                    return_data += "Morgen Nachmittag {} bei einer Temperatur von {:.2f} °C\n".format(weather_description, temp)
                
                if date.strftime("%H") == "21":
                    return_data += "Morgen Nacht {} bei einer Temperatur von {:.2f} °C\n".format(weather_description, temp)

        return return_data
                

    def parse_date(self, raw_date):
        year = raw_date[0:4]
        month = raw_date[5:7]
        day = raw_date[8:10]
        hour = raw_date[11:13]
        minute = raw_date[14:16]

        date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))

        return date

    def parse_weekday(self, date):
        return ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")[date.weekday()]

if __name__ == "__main__":
    Weather()
