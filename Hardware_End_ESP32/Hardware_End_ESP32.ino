#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "CA.h"

//---- WiFi settings
const char* ssid = "SSID";
const char* password = "Wifi pass";
//---- MQTT Broker settings
const char* mqtt_server = "xxxxxxxx.xxxx.xx.hivemq.cloud"; // replace with your broker url
const char* mqtt_username = "usr_nam";
const char* mqtt_password = "usr_pass";
const int mqtt_port = 8883;

WiFiClientSecure espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;

#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];

const char* sensor1_topic = "temp";

#define motor 17
#define ONE_WIRE_BUS 32
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  sensors.begin();
  Serial.begin(115200);
  Serial.print("\nConnecting to ");
  Serial.println(ssid);
  pinMode(motor, OUTPUT);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  randomSeed(micros());
  Serial.println("\nWiFi connected\nIP address: ");
  Serial.println(WiFi.localIP());

  while (!Serial) delay(1);

  espClient.setCACert(root_ca);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  
}

void loop() {

  if (!client.connected()) reconnect();
  client.loop();
  sensors.requestTemperatures(); 
  publishMessage(sensor1_topic, String(sensors.getTempCByIndex(0)), true);
  delay(500);
}

//=======================================================================Function=================================================================================

void reconnect() {
  // Loop until we’re reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection…");
    String clientId = "ESP8266Client-"; // Create a random client ID
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("connected");
      client.subscribe("Fan");   // subscribe the topics here
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");   // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

//=======================================
// This void is called every time we have a message from the broker

void callback(char* topic, byte* payload, unsigned int length) {
  String incommingMessage = "";
  for (int i = 0; i < length; i++) incommingMessage += (char)payload[i];
  Serial.println("Message arrived [" + String(topic) + "]" + incommingMessage);
  if (String(topic)=="Fan"){
    if (String(incommingMessage)=="ON"){
      digitalWrite(motor,1);
    }else{
      digitalWrite(motor,0);
    }
  }
  
}

//======================================= publising as string
void publishMessage(const char* topic, String payload , boolean retained) {
  if (client.publish(topic, payload.c_str(), true))
    Serial.println("Message publised [" + String(topic) + "]: " + payload);
}
