from datetime import datetime

from wcpp import Entry, Packet

packet_id_dict = {
    "A": "Tracker",
    "B": "Mission",
    "C": "Rocket",
    "D": "Ground Station",
}
entry_name_dict = {
    "La": "Latitude",
    "Lo": "Longitude",
    "Al": "GPS Altitude",
    "TI": "Time",
    "Va": "Volt(1)",
    "Vb": "Volt(2)",
    "Vc": "Volt(3)",
    "Vd": "Volt(4)",
    "Ve": "Volt(5)",
    "Vf": "Volt(6)",
    "Ia": "Current(1)",
    "Ib": "Current(2)",
    "Ic": "Current(3)",
    "Id": "Current(4)",
    "Ie": "Current(5)",
    "If": "Current(6)",
    "Pr": "Pressure",
    "Te": "Temperature",
    "Pa": "Pressure Altitude",
    "Si": "Sita",
    "Ph": "Phi",
    "Tp": "Tank Pressure",
}


def handle_packet(packet: Packet):
    packet_id = chr(packet.packet_id)
    if packet_id in packet_id_dict:
        measurement = packet_id_dict.get(packet_id)
    else:
        measurement = packet_id

    tags = {
        "origin": packet.origin_unit_id,
        "destination": packet.dest_unit_id,
        "component": packet.component_id,
    }

    fields = {}
    for entry in packet.entries:
        entry_name = entry.name
        if entry_name in entry_name_dict:
            name = entry_name_dict.get(entry_name)
        else:
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
