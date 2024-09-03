# WASA Telemeter
## Packet, Entry ID管理
Packet id, Entry name, component id, unit idなどは、![こちらのJsonファイル](./tornado/lib/wcpp/id_name_mapping.json) に保存してあります。idなどを更新する際は、Jsonファイルも更新していただけると助かります。
## ESP code
Download [Arduino WebSockets Client library](https://github.com/Links2004/arduinoWebSockets) for ESP32

ESPでサーバと送受信をするプログラムを作成するにあたっては、上のライブラリをインストールしてください。

ESPからサーバに送る際のサンプルコードは![esp_packet_example](./esp_packet_example/)という名前のディレクトリに入っています。Loop()内では、５秒毎にダミーのパケットを作成してサーバーに送る処理が記載されており、WebSocketEvent()ではESPがサーバから受信したデータの処理を行っています。こちらはArduino IDEでの実行を前提としたコードであるため、Platform IOなどを使用する際は書き直してください。

### 初期設定
ESPと接続するWifiのssidとパスワードに変更してください。
```c++
WiFiMulti.addAP("ssid", "pass");
```

"ipaddress"を、サーバのIPアドレスに変更してください。IPアドレスは私に聞いてもらえれば個人的に連絡します。
```c++
webSocket.begin("ipaddress", 80, "/ws");
```

### データ送信（ESP -> サーバー)
`uint_8[]`型の配列にWCPP形式でデータを保存します。`p.telemetry()`でテレメトリ用のパケットを作成します。引数は次の通り`p.telemetry(packet_id, component_id, origin_unit_id, dest_unit_id)`

`p.append()`でエントリを追加します。

```c++
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
```

サーバにデータを送る際は、`uint8_t[]`型の配列にWCPP形式でデータを保存し、第一引数に代入します。第二引数には、パケットのサイズを代入します。
```c++
webSocket.sendBIN(buf, p.size());
```

### データ受信 (ESP <- サーバー)
受信したデータは`webSocketEvent()`に渡されます。(データを受信するたびに`webSocketEvent()`が発火)
```c++
webSocket.onEvent(webSocketEvent);
```

WCPPはバイナリデータとして送信されるため、`case WStype_BIN`で処理されます。サンプルコードでは、パケットをSerialPrintする`printPacket()`という関数を作成しました。

```c++
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
```

## Grafana
Dashboard name: **rockoon_dashboard**
## InfluxDB
Default bucket name: **rockoon**

Organization name: **wasa_rockoon**

## ESP code
Download [Arduino WebSockets Client library](https://github.com/Links2004/arduinoWebSockets) for ESP32
