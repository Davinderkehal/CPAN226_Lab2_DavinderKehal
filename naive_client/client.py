
# This program was modified by Davinder Kehal / N01718686

import socket

import argparse
import time
import os
import struct  # IMPROVEMENT: Handle sequence numbers

def run_client(target_ip, target_port, input_file):
    # 1. Create a UDP socket
    seq_num = 0  # IMPROVEMENT: Track packet order
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (target_ip, target_port)
    sock.settimeout(1.0)  # IMPROVEMENT: Timeout for ACK waiting

    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    if not os.path.exists(input_file):
        print(f"[!] Error: File '{input_file}' not found.")
        return

    try:
        with open(input_file, 'rb') as f:
            while True:
                # Read a chunk of the file
                chunk = f.read(4096) # 4KB chunks
                
                if not chunk:
                    # End of file reached
                    break

                packet = struct.pack("!I", seq_num) + chunk   # IMPROVEMENT: Add sequence header

            while True:
                sock.sendto(packet, server_address)       # IMPROVEMENT: Send packet
                try:
                    ack, _ = sock.recvfrom(4)             # IMPROVEMENT: Wait for ACK
                    ack_num = struct.unpack("!I", ack)[0] # IMPROVEMENT: Decode ACK
                    if ack_num == seq_num:
                        break                              # IMPROVEMENT: ACK confirmed
                except socket.timeout:
                    pass                                  # IMPROVEMENT: Retransmit on timeout

            seq_num += 1                                  # IMPROVEMENT: Next packet

        # Send empty packet to signal "End of File"
        sock.sendto(struct.pack("!I", seq_num), server_address)  # IMPROVEMENT: EOF with sequence
        print("[*] File transmission complete.")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive UDP File Sender")
    parser.add_argument("--target_ip", type=str, default="127.0.0.1", help="Destination IP (Relay or Server)")
    parser.add_argument("--target_port", type=int, default=12000, help="Destination Port")
    parser.add_argument("--file", type=str, required=True, help="Path to file to send")
    args = parser.parse_args()

    run_client(args.target_ip, args.target_port, args.file)