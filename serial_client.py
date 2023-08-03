#!/usr/bin/env python3

import argparse
import datetime
import struct
import time

import serial
import websocket
from cobs import cobs
from wccp.packet import Packet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', help='Serial port')
    parser.add_argument('-i', '--id', help='System id')
    parser.add_argument('-b', '--baud', help='Baudrate', type=int,
                        default=115200)
    parser.add_argument('-s', '--server', help='Server address',
                        default='ws://localhost:8888')
    parser.add_argument('-n', '--noprint', help='Stop printing data',
                        action='store_true')

    args = parser.parse_args();
    print(args)

    source = 'serial'

    ws = None

    if args.id:
        # websocket.enableTrace(True)

        start_time = datetime.datetime.now().isoformat()

        ws = websocket.WebSocket()
        ws.connect(
            f'{args.server}/api/systems/{args.id}/packets'\
            f'?source={source}&startTime={start_time}')

    with serial.Serial(args.port, args.baud) as ser:
        print('connected port:', args.port, ', baud =', args.baud)

        buf = b''

        while True:
            try:
                buf += ser.read_all() or b''
            except:
                print('disconnected')
                break;

            if not buf:
                continue

            splitted = buf.split(b'\x00', 1)
            if len(splitted) <= 1:
                continue
            buf = splitted[1]

            decoded = cobs.decode(splitted[0])

            if decoded[0] == 0:
                continue

            # print(decoded)

            packet = Packet.decode(decoded)

            if not packet:
                print('decode error')
                continue

            if ws:
                unix_time = int(time.time() * 1000)
                time_bin = struct.pack('<Q', unix_time)
                ws.send(time_bin + decoded, websocket.ABNF.OPCODE_BINARY)

            if not args.noprint:
                packet.print()

    if ws:
        ws.close()

if __name__ == "__main__":
    main()
