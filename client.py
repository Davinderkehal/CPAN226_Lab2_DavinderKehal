# This program was modified by Davinder Kehal / N01718686

import socket
import argparse
import struct  # IMPROVEMENT: Used for sequence numbers
import os
import time

def run_client(target_ip, target_port, input_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      # IMPROVEMENT: Create UDP socket
    sock.settimeout(1.0)                                         # IMPROVEMENT: Timeout for ACK
    server_address = (target_ip, target_port)                    # IMPROVEMENT: Target server
    seq_num = 0                                                  # IMPROVEMENT: Sequence counter

    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    # Send file data
    with open(input_file, 'rb') as f:
        while True:
            chunk = f.read(900)                                  # IMPROVEMENT: Safe UDP payload size
            if not chunk:
                break                                            # IMPROVEMENT: EOF reached

            packet = struct.pack("!I", seq_num) + chunk          # IMPROVEMENT: Add sequence header

            while True:
                sock.sendto(packet, server_address)              # IMPROVEMENT: Send packet
                try:
                    ack, _ = sock.recvfrom(4)                    # IMPROVEMENT: Wait for ACK
                    ack_num = struct.unpack("!I", ack)[0]        # IMPROVEMENT: Decode ACK
                    if ack_num == seq_num:
                        break                                    # IMPROVEMENT: Correct ACK received
                except socket.timeout:
                    continue                                     # IMPROVEMENT: Retransmit on timeout
                except ConnectionResetError:
                    continue                                     # IMPROVEMENT: Windows UDP reset workaround

            seq_num += 1                                         # IMPROVEMENT: Move to next sequence

    # Send EOF packet (header only)
    eof_packet = struct.pack("!I", seq_num)                      # IMPROVEMENT: EOF signal

    while True:
        sock.sendto(eof_packet, server_address)                  # IMPROVEMENT: Send EOF packet
        try:
            ack, _ = sock.recvfrom(4)                            # IMPROVEMENT: Wait for EOF ACK
            ack_num = struct.unpack("!I", ack)[0]                # IMPROVEMENT: Decode ACK
            if ack_num == seq_num:
                break                                            # IMPROVEMENT: EOF ACK received
        except socket.timeout:
            continue                                             # IMPROVEMENT: Retry EOF
        except ConnectionResetError:
            continue                                             # IMPROVEMENT: Windows UDP reset workaround

    print("[*] File transmission complete.")                     # IMPROVEMENT: Success message
    sock.close()                                                 # IMPROVEMENT: Close socket

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliable UDP File Sender")  # IMPROVEMENT
    parser.add_argument("--target_ip", type=str, default="127.0.0.1")         # IMPROVEMENT
    parser.add_argument("--target_port", type=int, default=12000)             # IMPROVEMENT
    parser.add_argument("--file", type=str, required=True)                    # IMPROVEMENT
    args = parser.parse_args()                                                 # IMPROVEMENT

    run_client(args.target_ip, args.target_port, args.file)                   # IMPROVEMENT