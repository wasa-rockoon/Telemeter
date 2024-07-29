from datetime import datetime

from wcpp import Entry, Packet


def handle_packet(packet: Packet):
    measurement = chr(packet.packet_id)

    tags = {
        "origin": packet.origin_unit_id,
        "destination": packet.dest_unit_id,
        "component": packet.component_id,
    }

    fields = {}
    for entry in packet.entries:
        name = entry.name
        data = handle_entry(entry)
        if data:
            fields[name] = data

    record = {
        "measurement": measurement,
        "tags": tags,
        "fields": fields,
    }
    print(record)
    return record


def handle_entry(entry: Entry):
    if entry.is_null():
        data = "null"
    elif entry.is_int():
        data = entry.int()
    elif entry.is_float16():
        data = entry.float()
    elif entry.is_float32():
        data = entry.float()
    elif entry.is_float64():
        data = entry.float()
    elif entry.is_bytes():
        data = repr(entry.string())
    # elif entry.is_packet():
    #     data = entry.packet()
    # elif entry.is_struct():
    #     data = entry.struct()
    else:
        data = None
    return data

    # TODO: Add case for packets in entries
