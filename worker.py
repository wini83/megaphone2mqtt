import signal
import sys
import time

import paho.mqtt.client as mqtt

from announce_request import AnnounceRequest
from announcer import Announcer
from ext_amp_conf import ExternalAmplifierConfig


class Worker(object):

    def __init__(self, mqtt_server_ip, mqtt_server_port,
                 mqtt_user=None,
                 mqtt_pass=None,
                 mqtt_base_topic="megaphone",
                 mp3_filename="output.mp3",
                 ext_amp_conf: ExternalAmplifierConfig = None):
        self.mqtt_server_ip = mqtt_server_ip
        self.mqtt_server_port = mqtt_server_port
        self.mqtt_user = mqtt_user
        self.mqtt_pass = mqtt_pass
        self.mqtt_base_topic = mqtt_base_topic
        self.client: mqtt.Client = mqtt.Client()
        self.mp3_filename = mp3_filename
        self.ext_amp_conf: ExternalAmplifierConfig = ext_amp_conf

        signal.signal(signal.SIGINT, self.signal_handler)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        if (self.mqtt_user is not None) and (self.mqtt_pass is not None):
            self.client.username_pw_set(self.mqtt_user, password=self.mqtt_pass)
        self.client.will_set(f"{self.mqtt_base_topic}/state", payload="offline", retain=True)
        self.announcer = Announcer()
        self.announcer.on_status_change = self.status_change

    def scan_for_chimes(self):
        pass

    # noinspection PyUnusedLocal
    def signal_handler(self, signum, frame):
        print('You pressed Ctrl+C - or killed me with -2')
        print("disconnect handler")
        self.client.publish(f"{self.mqtt_base_topic}/state", payload='offline')
        self.client.disconnect()
        sys.exit(0)

    def status_change(self, message):
        print(message)
        self.client.publish(f"{self.mqtt_base_topic}/log", payload=message)

    # noinspection PyUnusedLocal
    def on_connect(self, client, userdata, flags, rc):
        print("error = " + str(rc))
        self.client.publish(f"{self.mqtt_base_topic}/state", payload='online')
        self.client.subscribe(f"{self.mqtt_base_topic}/announce")

    # noinspection PyUnusedLocal
    def on_disconnect(self, userdata, flags, rc):
        print("disconnect on")
        self.client.publish(f"{self.mqtt_base_topic}/state", payload='offline', retain=True)

    # noinspection PyUnusedLocal
    def on_message(self, client, userdata, msg):
        my_json = msg.payload.decode('utf8')
        is_parsing_ok: bool = False
        req: AnnounceRequest = AnnounceRequest()
        req.load_from_json(my_json)
        if req.is_valid:
            try:
                self.client.publish(f"{self.mqtt_base_topic}/log", payload=req.__str__())
                self.announcer.announce(req.payload, volume=req.volume, play_chime=req.chime, lang=req.lang)
            except Exception as e:
                print(e)
                self.client.publish(f"{self.mqtt_base_topic}/log", payload='Playing failed')
        else:
            self.client.publish(f"{self.mqtt_base_topic}/log", payload='wrong announce structure')

    def run(self):
        self.client.connect(self.mqtt_server_ip, self.mqtt_server_port, 60)
        self.client.loop_start()
        while True:
            time.sleep(10)
