/*
 * WebSocketClient.ino
 *
 *  Created on: 24.05.2015
 *
 */

#include <WiFi.h>
#include <WiFiMulti.h>
#include <WiFiClientSecure.h>

#include <WebSocketsClient.h>


WiFiMulti WiFiMulti;
WebSocketsClient webSocket;

void floatToBinary(const float& value, uint8_t* buffer) {
  memcpy(buffer, &value, sizeof(float));
}

void hexdump(const void *mem, uint32_t len, uint8_t cols = 16) {
	const uint8_t* src = (const uint8_t*) mem;
	Serial.printf("\n[HEXDUMP] Address: 0x%08X len: 0x%X (%d)", (ptrdiff_t)src, len, len);
	for(uint32_t i = 0; i < len; i++) {
		if(i % cols == 0) {
			Serial.printf("\n[0x%08X] 0x%08X: ", (ptrdiff_t)src, i);
		}
		Serial.printf("%02X ", *src);
		src++;
	}
	Serial.printf("\n");
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
			Serial.printf("[WSc] get binary length: %u\n", length);
			hexdump(payload, length);

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

	WiFiMulti.addAP("ssid", "pass");

	WiFi.disconnect();
	while(WiFiMulti.run() != WL_CONNECTED) {
		delay(100);
	}

	// server address, port and URL
	webSocket.begin("54.248.18.111", 80, "/ws");

	// event handler
	webSocket.onEvent(webSocketEvent);
//
//	// use HTTP Basic Authorization this is optional remove if not needed
//	webSocket.setAuthorization("user", "Password");

	// try ever 5000 again if connection has failed
	webSocket.setReconnectInterval(5000);

}

void loop() {
    static unsigned long lastSendTime = 0;
    unsigned long currentTime = millis();
    
    // Check if 5 seconds have passed
    if (currentTime - lastSendTime > 5000) {
      float myFloat = 23.1;
      uint8_t binaryRepresentation[sizeof(float)];

      floatToBinary(myFloat, binaryRepresentation);
      Serial.println(sizeof(binaryRepresentation));
      
        webSocket.sendBIN(binaryRepresentation, sizeof(binaryRepresentation));
        lastSendTime = currentTime;
    }

    webSocket.loop();
}
