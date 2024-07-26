import websocket
from wcpp import Entry, Packet

ws = websocket.WebSocket()


def test_basic_packet():

    sample_buf = bytes()

    packets = []
    ws.connect("ws://localhost:8888")
    for i in range(0, 4):
        if i == 0:
            p = Packet.command(ord("A"), 0x11)
        elif i == 1:
            p = Packet.command(ord("B"), 0x11, 0x22, 0x33, 12345)
        elif i == 2:
            p = Packet.telemetry(ord("C"), 0x11)
        else:
            p = Packet.telemetry(ord("D"), 0x11, 0x22, 0x33, 12345)

        sp = Packet.telemetry(ord("P"), 0x55)
        sp.entries = [
            Entry("Px").set_int(0xFF00FF00),
            Entry("Py").set_float32(1.4142),
        ]

        p.entries = [
            Entry("Nu").set_null(),
            Entry("Ix").set_int(1),
            Entry("Iy").set_int(1234567890),
            Entry("Iz").set_int(-1234567890),
            Entry("Fx").set_float16(1.25),
            Entry("Fy").set_float32(4.56),
            Entry("Fz").set_float64(7.89),
            Entry("Bx").set_bytes(b"ABC"),
            Entry("By").set_string("abcdefghijk"),
            Entry("St").set_struct(
                [
                    Entry("Sx").set_int(54321),
                    Entry("Sy").set_float32(3.1415),
                ]
            ),
            Entry("Sp").set_packet(sp),
        ]

        buf = p.encode()
        sample_buf += buf
        sample_buf += bytes([0])
        p = Packet.decode(buf)
        packets.append(buf)

    return packets
