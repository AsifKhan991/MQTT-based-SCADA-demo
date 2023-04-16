from tkinter import *
import math, time
import threading

import paho.mqtt.client as paho
from paho import mqtt

auto=False
Fan=False
Thresh=30

broker_address = "725ac3fd70324e28bda1d0df128fdb5b.s1.eu.hivemq.cloud"
username = "SCADA"
password = "esp_test"

def on_connect(client, userdata, flags, rc,properties=None):
    print("Connected with result code "+str(rc))
    client.subscribe("temp")

def on_message(client, userdata, message):
    val=round(float(message.payload.decode("utf-8")),1)
    temp_gauge.set_val(val)
    if auto:
        if val>Thresh:
            fan_control(True)
        else:
            fan_control(False)

client = paho.Client(client_id="SCADA", userdata=None, protocol=paho.MQTTv5)
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address,8883)


class Gauge(Canvas):
    def __init__(self, master, unit, *args, **kwargs):
        Canvas.__init__(self, master, *args, **kwargs)

        # Define the size of the gauge
        self.width = 400
        self.height = 400
        self.size = (self.width, self.height)
        
        self.min_val = 0
        self.max_val = 100
        
        self.create_oval(10, 10, self.width - 10, self.height - 10, fill='ghost white', width=6)
        self.create_oval(self.width / 2-10, self.height / 2-10, self.width / 2+10, self.height / 2+10, fill='red', width=2)
        
        d1=60
        self.create_arc(d1, d1, self.width - d1, self.height - d1, start=-45, extent=270, style='arc', fill='black')
        d2=20
        self.create_arc(d2, d2, self.width - d2, self.height - d2, start=-45, extent=270, style='arc', fill='black')
        
        # Create the gauge labels
        self.labels = []
        for i in range(0, 11):
            value = self.min_val + (self.max_val - self.min_val) / 10 * i
            angle = math.radians(135 + i * 27)
            x = self.width / 2 + math.cos(angle) * 160
            y = self.height / 2 + math.sin(angle) * 160
            label = self.create_text(x, y, text=int(value), font=('Arial', 16), anchor="center")
            self.labels.append((value, label))
        
        # Create the gauge needle
        self.needle = self.create_line(self.width / 2, self.height / 2, self.width / 2, self.height / 2 - 140, width=5, fill='red')
        self.create_text(self.width / 2, self.height - 120, text=unit, font=('Arial', 30), anchor="center")
    def set_val(self, val):
        # Set the angle of the needle based on the current val value
        angle = 135+(val - self.min_val) / (self.max_val - self.min_val) * 270
        x1 = self.width / 2
        y1 = self.height / 2
        x2 = self.width / 2 + math.cos(math.radians(angle)) * 145
        y2 = self.height / 2 + math.sin(math.radians(angle)) * 145
        self.coords(self.needle, x1, y1, x2, y2)
        clr="#18ed1b"
        if val>Thresh:
            clr="red"
        self.create_rectangle(-50+self.width / 2, self.height - 85, 50+self.width / 2, self.height - 35, fill=clr, outline="black", width=2)
        self.create_text(self.width / 2, self.height - 60, text=val, font=('Arial', 30), anchor="center")

def main_loop():
    client.loop_forever()
    
def Auto():
    global auto
    if  auto:
        Auto_button.config(text="Manual",bg="gray")
        auto=False
    else:
        Auto_button.config(text="Auto",bg="green")
        auto=True
    return

def fan_control(val):
    global Fan
    if not val:
        client.publish("Fan",'OFF')
        Fan_button.config(text="Fan OFF",bg="red")
        Fan=False
    else:
        client.publish("Fan",'ON')
        Fan_button.config(text="Fan ON",bg="green")
        Fan=True
    return True
        
root = Tk()
root.title("MQTT based SCADA")
temp_gauge = Gauge(root, "°C",width=700, height=500)
temp_gauge.pack()
temp_gauge.set_val(0)
Fan_button = Button(root, text="FAN OFF",width=10, bg="red", height=2,font=('Arial', 30), anchor="center",command= lambda : fan_control(not Fan) if not auto else False)
Fan_button.place(x=420,y=50)
Auto_button = Button(root, text="Manual",width=10, bg="gray", height=2,font=('Arial', 20), anchor="center",command = Auto)
Auto_button.place(x=450,y=300)


        
t = threading.Thread(target=main_loop)
if __name__ == "__main__":
    t.start()
    root.mainloop()
    
    




