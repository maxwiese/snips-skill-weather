#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io

import requests

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
        except :
            self.config = None

        # start listening to MQTT
        self.start_blocking()
        
    # --> Sub callback function, one per intent
    def weather_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")

        current_weather = ""
        if intent_message.slots.days:
            day = intent_message.slots.days.first().value
            if day.encode("utf-8") == "heute":
                current_weather = str(requests.get("http://api.openweathermap.org/data/2.5/weather?id=2878270&lang=de_de&appid=acfdf5a3bb856dd2096e0ab80e8cc442").json().get("weather")[0].get("description"))

        current_weather = str(requests.get("http://api.openweathermap.org/data/2.5/weather?id=2878270&lang=de_de&appid=acfdf5a3bb856dd2096e0ab80e8cc442").json().get("weather")[0].get("description")) 
                

        
        # action code goes here...
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, current_weather, "snips-skill-weather")


    # More callback function goes here...

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == 'maxwiese:weather':
            self.wether_callback(hermes, intent_message)
        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    Weather()
