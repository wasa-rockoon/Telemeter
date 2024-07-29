#include "float16.h"
#include "packet.h"

#include <WiFi.h>
#include <WiFiMulti.h>
#include <WiFiClientSecure.h>

#include <WebSocketsClient.h>


WiFiMulti WiFiMulti;
WebSocketsClient webSocket;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {

  switch(type) {
    case WStype_DISCONNECTED:
      Serial.printf("[WSc] Disconnected!\n");
      break;
    case WStype_CONNECTED:
      Serial.printf("[WSc] Connected to url: %s\n", payload);

      // send message to server when Connected
      break;
    case WStype_TEXT:
            Serial.printf("[WSc] get text: %s\n", payload);


      // send message to server
      // webSocket.sendTXT("message here");
      break;
    case WStype_BIN:
      Serial.printf("[WSc] get binary length: %u\n", length);
      
      // send data to server
      // webSocket.sendBIN(payload, length);
      break;
    case WStype_ERROR:      
    case WStype_FRAGMENT_TEXT_START:
    case WStype_FRAGMENT_BIN_START:
    case WStype_FRAGMENT:
    case WStype_FRAGMENT_FIN:
      break;
  }

}


void setup() {
  // Serial.begin(921600);
  Serial.begin(115200);

  //Serial.setDebugOutput(true);

  Serial.println();
  Serial.println();
  Serial.println();

  for(uint8_t t = 4; t > 0; t--) {
    Serial.printf("[SETUP] BOOT WAIT %d...\n", t);
    delay(1000);
  }

  WiFiMulti.addAP("ssid", "password");

  WiFi.disconnect();
  while(WiFiMulti.run() != WL_CONNECTED) {
    delay(100);
  }

  // server address, port and URL
  webSocket.begin("ip adrress", 80, "/ws");

  // event handler
  webSocket.onEvent(webSocketEvent);
  //
  //  // use HTTP Basic Authorization this is optional remove if not needed
  //  webSocket.setAuthorization("user", "Password");

  // try ever 5000 again if connection has failed
  webSocket.setReconnectInterval(5000);

}



void loop() {
  static unsigned long lastSendTime = 0;
  unsigned long currentTime = millis();

  // Check if 5 seconds have passed
  if (currentTime - lastSendTime > 5000) {
    // Create packet

    uint8_t buf[255];
    memset(buf, 0, 255);
    wcpp::Packet p = wcpp::Packet::empty(buf, 255);
    p.telemetry('A', 0x11, 0x22, 0x33, 12345);
    p.append("La").setInt(1351234);
    p.append("Lo").setInt(351234);
    p.append("Al").setInt(1234);
    p.append("Ti").setInt(1234);
    p.append("Va").setInt(1111);
    p.append("Vb").setInt(1112);
    p.append("Vc").setInt(1113);
    p.append("Pr").setFloat32(1013.12);
    p.append("Te").setInt(29);
    p.append("Hu").setInt(78);
    p.append("Pa").setFloat32(1013.12);


    webSocket.sendBIN(buf, p.size());
    for (int i = 0; i < p.size(); i++) {
      Serial.print(buf[i]);
      Serial.print(", ");
    }
    Serial.println();
    lastSendTime = currentTime;

  }

  webSocket.loop();
}
