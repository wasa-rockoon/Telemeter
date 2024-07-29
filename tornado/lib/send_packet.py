import json

from wcpp import Entry, Packet

from .wcpp.handle_name import handle_name


def send_packet(data: json):
    data = json.loads(data)
    for key, value in data.items():
        packet_id = ord(handle_name("Grafana", "packet"))
        component_id = ord(handle_name("Environment", "component"))
        dest_unit_id = ord(handle_name("Tracker", "unit"))
        origin_unit_id = ord(handle_name("Ground station", "unit"))
        entry_name = handle_name(key, "entry")
        if entry_name == key:
            raise ValueError("Invalid entry name")
        packet = Packet().telemetry(
            packet_id=packet_id,
            component_id=component_id,
            origin_unit_id=origin_unit_id,
            dest_unit_id=dest_unit_id,
        )
        packet.entries = [Entry("Sp").set_float32(float(value))]
        buf = packet.encode()
        return buf
