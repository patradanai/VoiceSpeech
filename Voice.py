import paho.mqtt.client as mqtt
import time
import threading
from gtts import gTTS
from io import BytesIO
import os
import pygame
import json
from playsound import playsound
# ----------------- Variable -------------------- #
queueVoice = {}

# ----------------- Function -------------------- #


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True  # set flag
        print("connected OK Returned code=", rc)
    else:
        print("Bad connection Returned code= ", rc)
        client.connected_flag = False

    client.subscribe("/REALTIME/NEWLINE/PARSER/STATUS/#")


def on_disconnect(client, userdata, rc):
    print("Client Disconnected=", rc)
    client.connected_flag = False
    client.loop_stop()


def on_message(client, userdata, message):
    payload = json.loads(message.payload.decode("utf-8"))

    # Check in Queue
    if payload["Status"] == False:
        if payload["Machine"] in queueVoice:
            print("FOUND KEY")
        else:
            queueVoice[payload["Machine"]] = ""

    # if '/voice/nmpsc/' in message.topic:
    #     print("message received ", str(message.payload.decode("utf-8")))
    # if not message.payload.decode("utf-8") in QueueVoice:
    # QueueVoice.append(message.payload.decode("utf-8"))
    # print(QueueVoice)


def MQTT_RUN():
    client = mqtt.Client()
    client.connected_flag = False
    client.on_connect = on_connect          #
    client.on_disconnect = on_disconnect
    client.on_message = on_message          # attach function to callback

    # Connect MQTT TO SERVER
    try:
        client.connect("mtl-700-noa55.co.murata.local", port=1883)
    except Exception as err:
        print(err)

    while True:
        client.loop_start()
        while not client.connected_flag:  # wait in loop
            print(".")
            time.sleep(1)

        client.loop_stop()


def Play_Voice():
    # Iteration
    while True:
        if len(queueVoice) > 0:
            print(queueVoice)
            # Get First Dict
            data = next(iter(queueVoice))

            # Create
            CreateVoice(data)

            # Del First Dict After Speech
            del queueVoice[data]
            print(queueVoice)
        time.sleep(2)
    # tts = gTTS(
    #     'ขออนุญาติประกาศเรียก MT 7 4 0 ที่เครื่อง NMPSC 4 0 1 ค่ะ', lang='th')
    # mp3_fp = BytesIO()
    # tts.write_to_fp(mp3_fp)
    # mp3_fp.seek(0)
    # pygame.mixer.init()
    # pygame.init()
    # pygame.mixer.music.load(mp3_fp)
    # pygame.mixer.music.play()
    # while pygame.mixer.music.get_busy():
    #     time.sleep(1)


def CreateVoice(data):
    fileName = data + ".mp3"

    # Speech Machine
    if os.path.exists(fileName):
        playsound(fileName, True)
    else:
        tts = gTTS(
            'ขออนุญาติประกาศเรียก MT 7 4 0 ที่เครื่อง {} ค่ะ'.format(data), lang='th')
        tts.save(fileName)

        playsound(fileName, True)


if __name__ == "__main__":
    Mqtt = threading.Thread(target=MQTT_RUN)
    Voice = threading.Thread(target=Play_Voice)
    Mqtt.start()
    Voice.start()
