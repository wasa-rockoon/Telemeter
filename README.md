# WASA Telemeter
## Packet, Entry ID管理
Packet id, Entry name, component id, unit idなどは、![こちらのJsonファイル](./tornado/lib/wcpp/id_name_mapping.json) に保存してあります。idなどを更新する際は、Jsonファイルも更新していただけると助かります。

ESPからサーバに送る際のサンプルコードは![esp_packet_example](./esp_packet_example/)という名前のディレクトリに入っています。Loop()内では、５秒毎にダミーのパケットを作成してサーバーに送る処理が記載されており、WebSocketEvent()で、ESPがサーバから受信したデータの処理を行っています。なお、Arduino IDEでの実行を前提としたコードであるため、Platform IOなどを使用する際は書き直してください。
## Grafana
Dashboard name: **rockoon_dashboard**
## InfluxDB
Default bucket name: **rockoon**

Organization name: **wasa_rockoon**

## ESP code
Download [Arduino WebSockets Client library](https://github.com/Links2004/arduinoWebSockets) for ESP32
