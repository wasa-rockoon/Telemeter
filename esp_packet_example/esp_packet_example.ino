#include "float16.h"
#include "packet.h"

#include <WiFi.h>
#include <WiFiMulti.h>
#include <WiFiClientSecure.h>

#include <WebSocketsClient.h>


WiFiMulti WiFiMulti;
WebSocketsClient webSocket;

void printPacket(uint8_t *payload, size_t length) {
  wcpp::Packet p = wcpp::Packet::decode(payload);
  Serial.print("Packet id: ");
  Serial.println(p.packet_id());
  Serial.print("Packet origin unit id: ");
  Serial.println(p.origin_unit_id());
  Serial.print("Packet destination unit id: ");
  Serial.println(p.dest_unit_id());
  auto e = p.begin();
  Serial.print("Entry name: ");
  Serial.print((*e).name()[0]);
  Serial.println((*e).name()[1]);
  Serial.print("Entry value: ");
  Serial.println(String((*e).getFloat32(), 4));
  Serial.printf("[WSc] get binary length: %u\n", length);
  
}

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
      printPacket(payload, length);
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

  WiFiMulti.addAP("example ssid", "pass");

  WiFi.disconnect();
  while(WiFiMulti.run() != WL_CONNECTED) {
    delay(100);
  }

  // server address, port and URL
  webSocket.begin("ipaddress", 80, "/ws");

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

    // Tracker
    uint8_t buf[255];
    memset(buf, 0, 255);

    wcpp::Packet tracker_packet = wcpp::Packet::empty(buf, 255);
    tracker_packet.telemetry('A', 0x11, 'a', 0x11, 12345); // 送信元ユニットidをTrackerのものに設定
    // Geolocation
    tracker_packet.append("La").setFloat64(35.7087377); 
    tracker_packet.append("Lo").setFloat64(139.7170736);
    tracker_packet.append("Al").setInt(1234);

    // Time
    tracker_packet.append("Ut").setInt(1234);
    tracker_packet.append("Ts").setInt(1234);

    // Power
    tracker_packet.append("Vb").setInt(1111);
    tracker_packet.append("Vp").setInt(1112);
    tracker_packet.append("Vd").setInt(1113);
    tracker_packet.append("Ip").setInt(2111);
    tracker_packet.append("Id").setInt(2112);

    // Environment
    tracker_packet.append("Pr").setInt(1013);
    tracker_packet.append("Te").setInt(29);
    tracker_packet.append("Hu").setInt(78);
    tracker_packet.append("Pa").setInt(100000);
    
    webSocket.sendBIN(buf, tracker_packet.size());
    for (int i = 0; i < tracker_packet.size(); i++) {
      Serial.print(buf[i]);
      Serial.print(", ");
    }
    Serial.println();
    Serial.println(tracker_packet.size());


    // Mission
    memset(buf, 0, 255);

    wcpp::Packet mission_packet = wcpp::Packet::empty(buf, 255);
    mission_packet.telemetry('A', 0x11, 'b', 0x11, 12345); // 送信元ユニットidをTrackerのものに設定
    // Geolocation
    mission_packet.append("La").setFloat64(35.6087377); 
    mission_packet.append("Lo").setFloat64(139.7170736);
    mission_packet.append("Al").setInt(1234);

    // Time
    mission_packet.append("Ut").setInt(1234);
    mission_packet.append("Ts").setInt(1234);

    // Power
    mission_packet.append("Vb").setInt(1111);
    mission_packet.append("Vp").setInt(1112);
    mission_packet.append("Vd").setInt(1113);
    mission_packet.append("Ip").setInt(2111);
    mission_packet.append("Id").setInt(2112);

    // Environment
    mission_packet.append("Pr").setInt(1013);
    mission_packet.append("Te").setInt(29);
    mission_packet.append("Hu").setInt(78);
    mission_packet.append("Pa").setInt(100000);

    // IMU
    mission_packet.append("Ph").setInt(90);
    mission_packet.append("Si").setInt(45);

    // Tank
    mission_packet.append("Tp").setInt(100);
    mission_packet.append("Np").setInt(290);
    mission_packet.append("Tt").setInt(20);
    
    
    webSocket.sendBIN(buf, mission_packet.size());
    for (int i = 0; i < mission_packet.size(); i++) {
      Serial.print(buf[i]);
      Serial.print(", ");
    }
    Serial.println();
    Serial.println(mission_packet.size());


    // Rocket
    memset(buf, 0, 255);

    wcpp::Packet rocket_packet = wcpp::Packet::empty(buf, 255);
    rocket_packet.telemetry('A', 0x11, 'c', 0x11, 12345); // 送信元ユニットidをRocketのものに設定
    // Geolocation
    rocket_packet.append("La").setFloat64(35.7087377); 
    rocket_packet.append("Lo").setFloat64(139.6170736);
    rocket_packet.append("Al").setInt(1234);

    // Time
    rocket_packet.append("Ut").setInt(1234);
    rocket_packet.append("Ts").setInt(1234);

    // Power
    rocket_packet.append("Vb").setInt(1111);
    rocket_packet.append("Vp").setInt(1112);
    rocket_packet.append("Vd").setInt(1113);
    rocket_packet.append("Ip").setInt(2111);
    rocket_packet.append("Id").setInt(2112);

    // Environment
    rocket_packet.append("Pr").setInt(1013);
    rocket_packet.append("Te").setInt(29);
    rocket_packet.append("Hu").setInt(78);
    rocket_packet.append("Pa").setInt(100000);
    
    webSocket.sendBIN(buf, rocket_packet.size());
    for (int i = 0; i < rocket_packet.size(); i++) {
      Serial.print(buf[i]);
      Serial.print(", ");
    }
    Serial.println();
    Serial.println(rocket_packet.size());

    // Ground Station1
    memset(buf, 0, 255);

    wcpp::Packet gs_packet1 = wcpp::Packet::empty(buf, 255);
    gs_packet1.telemetry('A', 0x11, 'd', 0x11, 12345); // 送信元ユニットGS1のものに設定
    // Geolocation
    gs_packet1.append("La").setFloat64(35.6087377); 
    gs_packet1.append("Lo").setFloat64(139.6170736);
    gs_packet1.append("Al").setInt(1234);

    // Time
    gs_packet1.append("Ut").setInt(1234);
    gs_packet1.append("Ts").setInt(1234);

    // Power
    gs_packet1.append("Vb").setInt(1111);
    gs_packet1.append("Vp").setInt(1112);
    gs_packet1.append("Vd").setInt(1113);
    gs_packet1.append("Ip").setInt(2111);
    gs_packet1.append("Id").setInt(2112);

    // Environment
    gs_packet1.append("Pr").setInt(1013);
    gs_packet1.append("Te").setInt(29);
    gs_packet1.append("Hu").setInt(78);
    gs_packet1.append("Pa").setInt(100000);
    
    webSocket.sendBIN(buf, gs_packet1.size());
    for (int i = 0; i < gs_packet1.size(); i++) {
      Serial.print(buf[i]);
      Serial.print(", ");
    }
    Serial.println();
    Serial.println(gs_packet1.size());

    // Ground Station2
    memset(buf, 0, 255);

    wcpp::Packet gs_packet2 = wcpp::Packet::empty(buf, 255);
    gs_packet2.telemetry('A', 0x11, 'e', 0x11, 12345); // 送信元ユニットGS1のものに設定
    // Geolocation
    gs_packet2.append("La").setFloat64(35.5087377); 
    gs_packet2.append("Lo").setFloat64(139.3170736);
    gs_packet2.append("Al").setInt(1234);

    // Time
    gs_packet2.append("Ut").setInt(1234);
    gs_packet2.append("Ts").setInt(1234);

    // Power
    gs_packet2.append("Vb").setInt(1111);
    gs_packet2.append("Vp").setInt(1112);
    gs_packet2.append("Vd").setInt(1113);
    gs_packet2.append("Ip").setInt(2111);
    gs_packet2.append("Id").setInt(2112);

    // Environment
    gs_packet2.append("Pr").setInt(1013);
    gs_packet2.append("Te").setInt(29);
    gs_packet2.append("Hu").setInt(78);
    gs_packet2.append("Pa").setInt(100000);
    
    webSocket.sendBIN(buf, gs_packet2.size());
    for (int i = 0; i < gs_packet2.size(); i++) {
      Serial.print(buf[i]);
      Serial.print(", ");
    }
    Serial.println();
    Serial.println(gs_packet2.size());

// Ground Station
    memset(buf, 0, 255);

    wcpp::Packet gs_packet3 = wcpp::Packet::empty(buf, 255);
    gs_packet3.telemetry('A', 0x11, 'f', 0x11, 12345); // 送信元ユニットGS1のものに設定
    // Geolocation
    gs_packet3.append("La").setFloat64(35.3087377); 
    gs_packet3.append("Lo").setFloat64(139.7170736);
    gs_packet3.append("Al").setInt(1234);

    // Time
    gs_packet3.append("Ut").setInt(1234);
    gs_packet3.append("Ts").setInt(1234);

    // Power
    gs_packet3.append("Vb").setInt(1111);
    gs_packet3.append("Vp").setInt(1112);
    gs_packet3.append("Vd").setInt(1113);
    gs_packet3.append("Ip").setInt(2111);
    gs_packet3.append("Id").setInt(2112);

    // Environment
    gs_packet3.append("Pr").setInt(1013);
    gs_packet3.append("Te").setInt(29);
    gs_packet3.append("Hu").setInt(78);
    gs_packet3.append("Pa").setInt(100000);
    
    webSocket.sendBIN(buf, gs_packet3.size());
    for (int i = 0; i < gs_packet3.size(); i++) {
      Serial.print(buf[i]);
      Serial.print(", ");
    }
    Serial.println();
    Serial.println(gs_packet3.size());
    
    lastSendTime = currentTime;

  }

  webSocket.loop();
}